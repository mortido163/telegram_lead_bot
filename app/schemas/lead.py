from pydantic import BaseModel, Field


class EncryptedData(BaseModel):
    iv: list[int] = Field(..., description="12-byte GCM nonce")
    data: list[int] = Field(..., description="Ciphertext bytes")
    tag: list[int] | None = Field(None, description="16-byte GCM tag")
    cek: list[int] | None = Field(None, description="RSA-OAEP wrapped AES key")
