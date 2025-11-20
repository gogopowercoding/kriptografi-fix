# utils/aes_utils.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Gunakan kunci 16/24/32 bytes. Simpan di config/env sebaiknya.
AES_KEY = b'ThisIs16ByteKey!'  # contoh: ganti di production

def _pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def _unpad(data: bytes) -> bytes:
    if not data:
        raise ValueError("Padding tidak valid")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Padding tidak valid")
    return data[:-pad_len]

def encrypt_aes_bytes(plaintext: str) -> bytes:
    """
    Encrypt plaintext (str) -> return bytes: IV(16) || ciphertext
    """
    data = plaintext.encode('utf-8')
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(_pad(data))
    return iv + ct

def decrypt_aes_bytes(payload: bytes) -> str:
    """
    Decrypt payload bytes (IV||CT) -> return plaintext string
    """
    if len(payload) < 16:
        raise ValueError("Payload AES terlalu pendek")
    iv = payload[:16]
    ct = payload[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    pt_padded = cipher.decrypt(ct)
    pt = _unpad(pt_padded)
    return pt.decode('utf-8', errors='strict')
