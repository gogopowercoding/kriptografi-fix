# models/file_model.py
from config import mysql

class FileModel:
    @staticmethod
    def save_file(sender_id, receiver_id, filename, filedata_b64):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO files (sender_id, receiver_id, filename, filedata)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, filename, filedata_b64))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_files_for(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT f.*, u.nama AS sender_name
            FROM files f JOIN users u ON f.sender_id = u.id
            WHERE f.receiver_id = %s
            ORDER BY f.date_sent DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows

    @staticmethod
    def get_file(file_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM files WHERE id = %s", (file_id,))
        row = cur.fetchone()
        cur.close()
        return row
