import asyncio
from collections.abc import Iterable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.config import ALLOWED_ORIGINS, CHAT_ID
from app.core.constants import (
    BRIEF_MAX,
    BUDGET_MAX,
    DEADLINE_MAX,
    EMAIL_MAX,
    NAME_MAX,
    PEM_MEDIA_TYPE,
    SOURCE_MAX,
    TELEGRAM_MAX,
)
from app.schemas.lead import EncryptedData
from app.services.decrypt import decrypt_payload

router = APIRouter()


def _parse_allowed_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [o.strip() for o in value.split(",") if o.strip()]


def require_allowed_origin(
    request: Request, origins: Iterable[str] | None = None
) -> None:
    # Check Origin header for CORS requests; fall back to Referer for same-origin navigations.
    allowed = list(origins or _parse_allowed_origins(ALLOWED_ORIGINS))
    if not allowed:
        # Not configured: allow (dev/tests). Set ALLOWED_ORIGINS to enforce.
        return None
    origin = request.headers.get("origin") or ""
    if not origin:
        # Try derive from referer origin
        ref = request.headers.get("referer") or ""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(ref)
            if parsed.scheme and parsed.netloc:
                origin = f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            origin = ""
    if origin not in allowed:
        raise HTTPException(status_code=403, detail="origin not allowed")


def get_bot_from_state(request: Request):
    bot = getattr(request.app.state, "bot", None)
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is not configured")
    return bot


def get_pubkey_pem_from_state(request: Request) -> bytes:
    pem = getattr(request.app.state, "rsa_pub_pem", None)
    if not pem:
        raise HTTPException(status_code=503, detail="Public key not available")
    return pem


@router.get("/pubkey", dependencies=[Depends(require_allowed_origin)])
async def get_pubkey(
    pem: Annotated[bytes, Depends(get_pubkey_pem_from_state)],
):
    # pem is bytes
    return Response(content=pem, media_type=PEM_MEDIA_TYPE)


@router.post("/lead", dependencies=[Depends(require_allowed_origin)])
async def receive_lead(
    payload: EncryptedData,
    bot: Annotated[Any, Depends(get_bot_from_state)],
):
    iv = bytes(payload.iv)
    data = bytes(payload.data)
    tag = bytes(payload.tag) if payload.tag is not None else None
    cek = bytes(payload.cek) if payload.cek is not None else None

    loop = asyncio.get_running_loop()
    # Offload CPU-bound RSA/AES decrypt to thread pool to avoid blocking.
    d = await loop.run_in_executor(None, decrypt_payload, iv, data, tag, cek)

    def _clip(s: str | None, n: int) -> str:
        if not isinstance(s, str):
            return ""
        return s[:n]

    text = (
        f"📩 New request\n"
        f"👤 Name: {_clip(d.get('name'), NAME_MAX)}\n"
        f"💬 Telegram: {_clip(d.get('telegram'), TELEGRAM_MAX)}\n"
        f"💰 Budget: {_clip(d.get('budget'), BUDGET_MAX)}\n"
        f"📝 Brief: {_clip(d.get('brief'), BRIEF_MAX)}\n"
        f"⏰ Deadline: {_clip(d.get('deadline'), DEADLINE_MAX)}\n"
        f"📧 Email: {_clip(d.get('contact'), EMAIL_MAX)}\n"
        f"🔗 Source: {_clip(d.get('source'), SOURCE_MAX)}"
    )

    await bot.send_message(CHAT_ID, text)
    return {"status": "ok"}
