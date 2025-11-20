# controllers/message_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import UserModel
from models.message_model import MessageModel
from lib import aes_utils
from lib.des_utils import encrypt_des, decrypt_des
import config

message_bp = Blueprint('message_bp', __name__)

# SEND MESSAGE (ENCRYPT)
@message_bp.route('/send_message', methods=['GET','POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    users = UserModel.get_all_users_except(session['user_id'])

    if request.method == 'POST':

        receiver_id = int(request.form['receiver_id'])
        title = request.form['title']
        plaintext = request.form['message']

        caesar_key = request.form['caesar_key']
        des_key = request.form['des_key']

        # ---------- VALIDASI ----------
        if not caesar_key.isdigit():
            flash("Kunci Caesar HARUS berupa angka.")
            return redirect(url_for('message_bp.send_message'))

        if len(des_key) != 8:
            flash("Kunci DES HARUS 8 karakter.")
            return redirect(url_for('message_bp.send_message'))

        # ---------- SUPER ENCRYPTION ----------

        # 1) CAESAR (plaintext -> bytes)
        shift = int(caesar_key)
        caesar_bytes = bytes((ord(c) + shift) % 256 for c in plaintext)

        # 2) DES (bytes -> bytes)
        des_bytes = encrypt_des(caesar_bytes, des_key)   # FIXED

        # 3) AES (bytes -> base64 string)
        aes_cipher_b64 = aes_utils.encrypt_aes(des_bytes)

        # Simpan ke database
        MessageModel.send_text(
            session['user_id'],
            receiver_id,
            title,
            aes_cipher_b64
        )

        flash("Pesan terenkripsi terkirim. Kunci TIDAK disimpan.")
        return redirect(url_for('message_bp.inbox'))

    return render_template('send_message.html', users=users)


#= INBOX=
@message_bp.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    rows = MessageModel.get_inbox(session['user_id'])
    return render_template('inbox.html', messages=rows)


# ========= VIEW MESSAGE (DECRYPT ON DEMAND) ===========
@message_bp.route('/view_message/<int:message_id>', methods=['GET','POST'])
def view_message(message_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    msg = MessageModel.get_message_by_id(message_id)
    decrypted = None

    if request.method == "POST":

        caesar_key = request.form['caesar_key']
        des_key = request.form['des_key']

        if not caesar_key.isdigit():
            decrypted = "[Error: Kunci Caesar harus angka]"
            return render_template("view_message.html", message=msg, decrypted_message=decrypted)

        if len(des_key) != 8:
            decrypted = "[Error: Kunci DES harus 8 karakter]"
            return render_template("view_message.html", message=msg, decrypted_message=decrypted)

        try:
            # 1) AES (base64 string → bytes DES)
            des_bytes = aes_utils.decrypt_aes(msg['encrypted_message'])

            # 2) DES (bytes → bytes Caesar)
            caesar_bytes = decrypt_des(des_bytes, des_key)

            # 3) Caesar (bytes → plaintext)
            shift = int(caesar_key)
            decrypted = "".join(chr((b - shift) % 256) for b in caesar_bytes)

        except Exception as e:
            decrypted = f"[Error Dekripsi: {str(e)}]"

    return render_template("view_message.html", message=msg, decrypted_message=decrypted)
