from PIL import Image
import numpy as np

def image_to_array_rgb(path):
    """Load RGB image as 3D numpy array (H x W x 3)"""
    img = Image.open(path).convert('RGB')
    return np.array(img)

def array_to_image_rgb(arr, path=None):
    """Convert 3D array to RGB image"""
    img = Image.fromarray(np.uint8(arr))
    if path:
        img.save(path)
    return img

def calculate_capacity(cover_arr, **kwargs):
    """Calculate maximum capacity in bytes for LSB embedding"""
    # LSB dapat menyimpan 1 bit per channel per pixel
    # Total pixels * 3 channels = total bits
    # Dibagi 8 = total bytes
    h, w, c = cover_arr.shape
    total_bits = h * w * c  # 3 channels (RGB)
    bytes_capacity = total_bits // 8
    
    # Kurangi 4 bytes untuk panjang message
    return bytes_capacity - 4

def embed_message_rgb(cover_arr, message_bytes, **kwargs):
    """Embed message bytes into cover RGB array using LSB Sequential"""
    # Tambahkan panjang message di awal (4 bytes)
    message_len = len(message_bytes)
    full_message = message_len.to_bytes(4, 'big') + message_bytes
    
    # Convert message to bits
    message_bits = []
    for byte in full_message:
        for i in range(7, -1, -1):  # MSB first
            message_bits.append((byte >> i) & 1)
    
    # Copy cover array untuk modifikasi
    stego_arr = cover_arr.copy()
    
    # Flatten array untuk akses sequential
    h, w, c = stego_arr.shape
    flat_stego = stego_arr.flatten()
    
    # Check capacity
    if len(message_bits) > len(flat_stego):
        raise ValueError(f"Message terlalu besar! Butuh {len(message_bits)} bits, tersedia {len(flat_stego)} bits")
    
    # Embed bits ke LSB secara sequential
    for i, bit in enumerate(message_bits):
        # Clear LSB dan set dengan bit message
        flat_stego[i] = (flat_stego[i] & 0xFE) | bit
    
    # Reshape kembali
    stego_arr = flat_stego.reshape((h, w, c))
    
    return stego_arr

def extract_message_rgb(stego_arr, **kwargs):
    """Extract message bytes from stego RGB array using LSB Sequential"""
    # Flatten array untuk akses sequential
    h, w, c = stego_arr.shape
    flat_stego = stego_arr.flatten()
    
    # Extract LSB untuk mendapatkan length (4 bytes = 32 bits)
    length_bits = []
    for i in range(32):  # 4 bytes * 8 bits
        length_bits.append(flat_stego[i] & 1)
    
    # Convert length bits to integer
    message_len = 0
    for bit in length_bits:
        message_len = (message_len << 1) | bit
    
    # Validasi panjang message
    max_available = (len(flat_stego) // 8) - 4
    if message_len <= 0 or message_len > max_available:
        raise ValueError(f"Panjang message tidak valid: {message_len} (max: {max_available} bytes)")
    
    # Extract message bits
    total_bits_needed = 32 + (message_len * 8)  # length + message
    
    if total_bits_needed > len(flat_stego):
        raise ValueError(f"Data tidak cukup untuk extract message")
    
    message_bits = []
    for i in range(32, total_bits_needed):
        message_bits.append(flat_stego[i] & 1)
    
    # Convert bits to bytes
    message_bytes = []
    for i in range(0, len(message_bits), 8):
        byte_bits = message_bits[i:i+8]
        byte_val = 0
        for bit in byte_bits:
            byte_val = (byte_val << 1) | bit
        message_bytes.append(byte_val)
    
    return bytes(message_bytes)

# Legacy functions untuk backward compatibility
def extract_bit_planes_rgb(arr):
    """Return 3 lists of 8 bit-planes each, for R,G,B channels"""
    planes_r = [(arr[:,:,0] >> i) & 1 for i in range(8)]
    planes_g = [(arr[:,:,1] >> i) & 1 for i in range(8)]
    planes_b = [(arr[:,:,2] >> i) & 1 for i in range(8)]
    return planes_r, planes_g, planes_b

def merge_bit_planes_rgb(planes_r, planes_g, planes_b):
    """Merge bit-planes back to 3D RGB array"""
    h, w = planes_r[0].shape
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(8):
        arr[:,:,0] |= (planes_r[i].astype(np.uint8) << i)
        arr[:,:,1] |= (planes_g[i].astype(np.uint8) << i)
        arr[:,:,2] |= (planes_b[i].astype(np.uint8) << i)
    return arr

def complexity(block):
    """Compute complexity of a block (0..1)"""
    h, w = block.shape
    if h <= 1 or w <= 1:
        return 0
    horz = np.sum(block[:, :-1] != block[:, 1:])
    vert = np.sum(block[:-1, :] != block[1:, :])
    max_transitions = 2*h*w - h - w
    if max_transitions == 0:
        return 0
    return (horz + vert) / max_transitions

def is_complex(block, alpha=0.3):
    return complexity(block) >= alpha

def divide_blocks(plane, block_size=8):
    """Divide bit-plane into blocks of size block_size x block_size"""
    h, w = plane.shape
    blocks = []
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = plane[i:i+block_size, j:j+block_size]
            if block.shape == (block_size, block_size):
                blocks.append((i, j, block))
    return blocks

def embed_payload_rgb(cover_arr, payload_arr, block_size=8, alpha=0.3):
    """Legacy function - now uses LSB"""
    # Convert payload array to bytes
    payload_bytes = payload_arr.flatten().tobytes()
    return embed_message_rgb(cover_arr, payload_bytes)

def extract_payload_rgb(stego_arr, block_size=8, alpha=0.3):
    """Legacy function - now uses LSB"""
    # Extract bytes and convert to array
    message_bytes = extract_message_rgb(stego_arr)
    
    # Reshape to match stego_arr shape
    h, w, c = stego_arr.shape
    payload_arr = np.frombuffer(message_bytes, dtype=np.uint8)
    
    # Resize to match original shape
    total_size = h * w * c
    if len(payload_arr) < total_size:
        payload_arr = np.pad(payload_arr, (0, total_size - len(payload_arr)), 'constant')
    elif len(payload_arr) > total_size:
        payload_arr = payload_arr[:total_size]
    
    return payload_arr.reshape((h, w, c))