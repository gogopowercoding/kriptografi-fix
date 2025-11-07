# lib/caesar_fsr.py
import hashlib

def _keystream(seed: bytes, length: int):
    out = bytearray()
    state = seed
    while len(out) < length:
        state = hashlib.sha256(state).digest()
        out.extend(state)
    return bytes(out[:length])

def encrypt_text(plaintext: str, passphrase: str) -> bytes:
    data = plaintext.encode('utf-8')
    shift = sum(passphrase.encode('utf-8')) % 256
    shifted = bytes((b + shift) % 256 for b in data)
    ks = _keystream(passphrase.encode('utf-8'), len(shifted))
    cipher = bytes(a ^ b for a, b in zip(shifted, ks))
    return cipher

def decrypt_text(cipherbytes: bytes, passphrase: str) -> str:
    ks = _keystream(passphrase.encode('utf-8'), len(cipherbytes))
    shifted = bytes(a ^ b for a, b in zip(cipherbytes, ks))
    shift = sum(passphrase.encode('utf-8')) % 256
    plain = bytes((b - shift) % 256 for b in shifted)
    return plain.decode('utf-8', errors='ignore')
