import json

from fastapi import HTTPException

from app.core.constants import (
    AES_KEY_SIZES,
    GCM_NONCE_LEN,
    GCM_TAG_LEN,
    MAX_PAYLOAD_BYTES,
)
from app.crypto.keys import ensure_rsa_keys


def decrypt_payload(
    iv: bytes, data: bytes, tag: bytes | None, cek: bytes | None
) -> dict:
    if len(iv) != GCM_NONCE_LEN:
        raise HTTPException(status_code=400, detail="invalid iv length")
    if len(data) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=400, detail="payload too large")

    # Determine AES key
    if cek is None:
        raise HTTPException(status_code=400, detail="cek is required")
    priv, _ = ensure_rsa_keys()
    try:
        from Crypto.Cipher import PKCS1_OAEP  # type: ignore
        from Crypto.Hash import SHA256  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Crypto backend unavailable: {e}"
        ) from e
    cipher_rsa = PKCS1_OAEP.new(priv, hashAlgo=SHA256)  # type: ignore[arg-type]
    aes_key = cipher_rsa.decrypt(cek)
    if len(aes_key) not in AES_KEY_SIZES:
        raise HTTPException(status_code=400, detail="invalid cek unwrapped length")

    if tag is None:
        if len(data) < GCM_TAG_LEN:
            raise HTTPException(status_code=400, detail="ciphertext too short")
        data, tag = data[:-GCM_TAG_LEN], data[-GCM_TAG_LEN:]

    try:
        from Crypto.Cipher import AES  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Crypto backend unavailable: {e}"
        ) from e

    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    try:
        plaintext = cipher.decrypt_and_verify(data, tag)
    except Exception as e:
        # Invalid tag or corrupt data
        raise HTTPException(status_code=400, detail="decryption failed") from e
    return json.loads(plaintext.decode("utf-8"))
