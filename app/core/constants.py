"""Project-wide constants to avoid magic numbers."""

# Crypto parameters
GCM_NONCE_LEN = 12  # bytes
GCM_TAG_LEN = 16  # bytes
MAX_PAYLOAD_BYTES = 64 * 1024
AES_KEY_SIZES = (16, 24, 32)

# RSA
RSA_KEY_SIZE = 2048

# Message clipping limits
NAME_MAX = 100
TELEGRAM_MAX = 64
BUDGET_MAX = 32
BRIEF_MAX = 2000
DEADLINE_MAX = 60
EMAIL_MAX = 254
SOURCE_MAX = 512

# Media types
PEM_MEDIA_TYPE = "application/x-pem-file"
