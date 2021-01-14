from os import getenv
from flask import Flask, request, jsonify
from config import DevelopmentConfig, ProductionConfig


# Routes
from api import user_handler
# from api import home_handler
# from api import user_handler, handle_authorize
# from api import projects_handler
# from api import files_handler
# from api import threads_handler
# from api import payments_handler
# from api import settings_handler

# Database
from flask_sqlalchemy import SQLAlchemy

# Models
from models import db, ma
from models import User


# Init App
app = Flask(__name__, static_folder='static')

if getenv("FLASK_ENV") == "production":
    app.config.from_object(ProductionConfig())
else:
    app.config.from_object(DevelopmentConfig())

app.secret_key = getenv("APP_SECRET_KEY")

# Init DB
db.init_app(app)

# Init Marshmallow
ma.init_app(app)

# Actual endpoints
# app.register_blueprint(home_handler)
app.register_blueprint(user_handler)
# app.register_blueprint(projects_handler)
# app.register_blueprint(files_handler)
# app.register_blueprint(threads_handler)
# app.register_blueprint(payments_handler)
# app.register_blueprint(settings_handler)

# Jinja functions
# app.jinja_env.globals.update(convert_size=convert_size)
# app.jinja_env.globals.update(stripe_public_key=stripe_public_key)