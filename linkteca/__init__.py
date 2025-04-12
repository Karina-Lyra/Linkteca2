from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'segredo'

    # Banco de dados na pasta instance
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'linkteca.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Garante que a pasta instance existe
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
