import json
from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient

from app.app import create_app
from app.crypto.keys import ensure_rsa_keys


def _enc_sample(plaintext: dict[str, Any]):
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes

    priv, pub_pem = ensure_rsa_keys()
    rsa_pub = RSA.import_key(pub_pem)

    aes_key = get_random_bytes(32)
    iv = get_random_bytes(12)

    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(json.dumps(plaintext).encode("utf-8"))

    cek_wrap = PKCS1_OAEP.new(rsa_pub, hashAlgo=SHA256)
    cek = cek_wrap.encrypt(aes_key)

    return iv, ct, tag, cek


def test_pubkey_ok():
    app = create_app()
    client = TestClient(app)
    r = client.get("/api/pubkey")
    assert r.status_code == HTTPStatus.OK
    assert r.text.startswith("-----BEGIN PUBLIC KEY-----")


def test_lead_ok():
    # Provide a fake bot via app.state to avoid real Telegram calls
    class FakeBot:
        def __init__(self):
            self.calls = []

        async def send_message(self, chat_id, text):
            self.calls.append((chat_id, text))

    app = create_app()
    fake = FakeBot()
    app.state.bot = fake
    client = TestClient(app)

    # Build encrypted payload
    iv, ct, tag, cek = _enc_sample(
        {
            "name": "Bob",
            "telegram": "@bob",
            "budget": "2000",
            "brief": "Project",
            "deadline": "tomorrow",
            "contact": "b@example.com",
            "source": "pytest",
        }
    )

    payload = {
        "iv": list(iv),
        "data": list(ct),
        "tag": list(tag),
        "cek": list(cek),
    }

    r = client.post("/api/lead", json=payload)
    assert r.status_code == HTTPStatus.OK, r.text
    # Ensure our fake bot was called
    assert fake.calls, "Bot was not called"
    chat_id, text = fake.calls[-1]
    assert "Bob" in text and "@bob" in text
