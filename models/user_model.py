from config import mysql

class UserModel:
    @staticmethod
    def create_user(nama, email, password_hash, tgl_lahir):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (nama, email, password_hash, tgl_lahir)
            VALUES (%s, %s, %s, %s)
        """, (nama, email, password_hash, tgl_lahir))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_user_by_email(email):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()
        return user

    # di models/user_model.py (tambahkan)
    @staticmethod
    def get_all_users_except(user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nama FROM users WHERE id != %s", (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows
