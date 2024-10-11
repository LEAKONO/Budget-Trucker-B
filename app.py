from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_cors import CORS  
from config import Config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
session = Session()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    session.init_app(app)
    jwt.init_app(app)
    
    CORS(app)
    
    from routes import bp_routes
    from auth import bp_auth
    app.register_blueprint(bp_routes, url_prefix='/routes')
    app.register_blueprint(bp_auth, url_prefix='/auth')

    return app

