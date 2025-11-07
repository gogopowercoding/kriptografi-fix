# lib/crypto.py
import os
import base64
from Crypto.Cipher import AES

# ---------- AES key ----------
# gunakan variabel environment di produksi; 32 bytes untuk AES-256
AES_KEY = (os.environ.get('SECUREVAULT_AES_KEY') or 'default_32_byte_aes_key________').encode('utf-8')[:32]

# ---------------- AES (EAX mode) ----------------
def aes_encrypt(plaintext: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    payload = cipher.nonce + tag + ciphertext
    return base64.b64encode(payload).decode('utf-8')

def aes_decrypt(b64payload: str) -> str:
    raw = base64.b64decode(b64payload)
    if len(raw) < 32:
        raise ValueError("Payload AES terlalu pendek / korup")
    nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
    cipher = AES.new(AES_KEY, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')

# ---------------- Caesar cipher (simple) ----------------
def _shift_char(c: str, shift: int) -> str:
    o = ord(c)
    if 65 <= o <= 90:
        return chr(((o - 65 + shift) % 26) + 65)
    if 97 <= o <= 122:
        return chr(((o - 97 + shift) % 26) + 97)
    return c

def caesar_encrypt(text: str, key: str) -> str:
    if not key: shift = 3
    else: shift = sum(ord(ch) for ch in key) % 26
    return ''.join(_shift_char(c, shift) for c in text)

def caesar_decrypt(text: str, key: str) -> str:
    if not key: shift = 3
    else: shift = sum(ord(ch) for ch in key) % 26
    return ''.join(_shift_char(c, -shift) for c in text)

# ---------------- Simple FSR-like layer (educational) ----------------
# deterministic Feistel-like rounds over bytes; return latin-1 string to preserve bytes
def fsr_encrypt(text: str, key: str) -> str:
    if text == "":
        return ""
    data = text.encode('utf-8')
    # pad to even length
    if len(data) % 2 == 1:
        data += b'\x00'
    half = len(data) // 2
    L = bytearray(data[:half])
    R = bytearray(data[half:])
    key_bytes = (key or "k").encode('utf-8')
    rounds = max(1, len(key_bytes))
    for i in range(rounds):
        k = key_bytes[i % len(key_bytes)]
        f = bytearray(((b + k) & 0xFF) for b in R)
        newR = bytearray(a ^ b for a, b in zip(L, f))
        L = R
        R = newR
    out = bytes(L + R)
    return out.decode('latin-1')

def fsr_decrypt(cipher_text: str, key: str) -> str:
    if cipher_text == "":
        return ""
    data = cipher_text.encode('latin-1')
    half = len(data) // 2
    L = bytearray(data[:half])
    R = bytearray(data[half:])
    key_bytes = (key or "k").encode('utf-8')
    rounds = max(1, len(key_bytes))
    for i in reversed(range(rounds)):
        k = key_bytes[i % len(key_bytes)]
        f = bytearray(((b + k) & 0xFF) for b in L)
        prevL = bytearray(a ^ b for a, b in zip(R, f))
        R = L
        L = prevL
    out = bytes(L + R)
    if out and out[-1] == 0:
        out = out[:-1]
    return out.decode('utf-8', errors='ignore')
