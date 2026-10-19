"""Tầng LLM zero-shot (tùy chọn, config.nlp.llm.enabled): Gemini (mặc định) + Claude (dự phòng), cùng một giao diện.

Port từ disclosure-tone-car/src/textkit/llm_client.py – GIỮ: cache sha256, budget, rate limit, retry, fallback
Gemini↔Claude, temperature=0, parse_json. ĐỔI: bỏ phần OCR (vision/text_fix/locate), thêm classify_narrative().
  • Mọi phản hồi được cache ở data/interim/llm_cache/<sha256(model+loại+prompt)>.json → chạy lại không tốn lượt gọi.
  • Giới hạn: max_total_calls (lượt gọi thật, không tính cache) và requests_per_minute.
  • API key: biến môi trường GEMINI_API_KEY / ANTHROPIC_API_KEY hoặc file .env (không commit).
Model đặt trong config.yaml (nlp.llm.model_gemini / model_claude). Claude: dùng model nhận temperature (Haiku 4.5).
"""
from __future__ import annotations
import collections, hashlib, json, os, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NARRATIVES = ["regulation", "etf_institutional", "security_hacks", "stablecoins", "defi", "ai_tokens",
              "macro_monetary", "price_speculation", "other"]
NARRATIVE_SCHEMA = {
    "type": "object",
    "properties": {"narrative": {"type": "string", "enum": NARRATIVES},
                   "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                   "confidence": {"type": "number"}},
    "required": ["narrative", "sentiment", "confidence"],
}
PROMPT_NARRATIVE = (
    "You label crypto news headlines for an academic study. Use only the headline text; do not use knowledge of what "
    "happened later.\n"
    "narrative: the main theme, one of: regulation (laws, regulators, lawsuits, bans), etf_institutional (ETFs, "
    "institutional or corporate adoption), security_hacks (hacks, exploits, scams, fraud), stablecoins, defi, "
    "ai_tokens (AI-related tokens/projects), macro_monetary (rates, inflation, central banks, macro), "
    "price_speculation (price moves, predictions, trading), other.\n"
    "sentiment: tone of the headline for crypto prices (positive / negative / neutral). confidence in [0,1].\n"
    'Return only JSON: {"narrative": "...", "sentiment": "...", "confidence": number}.\n\nHEADLINE: ')


class RetryableError(Exception):
    """Lỗi tạm thời (429, 5xx, mạng) – được thử lại có backoff."""


class BudgetExceeded(Exception):
    pass


class LLMError(Exception):
    pass


def parse_json(raw: str) -> dict:
    s = (raw or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", s, re.S)
        if not m:
            raise
        return json.loads(m.group())


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass


def gemini_backend():
    """Backend Gemini (SDK chính thức google-genai). Trả hàm (model, prompt, schema, max_tokens) → (text, usage)."""
    from google import genai
    from google.genai import types, errors
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def call(model, prompt, schema, max_tokens):
        cfg = types.GenerateContentConfig(
            temperature=0, max_output_tokens=max_tokens, response_mime_type="application/json",
            response_json_schema=schema, automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        try:
            r = client.models.generate_content(model=model, contents=[prompt], config=cfg)
        except errors.APIError as e:
            if e.code == 429 or (e.code or 0) >= 500:
                raise RetryableError(f"gemini {e.code}: {str(e)[:200]}") from e
            raise
        except Exception as e:          # lỗi mạng
            if "timed out" in str(e).lower() or "connection" in str(e).lower():
                raise RetryableError(str(e)[:200]) from e
            raise
        cand = r.candidates[0] if r.candidates else None
        fr = getattr(getattr(cand, "finish_reason", None), "name", None)
        if fr and fr not in ("STOP", "FINISH_REASON_UNSPECIFIED"):
            # SAFETY/MAX_TOKENS/RECITATION... → không thử lại
            raise LLMError(f"gemini finish_reason={fr}")
        u = r.usage_metadata
        return r.text, {"input_tokens": getattr(u, "prompt_token_count", None),
                        "output_tokens": getattr(u, "candidates_token_count", None)}
    return call


def claude_backend():
    """Backend Claude (SDK chính thức anthropic). Tự retry của SDK tắt – retry do LLMClient quản lý."""
    import anthropic
    client = anthropic.Anthropic(max_retries=0)

    def call(model, prompt, schema, max_tokens):
        try:
            r = client.messages.create(model=model, max_tokens=max_tokens, temperature=0,
                                       messages=[{"role": "user", "content": prompt}])
        except anthropic.RateLimitError as e:
            raise RetryableError(f"claude 429: {e}") from e
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                raise RetryableError(f"claude {e.status_code}") from e
            raise
        except anthropic.APIConnectionError as e:
            raise RetryableError(f"claude connection: {e}") from e
        if r.stop_reason == "refusal":
            raise LLMError("claude refusal")
        text = "".join(b.text for b in r.content if b.type == "text")
        return text, {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
    return call


BACKENDS = {"gemini": (gemini_backend, "GEMINI_API_KEY"), "claude": (claude_backend, "ANTHROPIC_API_KEY")}


class LLMClient:
    def __init__(self, cfg: dict, cache_dir: Path | None = None, backends: dict | None = None, sleep=time.sleep,
                 clock=time.monotonic):
        _load_env()
        self.cfg = cfg
        self.cache_dir = Path(cache_dir or ROOT / "data" / "interim" / "llm_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._injected = backends or {}
        self._built = {}
        self.sleep, self.clock = sleep, clock
        self.calls = 0                      # lượt gọi API thật
        self.cache_hits = 0
        self.fail_streak = collections.Counter()
        self.usage = collections.Counter()  # token theo provider
        self._last_call = -1e9

    # ---------- chọn provider ----------
    def available(self, provider: str) -> bool:
        if provider in self._injected:
            return True
        return provider in BACKENDS and bool(os.getenv(BACKENDS[provider][1]))

    def providers(self) -> list[str]:
        order = [self.cfg.get("provider", "gemini"), self.cfg.get("fallback_provider")]
        order = [p for p in dict.fromkeys(order) if p and self.available(p)]
        # provider lỗi liên tục ≥ max_consecutive_failures → chuyển xuống cuối (dùng provider còn lại trước)
        k = self.cfg.get("max_consecutive_failures", 3)
        return sorted(order, key=lambda p: self.fail_streak[p] >= k)

    def _backend(self, provider):
        if provider in self._injected:
            return self._injected[provider]
        if provider not in self._built:
            self._built[provider] = BACKENDS[provider][0]()
        return self._built[provider]

    # ---------- lõi: cache + budget + rate limit + retry + fallback ----------
    def _key(self, model, kind, prompt):
        h = hashlib.sha256()
        for part in (model, kind, prompt):
            h.update(part.encode("utf-8")); h.update(b"\x00")
        return h.hexdigest()

    def _pace(self):
        gap = 60.0 / max(self.cfg.get("requests_per_minute", 10), 1e-9)
        wait = self._last_call + gap - self.clock()
        if wait > 0:
            self.sleep(wait)
        self._last_call = self.clock()

    def _with_retry(self, fn, *args):
        tries = self.cfg.get("max_retries", 4)
        for i in range(tries):
            try:
                self._pace()
                return fn(*args)
            except RetryableError:
                if i == tries - 1:
                    raise
                self.sleep(min(60, 2 ** (i + 1)))

    def request(self, kind: str, prompt: str, schema: dict, max_tokens: int = 8192) -> dict:
        """Gọi LLM (có cache). Trả dict JSON + provider/model/cached."""
        last = None
        for prov in self.providers():
            model = self.cfg[f"model_{prov}"]
            f = self.cache_dir / f"{self._key(model, kind, prompt)}.json"
            if f.exists():
                self.cache_hits += 1
                return {**json.loads(f.read_text(encoding="utf-8")), "cached": True}
            if self.calls >= self.cfg.get("max_total_calls", 0):
                raise BudgetExceeded(f"đã dùng hết max_total_calls = {self.cfg.get('max_total_calls')}")
            try:
                self.calls += 1
                raw, usage = self._with_retry(self._backend(prov), model, prompt, schema, max_tokens)
                out = parse_json(raw)
            except BudgetExceeded:
                raise
            except Exception as e:
                self.fail_streak[prov] += 1; last = e
                continue
            self.fail_streak[prov] = 0
            for k, v in (usage or {}).items():
                self.usage[f"{prov}_{k}"] += v or 0
            out = {**out, "provider": prov, "model": model, "usage": usage}
            f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
            return {**out, "cached": False}
        raise LLMError(f"mọi provider đều lỗi hoặc không có API key: {last}")

    # ---------- API dùng trong pipeline ----------
    def classify_narrative(self, headline: str) -> dict:
        """Zero-shot narrative + sentiment cho một tiêu đề. Nhãn ngoài danh sách → 'other'."""
        out = self.request("narrative", PROMPT_NARRATIVE + headline.strip(), NARRATIVE_SCHEMA, max_tokens=200)
        if out.get("narrative") not in NARRATIVES:
            out["narrative"] = "other"
        return out
