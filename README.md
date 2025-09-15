# telegram-lead-bot

FastAPI backend for encrypted lead submissions sent to Telegram.

## Architecture
- app/app.py: FastAPI app factory
- app/api/routes.py: HTTP endpoints (/pubkey, /lead)
- app/schemas/lead.py: request models
- app/crypto/keys.py: RSA key management (load or generate)
- app/services/decrypt.py: RSA-OAEP + AES-GCM decrypt
- app/services/telegram_bot.py: lazy aiogram bot
- app/core/config.py: environment config
- main.py: thin entrypoint

## Environment
- BOT_TOKEN: Telegram bot token
- CHAT_ID: Target chat ID
- (Optional) RSA keys:
  - RSA_PRIV_PEM / RSA_PUB_PEM (PEM content)
  - or RSA_PRIV_PATH / RSA_PUB_PATH (file paths)
 - ALLOWED_ORIGINS: Comma-separated list of allowed origins for /pubkey and /lead
   (e.g., `https://example.com,https://www.example.com`).
   When set, CORS is enabled for these origins, and requests with other origins
   will receive 403. If not set, origin checks are bypassed (useful for local dev/tests).

## Run
```bash
# install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# dev tools (optional)
pip install -r requirements-dev.txt
pre-commit install

# run
uvicorn main:app --host 127.0.0.1 --port 3000
```

## API (all endpoints under /api)
- GET /api/pubkey → PEM public key
- POST /api/lead → body (all bytes arrays):
  - iv: 12-byte nonce
  - data: ciphertext
  - tag: 16-byte GCM tag
  - cek: RSA-OAEP(SHA-256) wrapped AES key

## Tests
```bash
pytest -q
```

## CI
GitHub Actions runs ruff (check), black --check, and pytest on push/PR.
