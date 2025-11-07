import os
from config import mysql

class ImageModel:
    @staticmethod
    def save_image(sender_id, receiver_id, image_path, hidden_message_encrypted):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO images (sender_id, receiver_id, image_path, hidden_message)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, image_path, hidden_message_encrypted))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_received_images(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT images.*, users.nama AS sender_name
            FROM images
            JOIN users ON images.sender_id = users.id
            WHERE receiver_id = %s
            ORDER BY date_sent DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows
