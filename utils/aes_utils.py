from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Kunci AES (16, 24, 32 byte)
AES_KEY = b'ThisIs16ByteKey!'  # ganti sesuai kebutuhan
AES_IV = b'ThisIs16ByteIV!!'   # 16 byte IV

def pad(data: bytes) -> bytes:
    """PKCS7 padding"""
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Padding tidak valid")
    return data[:-pad_len]

def encrypt_aes_bytes(plaintext: str) -> bytes:
    """Encrypt string dan kembalikan bytes"""
    data_bytes = plaintext.encode('utf-8')
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted = cipher.encrypt(pad(data_bytes))
    return encrypted

def decrypt_aes_bytes(ciphertext: bytes) -> str:
    """Decrypt bytes dan kembalikan string"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted = unpad(cipher.decrypt(ciphertext))
    return decrypted.decode('utf-8')
