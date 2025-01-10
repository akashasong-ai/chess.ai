from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Move config import inside function to avoid circular imports
    from config import Config
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Import routes after db is initialized
        from app.routes import main
        app.register_blueprint(main)

    return app