from functools import lru_cache

from fastapi import HTTPException

from app.core.config import RSA_PRIV_PATH, RSA_PRIV_PEM, RSA_PUB_PATH, RSA_PUB_PEM
from app.core.constants import RSA_KEY_SIZE


def _read_file(path: str | None) -> bytes | None:
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_keys() -> tuple[object, bytes]:
    try:
        from Crypto.PublicKey import RSA  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Crypto backend unavailable: {e}"
        ) from e

    priv_pem = (RSA_PRIV_PEM.encode("utf-8") if RSA_PRIV_PEM else None) or _read_file(
        RSA_PRIV_PATH
    )
    pub_pem = (RSA_PUB_PEM.encode("utf-8") if RSA_PUB_PEM else None) or _read_file(
        RSA_PUB_PATH
    )

    if priv_pem:
        rsa_priv = RSA.import_key(priv_pem)
        rsa_pub_pem: bytes = pub_pem or rsa_priv.publickey().export_key("PEM")
    else:
        key = RSA.generate(RSA_KEY_SIZE)
        rsa_priv = key
        rsa_pub_pem = key.publickey().export_key("PEM")
    return rsa_priv, rsa_pub_pem


def ensure_rsa_keys():
    return _load_keys()


def get_public_pem() -> bytes:
    _, pub = _load_keys()
    if not pub:
        raise HTTPException(status_code=503, detail="Public key not available")
    return pub  # bytes
