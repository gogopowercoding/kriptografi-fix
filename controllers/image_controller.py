# controllers/image_controller.py
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.image_model import ImageModel
from models.user_model import UserModel
from utils.aes_utils import encrypt_aes_bytes, decrypt_aes_bytes
from lib import lsb_sequential_utils
from PIL import Image
import numpy as np
from flask import send_file
import io

image_bp = Blueprint('image_bp', __name__)
UPLOAD_FOLDER = 'static/uploads'

def save_image_array(arr, path):
    img = Image.fromarray(np.uint8(arr))
    img.save(path, format='PNG')  # force PNG for lossless

@image_bp.route('/send_image', methods=['GET','POST'])
def send_image():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    users = UserModel.get_all_users_except(session['user_id'])

    if request.method == 'POST':
        sender_id = session['user_id']
        receiver_id = request.form.get('receiver_id')
        hidden_text = request.form.get('hidden_text')
        image_file = request.files.get('image')

        if not image_file:
            flash('Pilih gambar terlebih dahulu!')
            return render_template('send_image.html', users=users)

        # Save uploaded cover image temporarily
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{image_file.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        try:
            # AES encrypt (returns IV || ciphertext) as bytes
            aes_payload = encrypt_aes_bytes(hidden_text)  # bytes (iv + ct)

            # Load cover image array
            cover_arr = lsb_sequential_utils.image_to_array_rgb(image_path)

            # Capacity check (capacity in bytes excludes 4 header bytes)
            max_capacity = lsb_sequential_utils.calculate_capacity(cover_arr)
            if len(aes_payload) > max_capacity:
                flash(f'Pesan terlalu panjang! Maksimal {max_capacity} bytes, pesan Anda {len(aes_payload)} bytes')
                return render_template('send_image.html', users=users)

            # Embed (will prefix message length automatically)
            stego_arr = lsb_sequential_utils.embed_message_rgb(cover_arr, aes_payload)

            # Save stego image
            stego_filename = f"stego_{uuid.uuid4().hex}.png"
            stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
            save_image_array(stego_arr, stego_path)

            # Save metadata only (do NOT save hidden bytes)
            ImageModel.save_image(sender_id, receiver_id, stego_path)

            # Optionally remove original uploaded cover to save space
            try:
                os.remove(image_path)
            except Exception:
                pass

            flash('Gambar dengan pesan rahasia berhasil dikirim!')
            return redirect(url_for('image_bp.send_image'))

        except Exception as e:
            flash(f'Error saat embedding: {str(e)}')
            return render_template('send_image.html', users=users)

    # GET
    return render_template('send_image.html', users=users)


@image_bp.route('/received_images')
def received_images():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user_id = session['user_id']
    images = ImageModel.get_received_images(user_id)

    decrypted_messages = []
    for img in images:
        try:
            # Load stego image from path in DB
            stego_arr = lsb_sequential_utils.image_to_array_rgb(img['image_path'])

            # Extract payload bytes (header removed by function, returns bytes of AES payload)
            extracted = lsb_sequential_utils.extract_message_rgb(stego_arr)

            # Decrypt AES payload (expects iv + ct)
            decrypted_text = decrypt_aes_bytes(extracted)

            decrypted_messages.append({
                'sender_name': img['sender_name'],
                'image_path': img['image_path'],
                'message': decrypted_text,
                'date_sent': img['date_sent']
            })
        except Exception as e:
            decrypted_messages.append({
                'sender_name': img.get('sender_name'),
                'image_path': img.get('image_path'),
                'message': f"[Error: {str(e)}]",
                'date_sent': img.get('date_sent')
            })

    return render_template('received_images.html', images=decrypted_messages)

@image_bp.route('/download_message/<path:image_path>')
def download_message(image_path):
    try:
        # Load stego image again (absolute path)
        stego_arr = lsb_sequential_utils.image_to_array_rgb(image_path)

        # Extract payload (iv + ciphertext)
        extracted = lsb_sequential_utils.extract_message_rgb(stego_arr)

        # Decrypt AES
        decrypted_text = decrypt_aes_bytes(extracted)

    except Exception as e:
        decrypted_text = f"[Error: {str(e)}]"

    # Buat file TXT dalam memory
    buffer = io.BytesIO()
    buffer.write(decrypted_text.encode('utf-8'))
    buffer.seek(0)

    # Nama file
    filename = "secret_message.txt"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain"
    )
