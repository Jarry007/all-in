from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown
from flask_login import LoginManager
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class,ALL
from flask_ckeditor import CKEditor
from faker import Faker
from flask_cors import CORS

def creat_folder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        os.chmod(folder_path, os.O_RDWR)


APP_DIR=os.path.dirname(__file__)
STATIC_DIR=os.path.join(APP_DIR, 'static')


app = Flask(__name__)
app.debug=True
app.config['SECRET_KEY'] = 'jarry'

app.config.update(
    MAIL_DEBUG = True,
    MAIL_SERVER = 'smtp.qq.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL=True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME =os.environ.get('MAIL_USER'),
    MAIL_PASSWORD = os.environ.get('EMAIL_PWD'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    MAX_CONTENT_LENGTH = 2 * 1024 *1024
)
app.config['UPLOADS_RELATIVE'] = 'uploads'
app.config['UPLOADS_FOLDER'] = os.path.join(STATIC_DIR, app.config['UPLOADS_RELATIVE'])
app.config['UPLOADED_PHOTOS_DEST'] = app.config['UPLOADS_FOLDER']




db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
pagedown = PageDown(app)
loginmanager = LoginManager(app)
ck = CKEditor(app)
cors = CORS(app)
loginmanager.session_protection = 'strong'
loginmanager.login_view = 'user_login'

import apps.views
