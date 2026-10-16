"""Tiện ích dùng chung. Port từ disclosure-tone-car/src/common.py (đổi: config/config.yaml, bỏ nhánh thị trường)."""
import os, pathlib, re, unicodedata, yaml
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(ROOT / "config" / "config.yaml", encoding="utf-8"))
# Email/khóa KHÔNG ghi vào repo: ưu tiên biến môi trường, rồi config/config.local.yaml (nằm trong .gitignore)
_local = ROOT / "config" / "config.local.yaml"
if _local.exists():
    CFG.update(yaml.safe_load(open(_local, encoding="utf-8")) or {})
if os.getenv("CONTACT_EMAIL"):
    CFG["contact_email"] = os.environ["CONTACT_EMAIL"]


def P(*a) -> pathlib.Path:
    p = ROOT.joinpath(*a)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def D(*a) -> pathlib.Path:
    """D('processed','daily.parquet') → data/processed/daily.parquet"""
    return P("data", *a)


def O(*a) -> pathlib.Path:
    """O('tables','x.csv') → outputs/tables/x.csv"""
    return P("outputs", *a)


def K(prefix, lo, hi):
    """Tên cột hợp lệ cho công thức hồi quy: CAR[-1,+1] → car_m1_1."""
    f = lambda x: f"m{-x}" if x < 0 else str(x)
    return f"{prefix}_{f(lo)}_{f(hi)}"


def winsor(s: pd.Series, lo=.01, hi=.99) -> pd.Series:
    q = s.quantile([lo, hi])
    return s.clip(q.iloc[0], q.iloc[1])


def norm_vi(t: str) -> str:
    """Chuẩn hóa Unicode tiếng Việt (NFC), chữ thường, gộp khoảng trắng."""
    t = unicodedata.normalize("NFC", t or "").lower()
    return re.sub(r"\s+", " ", t).strip()


def to_utc(ts, tz: str = "UTC") -> pd.Series:
    """Mọi timestamp về UTC. Chuỗi không có múi giờ được hiểu theo `tz` (vd 'Asia/Ho_Chi_Minh' cho báo Việt)."""
    s = pd.to_datetime(ts, errors="coerce")
    if getattr(s.dt, "tz", None) is None:
        s = s.dt.tz_localize(tz)
    return s.dt.tz_convert("UTC")
