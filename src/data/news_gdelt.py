"""GDELT GKG 2.0 (file 15 phút, tĩnh) → tiêu đề + URL + giờ GDELT thấy bài (docs/SOURCES.md: nguồn chính).

Vì sao GKG thay DOC API: DOC API 429 gần như liên tục (≈1 lệnh/4 phút từ IP này, 2026-10-16) và cắt 250 bài/lệnh;
file GKG không giới hạn, đủ mọi bài trong lô. Lọc bằng regex trên <PAGE_TITLE>.
  • en: file .gkg.csv.zip (nguồn tiếng Anh); vi: file .translation.gkg.csv.zip, chỉ dòng srclc:vie.
  • first_seen_utc = DATE của lô 15 phút (= seendate của DOC API).
shortcut: chỉ tải lô phút `--minutes` mỗi giờ (mặc định :00 ≈ 25% bài, mẫu đều theo thời gian) vì 96 file/ngày ≈ 600 MB;
thêm 15/30/45 khi cần đủ. Cache: data/raw/gkg/<lang>/<YYYYMMDD>_<mm>.jsonl, ghi khi đủ 24 lô của ngày.
Chạy: python -m data.news_gdelt --lang en ; audit giờ đăng: python -m data.news_gdelt --audit 300
"""
from __future__ import annotations
import argparse, html, io, json, re, sys, pathlib, threading, time, unicodedata, zipfile
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd, requests
from utils.common import CFG, D

