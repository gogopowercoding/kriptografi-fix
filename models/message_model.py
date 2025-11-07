# models/message_model.py
from config import mysql

class MessageModel:
    @staticmethod
    def send_text(sender_id, receiver_id, title, encrypted_message_b64):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, title, encrypted_message)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, title, encrypted_message_b64))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_inbox(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.*, u.nama AS sender_name
            FROM messages m JOIN users u ON m.sender_id = u.id
            WHERE m.receiver_id = %s
            ORDER BY m.date_sent DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows

    @staticmethod
    def get_message_by_id(message_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.*, u.nama AS sender_name
            FROM messages m JOIN users u ON m.sender_id = u.id
            WHERE m.id = %s
        """, (message_id,))
        row = cur.fetchone()
        cur.close()
        return row
