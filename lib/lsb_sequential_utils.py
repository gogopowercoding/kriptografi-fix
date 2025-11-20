# lib/lsb_sequential_utils.py
from PIL import Image
import numpy as np

def image_to_array_rgb(path):
    img = Image.open(path).convert('RGB')
    return np.array(img)

def array_to_image_rgb(arr, path=None):
    img = Image.fromarray(np.uint8(arr))
    if path:
        img.save(path, format='PNG')
    return img

def calculate_capacity(cover_arr):
    h, w, c = cover_arr.shape
    total_bits = h * w * c  # bits available (1 bit per channel)
    total_bytes = total_bits // 8
    # Reserve 4 bytes for length header
    return total_bytes - 4

def embed_message_rgb(cover_arr, message_bytes):
    """
    message_bytes: actual bytes to embed (already prepared, e.g. IV+CT)
    We'll prepend 4-byte length (big-endian) inside this function.
    """
    message_len = len(message_bytes)
    header = message_len.to_bytes(4, 'big')
    full = header + message_bytes  # bytes

    # convert to bit list (MSB first per byte)
    bits = []
    for b in full:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    stego = cover_arr.copy()
    flat = stego.flatten()

    if len(bits) > len(flat):
        raise ValueError(f"Message terlalu besar! Need {len(bits)} bits, available {len(flat)} bits")

    for i, bit in enumerate(bits):
        flat[i] = (int(flat[i]) & 0xFE) | bit

    stego = flat.reshape(stego.shape)
    return stego

def extract_message_rgb(stego_arr):
    flat = stego_arr.flatten()

    # read 32 bits for length
    if len(flat) < 32:
        raise ValueError("Gambar terlalu kecil untuk menyimpan header panjang")

    length_bits = [int(flat[i]) & 1 for i in range(32)]
    message_len = 0
    for bit in length_bits:
        message_len = (message_len << 1) | bit

    # validate
    total_bytes_available = (len(flat) // 8) - 4
    if message_len <= 0 or message_len > total_bytes_available:
        raise ValueError(f"Panjang message tidak valid: {message_len} (max {total_bytes_available})")

    total_bits_needed = 32 + (message_len * 8)
    if total_bits_needed > len(flat):
        raise ValueError("Data tidak cukup untuk extract message")

    # extract bits
    bits = [int(flat[i]) & 1 for i in range(32, total_bits_needed)]

    # build bytes
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        out.append(byte)

    return bytes(out)
