import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSA_PRIV_PEM = os.getenv("RSA_PRIV_PEM")
RSA_PUB_PEM = os.getenv("RSA_PUB_PEM")
RSA_PRIV_PATH = os.getenv("RSA_PRIV_PATH")
RSA_PUB_PATH = os.getenv("RSA_PUB_PATH")

# Comma-separated list of allowed origins (e.g., "https://example.com,https://www.example.com").
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
