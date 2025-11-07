# controllers/file_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models.user_model import UserModel
from models.file_model import FileModel
from lib import twofish_utils, aes_utils
import config, base64, os, tempfile


file_bp = Blueprint('file_bp', __name__)

# derive twofish key from master AES key (prototype)
TWOFISH_KEY = config.AES_MASTER_KEY

@file_bp.route('/send_file', methods=['GET','POST'])
def send_file():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    users = UserModel.get_all_users_except(session['user_id'])
    if request.method == 'POST':
        f = request.files.get('file')
        receiver_id = int(request.form['receiver_id'])
        if not f:
            flash('Pilih file terlebih dahulu.')
            return redirect(url_for('file_bp.send_file'))
        data = f.read()
        # limit size (example 10 MB)
        if len(data) > 10 * 1024 * 1024:
            flash('Ukuran file terlalu besar (maks 10 MB).')
            return redirect(url_for('file_bp.send_file'))
        # encrypt with Twofish
        tf_ct = twofish_utils.encrypt_bytes(TWOFISH_KEY, data)
        # then encrypt Twofish ciphertext with AES for DB (base64)
        payload_b64 = aes_utils.encrypt_aes(tf_ct)
        FileModel.save_file(session['user_id'], receiver_id, f.filename, payload_b64)
        flash('File terenkripsi terkirim.')
        return redirect(url_for('file_bp.received_files'))
    return render_template('send_file.html', users=users)

@file_bp.route('/received_files')
def received_files():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    rows = FileModel.get_files_for(session['user_id'])
    return render_template('received_files.html', files=rows)

from flask import Response
import os

@file_bp.route('/download_file/<int:file_id>')
def download_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    rec = FileModel.get_file(file_id)
    if not rec:
        flash('File tidak ditemukan.')
        return redirect(url_for('file_bp.received_files'))

    try:
        tf_ct = aes_utils.decrypt_aes(rec['filedata'])
        plaintext = twofish_utils.decrypt_bytes(TWOFISH_KEY, tf_ct)
    except Exception as e:
        flash('Gagal dekripsi file: ' + str(e))
        return redirect(url_for('file_bp.received_files'))

    # write ke temp file
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(plaintext)
    tmp.flush()
    tmp.close()

    filename = rec['filename'] or 'download.bin'

    # baca isi file dan buat Response manual
    with open(tmp.name, 'rb') as f:
        data = f.read()
    os.remove(tmp.name)  # hapus file sementara

    resp = Response(data, mimetype='application/octet-stream')
    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp
