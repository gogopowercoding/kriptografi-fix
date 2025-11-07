import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.image_model import ImageModel
from utils.aes_utils import encrypt_aes_bytes, decrypt_aes_bytes
from lib import lsb_sequential_utils  # Sekarang menggunakan LSB Sequential
from PIL import Image
import numpy as np

image_bp = Blueprint('image_bp', __name__)

UPLOAD_FOLDER = 'static/uploads'

def save_image_array(arr, path):
    """Simpan array RGB sebagai gambar"""
    img = Image.fromarray(np.uint8(arr))
    img.save(path, quality=100)  # Quality 100 untuk menjaga data LSB

@image_bp.route('/send_image', methods=['GET', 'POST'])
def send_image():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    if request.method == 'POST':
        sender_id = session['user_id']
        receiver_id = request.form['receiver_id']
        hidden_text = request.form['hidden_text']
        image_file = request.files.get('image')

        if not image_file:
            flash('Pilih gambar terlebih dahulu!')
            return redirect(url_for('image_bp.send_image'))

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{image_file.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        try:
            # Enkripsi pesan → hasil bytes
            encrypted_hidden_bytes = encrypt_aes_bytes(hidden_text)
            
            # Load cover image
            cover_arr = lsb_sequential_utils.image_to_array_rgb(image_path)
            
            # Hitung kapasitas maksimal (LSB Sequential)
            max_capacity = lsb_sequential_utils.calculate_capacity(cover_arr)
            
            # Cek apakah pesan muat
            if len(encrypted_hidden_bytes) > max_capacity:
                flash(f'Pesan terlalu panjang! Maksimal {max_capacity} bytes, pesan Anda {len(encrypted_hidden_bytes)} bytes')
                return redirect(url_for('image_bp.send_image'))

            # Embed menggunakan LSB Sequential
            stego_arr = lsb_sequential_utils.embed_message_rgb(cover_arr, encrypted_hidden_bytes)

            # Simpan stego image (gunakan PNG untuk lossless)
            stego_filename = f"stego_{uuid.uuid4().hex}.png"
            stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
            save_image_array(stego_arr, stego_path)

            # Simpan metadata di DB
            ImageModel.save_image(sender_id, receiver_id, stego_path, encrypted_hidden_bytes)

            flash('Gambar dengan pesan rahasia berhasil dikirim!')
            return redirect(url_for('image_bp.send_image'))
        
        except Exception as e:
            flash(f'Error saat embedding: {str(e)}')
            return redirect(url_for('image_bp.send_image'))

    return render_template('send_image.html')


@image_bp.route('/received_images')
def received_images():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user_id = session['user_id']
    images = ImageModel.get_received_images(user_id)

    decrypted_messages = []
    for img in images:
        try:
            # Load stego image
            stego_arr = lsb_sequential_utils.image_to_array_rgb(img['image_path'])
            
            # Extract message bytes menggunakan LSB Sequential
            extracted_bytes = lsb_sequential_utils.extract_message_rgb(stego_arr)

            # Decrypt menggunakan AES
            decrypted_text = decrypt_aes_bytes(extracted_bytes)

            decrypted_messages.append({
                'sender_name': img['sender_name'],
                'image_path': img['image_path'],
                'message': decrypted_text,
                'date_sent': img['date_sent']
            })
        except Exception as e:
            decrypted_messages.append({
                'sender_name': img['sender_name'],
                'image_path': img['image_path'],
                'message': f"[Error: {str(e)}]",
                'date_sent': img['date_sent']
            })

    return render_template('received_images.html', images=decrypted_messages)