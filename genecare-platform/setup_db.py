from app import create_app
from app.extensions import db  # Import db langsung dari app.extensions
import os

def setup_database():
    # Get the path to the database file
    app = create_app()
    with app.app_context():
        # Drop all existing tables and recreate them
        db.drop_all()
        db.create_all()
        print("Database tables recreated successfully!")

if __name__ == "__main__":
    setup_database()