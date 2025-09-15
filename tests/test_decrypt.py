import json

from app.crypto.keys import ensure_rsa_keys
from app.services.decrypt import decrypt_payload


def _enc_sample(plaintext: dict):
    # Build a sample encrypted payload using the same primitives as the server
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256
    from Crypto.Random import get_random_bytes

    priv, pub_pem = ensure_rsa_keys()
    # Generate AES key and IV
    aes_key = get_random_bytes(32)
    iv = get_random_bytes(12)

    # Encrypt plaintext
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(json.dumps(plaintext).encode("utf-8"))

    # Wrap AES key
    from Crypto.PublicKey import RSA

    rsa_pub = RSA.import_key(pub_pem)
    rsa_wrap = PKCS1_OAEP.new(rsa_pub, hashAlgo=SHA256)
    cek = rsa_wrap.encrypt(aes_key)

    return {
        "iv": iv,
        "data": ct,
        "tag": tag,
        "cek": cek,
    }


def test_decrypt_happy_path():
    ptxt = {
        "name": "Alice",
        "telegram": "@alice",
        "budget": "1000",
        "brief": "Hello",
        "deadline": "soon",
        "contact": "a@example.com",
        "source": "test",
    }
    enc = _enc_sample(ptxt)
    out = decrypt_payload(enc["iv"], enc["data"], enc["tag"], enc["cek"])
    assert out["name"] == "Alice"
    assert out["telegram"] == "@alice"


def test_decrypt_tag_mismatch():
    ptxt = {"x": "y"}
    enc = _enc_sample(ptxt)
    # Corrupt tag
    bad_tag = bytes([b ^ 0xFF for b in enc["tag"]])
    from http import HTTPStatus

    from fastapi import HTTPException

    try:
        decrypt_payload(enc["iv"], enc["data"], bad_tag, enc["cek"])
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == HTTPStatus.BAD_REQUEST
        assert "decryption failed" in e.detail
