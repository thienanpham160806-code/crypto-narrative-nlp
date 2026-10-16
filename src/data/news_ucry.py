"""UCRY Policy/Price (Lucey, Vigne, Yarovaya & Wang 2022) – chỉ số bất định crypto từ tin LexisNexis, theo tuần.

Nguồn: https://sites.google.com/view/cryptocurrency-indices/the-indices/crypto-uncertainty (file Google Drive,
tuần thứ Hai–Chủ nhật, có đến 2024 Q4). Lưu thô ở data/raw/ucry/ucry_weekly.csv.
Point-in-time (DATA_CONTRACT §6): giá trị tuần kết thúc Chủ nhật w chỉ dùng từ ngày w+1. Ngày t lấy tuần gần nhất
có w+1 ≤ t, tối đa STALE ngày; quá hạn (sau tuần cuối) → NaN, không kéo dài.
Chuỗi là bản tính lại hồi cứu, không có vintage theo thời gian thực → ghi trong phần hạn chế của paper.
Chạy: python -m data.news_ucry
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd, requests
from utils.common import CFG, D

URL = "https://drive.google.com/uc?export=download&id=1AmPZUOvs0YWWxRSXSc9R8y8XcjhPf2C9"
STALE = 7


def download() -> pathlib.Path:
    f = D("raw", "ucry", "ucry_weekly.csv")
    if not f.exists():
        f.write_bytes(requests.get(URL, timeout=60).content)
    return f


def daily(raw: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    raw = raw.dropna(subset=["Timeline"])
    w = pd.DataFrame(dict(
        week_end=pd.to_datetime(raw.Timeline.str.split("-").str[1].str.strip(), format="%d/%m/%Y").dt.tz_localize("UTC"),
        ucry_policy=raw["UCRY Policy Index"].astype(float), ucry_price=raw["UCRY Price Index"].astype(float)))
    w["available"] = w.week_end + pd.Timedelta(days=1)
    dates = pd.DataFrame(dict(date=pd.date_range(start, end, freq="D", tz="UTC")))
    out = pd.merge_asof(dates, w.sort_values("available"), left_on="date", right_on="available",
                        direction="backward", tolerance=pd.Timedelta(days=STALE))
    return out[["date", "ucry_policy", "ucry_price", "week_end"]]


def main():
    raw = pd.read_csv(download(), encoding="utf-8-sig")
    out = daily(raw, CFG["sample"]["start"], CFG["sample"]["end"])
    out.to_parquet(D("processed", "ucry_daily.parquet"), index=False)
    print(out.dropna().agg(["count", "min", "max"]).to_string())


if __name__ == "__main__":
    main()
