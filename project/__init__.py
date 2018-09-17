import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)


app_settings = os.getenv(
    'APP_SETTINGS',
    'project.settings.DevelopmentConfig'
)
app.config.from_object(app_settings)
app.url_map.strict_slashes = False

CORS(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)


from .api import register_blueprints, register_error_handlers # noqa

register_blueprints()
register_error_handlers()
