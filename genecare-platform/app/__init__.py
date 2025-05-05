from flask import Flask, render_template
from app.extensions import db  # Import db at the module level
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Initialize blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api.routes import api_bp
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

    # Initialize repository directly here
    initialize_repository()
    
    return app

# Moved initialize_repository function definition here but keep it unchanged
def initialize_repository():
    from app.data.repositories import HealthDataRepository
    from app.api.routes import set_repository

    repository = HealthDataRepository(db.session)
    set_repository(repository)