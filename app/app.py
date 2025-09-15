from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import health_router
from app.api.routes import router
from app.core.config import ALLOWED_ORIGINS, BOT_TOKEN
from app.core.logging import configure_logging
from app.crypto.keys import ensure_rsa_keys
from app.services.telegram_bot import create_bot


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI()
    # Initialize RSA keys and expose via app.state
    rsa_priv, rsa_pub_pem = ensure_rsa_keys()
    app.state.rsa_priv = rsa_priv
    app.state.rsa_pub_pem = rsa_pub_pem

    # Initialize Telegram Bot if token provided; keep optional to not break tests/dev
    app.state.bot = create_bot(BOT_TOKEN) if BOT_TOKEN else None

    origins = [o.strip() for o in (ALLOWED_ORIGINS or "").split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
    app.include_router(health_router, prefix="/api")
    app.include_router(router, prefix="/api")
    return app
