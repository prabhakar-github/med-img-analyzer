from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db
from app.models import Operator


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Operator.query.get(int(user_id))
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.upload.routes import upload_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    # Root route redirects to login or dashboard
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('upload.dashboard'))
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # Set maximum content length for file uploads
    app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_CONTENT_LENGTH']
    
    return app