# lib/aes_utils.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Populate this at app start with 32-byte key
KEY = None

def init(key_bytes: bytes):
    global KEY
    if not isinstance(key_bytes, (bytes, bytearray)) or len(key_bytes) < 16:
        raise ValueError("AES key must be bytes (>=16).")
    # use 32 bytes
    KEY = key_bytes[:32].ljust(32, b'\0')

def encrypt_aes(plaintext: bytes) -> str:
    """Return base64 of iv(12)+tag(16)+ciphertext."""
    iv = get_random_bytes(12)
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    payload = iv + tag + ct
    return base64.b64encode(payload).decode('utf-8')

def decrypt_aes(b64payload: str) -> bytes:
    payload = base64.b64decode(b64payload)
    iv = payload[:12]
    tag = payload[12:28]
    ct = payload[28:]
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=iv)
    return cipher.decrypt_and_verify(ct, tag)
