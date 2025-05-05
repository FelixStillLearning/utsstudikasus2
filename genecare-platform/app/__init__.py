from flask import Flask, render_template, redirect, url_for
from app.extensions import db, login_manager  # Import login_manager
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)  # Initialize login_manager
    
    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.auth.models import User
        return User.query.get(int(user_id))
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Initialize blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api.routes import api_bp
    # Register API blueprint with the /api prefix
    app.register_blueprint(api_bp, url_prefix='/api')

    # Add a route for the root URL
    @app.route('/')
    def home():
        print("Home route accessed")  # Debug statement
        return render_template('index.html')

    # Add a route for '/genecare-platform'
    @app.route('/genecare-platform')
    def genecare_platform():
        return render_template('index.html')
        
    # Add redirect for recommendations
    @app.route('/recommendations')
    def recommendations_redirect():
        return redirect(url_for('auth.recommendations'))

    # Initialize repository directly here
    initialize_repository()
    
    return app

# Moved initialize_repository function definition here but keep it unchanged
def initialize_repository():
    from app.data.repositories import HealthDataRepository
    from app.api.routes import set_repository

    repository = HealthDataRepository(db.session)
    set_repository(repository)