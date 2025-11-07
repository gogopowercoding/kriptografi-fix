# controllers/message_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import UserModel
from models.message_model import MessageModel
from lib import caesar_fsr, aes_utils
import config

message_bp = Blueprint('message_bp', __name__)

@message_bp.route('/send_message', methods=['GET','POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    users = UserModel.get_all_users_except(session['user_id'])
    if request.method == 'POST':
        receiver_id = int(request.form['receiver_id'])
        title = request.form.get('title','(no title)')
        plaintext = request.form['message']
        # derive passphrase: combine sender and receiver and master key
        passphrase = f"{session['user_id']}:{receiver_id}:{config.AES_MASTER_KEY[:8].decode(errors='ignore')}"
        cipher_bytes = caesar_fsr.encrypt_text(plaintext, passphrase)
        # encrypt with AES for DB storage (base64)
        payload_b64 = aes_utils.encrypt_aes(cipher_bytes)
        MessageModel.send_text(session['user_id'], receiver_id, title, payload_b64)
        flash('Pesan terenkripsi terkirim.')
        return redirect(url_for('message_bp.inbox'))
    return render_template('send_message.html', users=users)

@message_bp.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    rows = MessageModel.get_inbox(session['user_id'])
    return render_template('inbox.html', messages=rows)

@message_bp.route('/view_message/<int:message_id>')
def view_message(message_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    msg = MessageModel.get_message_by_id(message_id)
    if not msg:
        flash('Pesan tidak ditemukan.')
        return redirect(url_for('message_bp.inbox'))
    try:
        cipher_bytes = aes_utils.decrypt_aes(msg['encrypted_message'])
        passphrase = f"{msg['sender_id']}:{msg['receiver_id']}:{config.AES_MASTER_KEY[:8].decode(errors='ignore')}"
        # note: when decrypting we used sender:receiver same derivation as encrypt
        # but here receiver_id is current user; ensure consistent derivation rule
        # we'll derive passphrase using sender_id:receiver_id as in encryption
        passphrase = f"{msg['sender_id']}:{msg['receiver_id']}:{config.AES_MASTER_KEY[:8].decode(errors='ignore')}"
        plaintext = caesar_fsr.decrypt_text(cipher_bytes, passphrase)
    except Exception as e:
        plaintext = f"[Error dekripsi: {str(e)}]"
    return render_template('view_message.html', message=msg, decrypted_message=plaintext)
