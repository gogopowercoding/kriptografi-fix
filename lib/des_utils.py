# lib/des_utils.py
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


#  ENKRIPSI DES (bytes in → bytes out)

def encrypt_des(data_bytes: bytes, key: str) -> bytes:
   
    if len(key) != 8:
        raise ValueError("Kunci DES HARUS 8 karakter.")

    key_bytes = key.encode()          # convert ke bytes
    cipher = DES.new(key_bytes, DES.MODE_ECB)

    padded = pad(data_bytes, 8)       # DES block size = 8 bytes
    ct = cipher.encrypt(padded)

    return ct                         


def decrypt_des(cipher_bytes: bytes, key: str) -> bytes:
  
    if len(key) != 8:
        raise ValueError("Kunci DES HARUS 8 karakter.")

    key_bytes = key.encode()
    cipher = DES.new(key_bytes, DES.MODE_ECB)

    pt_padded = cipher.decrypt(cipher_bytes)
    pt = unpad(pt_padded, 8)

    return pt                         
