from flask import Flask
from config import init_app, AES_MASTER_KEY, mysql
from controllers import auth_controller, message_controller, image_controller
from lib import aes_utils
from controllers.message_controller import message_bp
from controllers.file_controller import file_bp
from controllers.image_controller import image_bp 

app = Flask(__name__)
app.secret_key = 'supersecretkey2'  # ubah di produksi

# Inisialisasi koneksi MySQL
init_app(app)

# Inisialisasi AES
aes_utils.init(AES_MASTER_KEY)

# Registrasi route / blueprint


app.add_url_rule('/', view_func=auth_controller.login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=auth_controller.register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=auth_controller.dashboard)
app.add_url_rule('/logout', view_func=auth_controller.logout)

app.register_blueprint(message_bp)
app.register_blueprint(file_bp)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    app.run(debug=True)
