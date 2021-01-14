from os import getenv
from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from config import ProductionConfig, DevelopmentConfig

from uuid import uuid4

# Models
from models import db
from models import User


app = Flask(__name__, static_folder='static')
if getenv("FLASK_ENV") == "production":
    app.config.from_object(ProductionConfig())
else:
    app.config.from_object(DevelopmentConfig())


db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def seed():
    pass


if __name__ == '__main__':
    # If Plan doesn't exist, we need to create the free plan.
    # Issue is, we need to hook into the init function?
    manager.run()