"""
VieNeu TTS API Server (standalone)
==================================
Gói API độc lập cho VieNeu-TTS, chạy bằng package `vieneu` trên PyPI
(không cần toàn bộ source VieNeu Studio).

Chạy:
    uvicorn server:app --host 0.0.0.0 --port 8000

Cấu hình qua biến môi trường:
    VIENEU_MODE       v3nano | turbo        (mặc định: v3nano)
    VIENEU_PRECISION  int8 | fp32           (mặc định: int8, chỉ ảnh hưởng turbo)
    VIENEU_VOICE      giọng mặc định        (mặc định: giọng đầu tiên trong preset)
    TTS_API_KEY       nếu đặt, client phải gửi header X-API-Key hoặc ?api_key=
    TTS_MAX_CHARS     giới hạn độ dài text mỗi request (mặc định: 5000)

Endpoints:
    GET  /health   -> trạng thái server + model đã load chưa
    GET  /voices   -> danh sách giọng preset [{label, id}]
    POST /speak    -> JSON {text, voice?, speed?} -> trả về file WAV trực tiếp
"""

from __future__ import annotations

import io
import logging
import os
import threading
import time

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("vieneu-tts-api")

MODE = os.getenv("VIENEU_MODE", "v3nano").strip().lower()          # v3nano | turbo
PRECISION = os.getenv("VIENEU_PRECISION", "int8").strip().lower()  # int8 | fp32 (turbo)
DEFAULT_VOICE = os.getenv("VIENEU_VOICE", "").strip()
API_KEY = os.getenv("TTS_API_KEY", "").strip()
MAX_CHARS = int(os.getenv("TTS_MAX_CHARS", "5000"))

_engine = None
_engine_lock = threading.Lock()
_engine_meta: dict = {"loaded": False, "mode": MODE, "sample_rate": None, "error": None}
_voices_cache: list[dict] = []


def _load_engine():
    """Load model 1 lần duy nhất (lazy, thread-safe)."""
    global _engine
    with _engine_lock:
        if _engine is not None:
            return _engine
        from vieneu import Vieneu

        t0 = time.time()
        log.info("Đang load model VieNeu-TTS (mode=%s, precision=%s)...", MODE, PRECISION)
        try:
            if MODE == "v3nano":
                _engine = Vieneu(mode="v3nano")
            else:
                _engine = Vieneu(precision=PRECISION)
        except Exception as exc:  # noqa: BLE001
            _engine_meta["error"] = str(exc)
            log.exception("Load model thất bại")
            raise
        _engine_meta["loaded"] = True
        _engine_meta["sample_rate"] = getattr(_engine, "sample_rate", 24000 if MODE == "v3nano" else 48000)
        log.info("Load model xong sau %.1fs (sample_rate=%s)", time.time() - t0, _engine_meta["sample_rate"])

        # cache danh sách giọng
        try:
            for label, vid in _engine.list_preset_voices():
                _voices_cache.append({"label": str(label), "id": str(vid)})
        except Exception as exc:  # noqa: BLE001
            log.warning("Không lấy được danh sách giọng: %s", exc)
        return _engine


def _default_voice() -> str:
    if DEFAULT_VOICE:
        return DEFAULT_VOICE
    ids = [v["id"] for v in _voices_cache]
    return "Hữu Quân" if "Hữu Quân" in ids else (ids[0] if ids else "")


def _check_auth(request: Request):
    if not API_KEY:
        return
    provided = request.headers.get("x-api-key", "") or request.query_params.get("api_key", "")
    if provided != API_KEY:
        raise HTTPException(status_code=401, detail="Sai hoặc thiếu API key.")


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Văn bản cần đọc")
    voice: str = Field(default="", description="Tên/id giọng (xem /voices). Để trống = giọng mặc định.")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Tốc độ đọc 0.5 - 2.0")


def _wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    import soundfile as sf

    buf = io.BytesIO()
    sf.write(buf, np.asarray(audio, dtype=np.float32), sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


app = FastAPI(title="VieNeu TTS API", version="1.0.0")


@app.on_event("startup")
async def _startup():
    # Preload model ngay khi server khởi động để request đầu không phải chờ.
    # Nếu model chưa tải về, lần đầu sẽ tải từ HuggingFace (cần mạng).
    try:
        await run_in_threadpool(_load_engine)
    except Exception as exc:  # noqa: BLE001
        log.error("Preload model thất bại, sẽ thử lại ở request đầu: %s", exc)


@app.get("/health")
async def health():
    return {
        "status": "ok" if _engine_meta["loaded"] else "loading",
        "mode": MODE,
        "precision": PRECISION,
        "sample_rate": _engine_meta["sample_rate"],
        "voices": len(_voices_cache),
        "error": _engine_meta["error"],
    }


@app.get("/voices")
async def voices(request: Request):
    _check_auth(request)
    _load_engine()
    return {"voices": _voices_cache, "default": _default_voice()}


@app.post("/speak")
async def speak(req: SpeakRequest, request: Request):
    _check_auth(request)
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text rỗng.")
    if len(text) > MAX_CHARS:
        raise HTTPException(status_code=400, detail=f"Text quá dài (tối đa {MAX_CHARS} ký tự).")

    engine = _load_engine()
    voice = req.voice.strip() or _default_voice()

    def _do_infer():
        kwargs: dict = {"voice": voice} if voice else {}
        # speed: nano hỗ trợ native; turbo cũng nhận speed qua infer
        try:
            return engine.infer(text, speed=req.speed, **kwargs)
        except TypeError:
            return engine.infer(text, **kwargs)

    t0 = time.time()
    try:
        audio = await run_in_threadpool(_do_infer)
    except Exception as exc:
        log.exception("infer thất bại")
        raise HTTPException(status_code=500, detail=f"Lỗi tổng hợp giọng nói: {exc}")
    elapsed = time.time() - t0

    wav = _wav_bytes(audio, _engine_meta["sample_rate"] or 24000)
    audio_sec = len(np.asarray(audio).ravel()) / (_engine_meta["sample_rate"] or 24000)
    log.info("speak: %d ký tự -> %.1fs audio (%.1fs wall, voice=%s)", len(text), audio_sec, elapsed, voice or "-")

    # Header HTTP chỉ chấp nhận ký tự latin-1 -> sanitize tên giọng Unicode
    safe_voice = (voice or "").encode("ascii", errors="ignore").decode("ascii")
    return StreamingResponse(
        io.BytesIO(wav),
        media_type="audio/wav",
        headers={
            "Content-Disposition": 'attachment; filename="speech.wav"',
            "X-Audio-Seconds": f"{audio_sec:.2f}",
            "X-Voice": safe_voice,
        },
    )


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    log.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Lỗi server."})
