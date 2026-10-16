"""Server local: phục vụ dashboard đã build + /api/live (chấm trực tiếp, cache 10 phút).

Chạy: python dashboard/export.py && (cd dashboard/web && npm run build) && uvicorn dashboard.server:app --port 8000
Dev frontend: cd dashboard/web && npm run dev (proxy /api → :8000).
"""
from __future__ import annotations
import pathlib, time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dashboard import live
from data.news_rss import FEEDS

DIST = pathlib.Path(__file__).resolve().parent / "web" / "dist"
TTL = 600
app = FastAPI(title="Crypto Narrative Report")
_cache = {"t": 0.0, "data": None}


@app.get("/api/live")
def api_live():
    if _cache["data"] is None or time.time() - _cache["t"] > TTL:
        _cache.update(t=time.time(), data=live.payload(tuple(FEEDS)))
    return _cache["data"]


if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
