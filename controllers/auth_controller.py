from flask import render_template, request, redirect, url_for, flash, session
import hashlib
from models.user_model import UserModel

def hash_blake2s(password):
    h = hashlib.blake2s()
    h.update(password.encode('utf-8'))
    return h.hexdigest()

def register():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        password = request.form['password']
        tgl_lahir = request.form['tgl_lahir']

        password_hash = hash_blake2s(password)
        UserModel.create_user(nama, email, password_hash, tgl_lahir)
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = UserModel.get_user_by_email(email)

        if user and user['password_hash'] == hash_blake2s(password):
            session['user_id'] = user['id']
            session['nama'] = user['nama']
            flash('Login berhasil!')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

def logout():
    session.clear()
    flash('Anda telah logout.')
    return redirect(url_for('login'))

def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', nama=session['nama'])
