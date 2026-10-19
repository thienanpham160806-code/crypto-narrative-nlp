"""HTTP lịch sự cho mọi nguồn (news API, RSS, sàn): token-bucket + retry 429/5xx + User-Agent có email.

Port từ disclosure-tone-car: src/us/edgar_client.py (gốc m4a1ak471994/lm2011-replication, MIT – xem
third_party_licenses/) + src/vn/http.py. Đổi: một client dùng chung, rps truyền vào thay vì đọc cứng từ config.
"""
from __future__ import annotations
import threading, time
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from utils.common import CFG


class RateLimiter:
    """Token bucket: nạp lại `rps` token/giây, dung lượng = rps."""
    def __init__(self, rps: float):
        self.rate = self.capacity = self.tokens = rps
        self.last = time.monotonic(); self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate); self.last = now
            if self.tokens < 1.0:
                time.sleep((1.0 - self.tokens) / self.rate); self.tokens = 0.0; self.last = time.monotonic()
            else:
                self.tokens -= 1.0


class RetryableHTTPError(Exception):
    pass


class Client:
    def __init__(self, rps: float = 2.0, headers: dict | None = None):
        self.headers = {"User-Agent": f"UEL-Fintech crypto-narrative research {CFG.get('contact_email', '')}",
                        **(headers or {})}
        self.s = self._session()
        self.limiter = RateLimiter(rps)

    def _session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update(self.headers)
        return s

    @retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=30),
           retry=retry_if_exception_type((RetryableHTTPError, requests.RequestException)))
    def get(self, url: str, timeout: int = 60, **kw) -> requests.Response | None:
        self.limiter.acquire()
        try:
            r = self.s.get(url, timeout=timeout, **kw)
        except requests.RequestException:
            self.s = self._session()        # kết nối cũ trong pool hỏng (SSL/reset) → lần thử sau dùng phiên mới
            raise
        if r.status_code == 404:            # không tồn tại → không thử lại
            return None
        if r.status_code in (429, 500, 502, 503, 504):
            ra = r.headers.get("Retry-After")
            if ra and ra.isdigit():
                time.sleep(min(30, int(ra)))
            raise RetryableHTTPError(f"{r.status_code} {url}")
        r.raise_for_status()
        return r