BASE = "https://data.gdeltproject.org/gdeltv2/"
FEED = {"en": ".gkg.csv.zip", "vi": ".translation.gkg.csv.zip"}
SOURCE = {"en": "gdelt", "vi": "vn:gdelt"}
KEEP = {
    "en": re.compile(r"\b(bitcoin|btc|ethereum|eth|ether|crypto\w*|stablecoins?|solana|xrp|binance|bnb|blockchain|"
                     r"defi|altcoins?|memecoins?|tether|usdt|usdc|coinbase)\b", re.I),
    "vi": re.compile(r"bitcoin|\bbtc\b|ethereum|crypto|tiền (mã|điện tử|số|ảo|kỹ thuật số)|tài sản (số|mã hóa|ảo)|"
                     r"stablecoin|blockchain|binance|\busdt\b", re.I),
}
TITLE = re.compile(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>")
STRIDE = 16


def title_of(extras: str) -> str:
    m = TITLE.search(extras or "")
    return unicodedata.normalize("NFC", html.unescape(m.group(1))).strip() if m else ""


def parse(raw: bytes, lang: str) -> list[dict]:
    out = []
    for line in raw.decode("utf-8", "replace").split("\n"):
        c = line.split("\t")
        if len(c) < 27 or (lang == "vi" and "srclc:vie" not in c[25]):
            continue
        t = title_of(c[26])
        if KEEP[lang].search(t):
            out.append(dict(date=c[1], domain=c[3], url=c[4], title=t))
    return out


def fetch(stamp: str, lang: str, get) -> list[dict]:
    """Một lô 15 phút. get = utils.http.Client.get (retry 429/5xx, None khi 404 = lô GDELT bị thiếu)."""
    r = get(BASE + stamp + FEED[lang], timeout=120)
    if r is None:
        return []
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return parse(z.read(z.namelist()[0]), lang)


def cache_dir(lang: str) -> pathlib.Path:
    return D("raw", "gkg", lang, "x").parent


def collect(lang: str, start, end, minutes=(0,), workers: int = 8, get=None) -> int:
    """Ngày lỗi mạng: ghi ERR vào progress.log, không ghi cache → lần chạy sau làm lại. Trả số dòng thu được."""
    from utils.http import Client
    get = get or Client(rps=workers).get
    days = pd.date_range(start, end, freq="D")
    todo = [(d, m) for d in days for m in minutes if not (cache_dir(lang) / f"{d:%Y%m%d}_{m:02d}.jsonl").exists()]
    todo.sort(key=lambda dm: ((dm[0] - days[0]).days % STRIDE, dm[0]))   # rải đều mẫu: dừng giữa chừng vẫn phủ đủ kỳ
    total, lock, log = len(days) * len(minutes), threading.Lock(), cache_dir(lang).parent / "progress.log"
    done = [total - len(todo)]

    def note(msg):
        print(msg, flush=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def day(dm):
        d, m = dm
        f = cache_dir(lang) / f"{d:%Y%m%d}_{m:02d}.jsonl"
        part = f.with_suffix(".part")                      # giờ đã tải xong: mạng chập chờn không làm mất cả ngày
        got = {}
        if part.exists():
            for line in part.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                got[rec["h"]] = rec["rows"]
        try:
            for h in range(24):
                if h not in got:
                    got[h] = fetch(f"{d:%Y%m%d}{h:02d}{m:02d}00", lang, get)
                    with open(part, "a", encoding="utf-8") as p:
                        p.write(json.dumps(dict(h=h, rows=got[h]), ensure_ascii=False) + "\n")
        except Exception as e:
            with lock:
                note(f"{pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} {lang} {d:%Y-%m-%d} :{m:02d} ERR {type(e).__name__} "
                     f"({len(got)}/24 giờ đã lưu)")
            return 0
        rows = [r for h in range(24) for r in got[h]]
        f.with_suffix(".tmp").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        f.with_suffix(".tmp").replace(f)
        part.unlink(missing_ok=True)
        with lock:
            done[0] += 1
            note(f"{pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} {lang} {d:%Y-%m-%d} :{m:02d} rows={len(rows)} "
                 f"done={done[0]}/{total} ({100 * done[0] / total:.1f}%)")
        return len(rows)

    with ThreadPoolExecutor(workers) as ex:
        return sum(ex.map(day, todo))


def load(lang: str) -> pd.DataFrame:
    fs = [pd.read_json(f, lines=True, dtype=False, convert_dates=False) for f in sorted(cache_dir(lang).glob("*.jsonl")) if f.stat().st_size]
    df = pd.concat(fs) if fs else pd.DataFrame(columns=["date", "domain", "url", "title"])
    df["first_seen_utc"] = pd.to_datetime(df.date.astype(str), format="%Y%m%d%H%M%S", utc=True)
    df = df.sort_values("first_seen_utc").drop_duplicates("url").drop(columns="date")
    return df.assign(source=SOURCE[lang], lang=lang, body=None, published_at_utc=pd.NaT, ts_source="gdelt_seendate")


# ---------- audit timestamp: giờ đăng do trang công bố (meta HTML) cho một mẫu URL ----------
NO_SCRAPE = {"coindesk.com", "cointelegraph.com", "decrypt.co", "theblock.co"}   # ToS cấm robot (docs/SOURCES.md)
META_RE = [r'property="article:published_time"\s+content="([^"]+)"', r'content="([^"]+)"\s+property="article:published_time"',
           r'"datePublished"\s*:\s*"([^"]+)"', r'itemprop="datePublished"\s+content="([^"]+)"']


def meta_published(page: str) -> pd.Timestamp | None:
    """Giờ đăng có múi giờ → UTC; chuỗi không có múi giờ thì bỏ (không đoán được)."""
    for p in META_RE:
        if (m := re.search(p, page)) and not pd.isna(t := pd.to_datetime(m.group(1), errors="coerce")) \
                and t.tzinfo is not None:
            return t.tz_convert("UTC")
    return None


def robots_ok(url: str, cache: dict) -> bool:
    from urllib import robotparser
    host = urlsplit(url).netloc
    if host not in cache:
        cache[host] = rp = robotparser.RobotFileParser(f"https://{host}/robots.txt")
        try:
            rp.read()
        except Exception:
            rp.disallow_all = True
    return cache[host].can_fetch("*", url)


def audit(lang: str = "en", n: int = 300, get=None, allowed=None) -> int:
    """Mẫu ngẫu nhiên (seed) URL GDELT, đọc meta giờ đăng → data/raw/html_meta.jsonl. Trả số URL có giờ."""
    import socket
    socket.setdefaulttimeout(20)                      # robots.txt treo thì bỏ qua
    ua = {"User-Agent": f"UEL-Fintech crypto-narrative research {CFG.get('contact_email', '')}"}
    get = get or (lambda u: requests.get(u, timeout=20, headers=ua))
    robots = {}
    allowed = allowed or (lambda u: robots_ok(u, robots))
    out = D("raw", "html_meta.jsonl")
    done = {json.loads(l)["url"] for l in open(out, encoding="utf-8")} if out.exists() else set()
    df = load(lang)
    df = df[~df.domain.isin(NO_SCRAPE) & ~df.url.isin(done)].sample(frac=1, random_state=CFG["seed"])
    k = 0
    with open(out, "a", encoding="utf-8") as f:
        for url in df.url:
            if k >= n:
                break
            try:
                r = get(url) if allowed(url) else None
                t = meta_published(r.text[:300_000]) if r is not None and r.status_code == 200 else None
            except Exception:
                t = None
            f.write(json.dumps(dict(url=url, published_at_utc=t.isoformat() if t is not None else None)) + "\n")
            k += t is not None
    return k


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en", choices=FEED)
    ap.add_argument("--start", default=CFG["sample"]["start"])
    ap.add_argument("--end", default=CFG["sample"]["end"])
    ap.add_argument("--minutes", type=int, nargs="+", default=[0])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--audit", type=int, default=0, help="số URL cần có giờ đăng (0 = thu GKG)")
    a = ap.parse_args()
    if a.audit:
        print(audit(a.lang, a.audit), "urls with published time")
    else:
        from utils.awake import keep_awake_on_ac
        keep_awake_on_ac()                            # cắm sạc: máy không tự ngủ khi đang thu
        while True:                                   # chạy lại các ngày lỗi cho tới khi đủ
            collect(a.lang, a.start, a.end, a.minutes, a.workers)
            left = [d for d in pd.date_range(a.start, a.end) for m in a.minutes
                    if not (cache_dir(a.lang) / f"{d:%Y%m%d}_{m:02d}.jsonl").exists()]
            if not left:
                break
            time.sleep(120)
