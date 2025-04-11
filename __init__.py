from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'segredo'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'linkteca.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from linkteca.routes import main
    app.register_blueprint(main)

    with app.app_context():
        if not os.path.exists(os.path.join(app.instance_path, 'linkteca.db')):
            db.create_all()

    return app
