# lib/twofish_utils.py
from twofish import Twofish
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = 16

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings"""
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt_bytes(key: bytes, data: bytes) -> bytes:
    """Encrypt data using Twofish in CBC mode"""
    tf = Twofish(key[:16])  # Twofish key max 16 bytes
    data_padded = pad(data, BLOCK_SIZE)
    iv = get_random_bytes(BLOCK_SIZE)
    ct = b''
    prev = iv
    # CBC mode manual
    for i in range(0, len(data_padded), BLOCK_SIZE):
        block = data_padded[i:i+BLOCK_SIZE]
        block_xor = xor_bytes(block, prev)
        enc_block = tf.encrypt(block_xor)
        ct += enc_block
        prev = enc_block
    return iv + ct

def decrypt_bytes(key: bytes, payload: bytes) -> bytes:
    """Decrypt data using Twofish in CBC mode"""
    tf = Twofish(key[:16])
    iv = payload[:BLOCK_SIZE]
    ct = payload[BLOCK_SIZE:]
    plaintext = b''
    prev = iv
    for i in range(0, len(ct), BLOCK_SIZE):
        block = ct[i:i+BLOCK_SIZE]
        dec_block = tf.decrypt(block)
        plain_block = xor_bytes(dec_block, prev)
        plaintext += plain_block
        prev = block
    return unpad(plaintext, BLOCK_SIZE)
