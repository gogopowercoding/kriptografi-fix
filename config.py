import os
from flask_mysqldb import MySQL

mysql = MySQL()

DEFAULT_AES_KEY = b"THIS_IS_DEMO_KEY_MUST_CHANGE_32BYTE!!"[:32]
AES_MASTER_KEY = os.environ.get("SECUREVAULT_AES_KEY", "").encode() or DEFAULT_AES_KEY

def init_app(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'securevault'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)
