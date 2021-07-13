from flask import Flask
from config import Config
from flask_login import LoginManager
import connectDB as cn

# ...

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from app import routes