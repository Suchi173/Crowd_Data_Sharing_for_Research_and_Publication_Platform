import os
import logging
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
# Use PyMySQL as the MySQL connector for SQLAlchemy
# Only if the DATABASE_URL is MySQL
if os.environ.get('DATABASE_URL', '').startswith('mysql'):
    pymysql.install_as_MySQLdb()
    
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configure applications
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database
db.init_app(app)
migrate.init_app(app, db)

# Initialize login manager
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models
from models import User, Document, Notification, Collaboration

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Import routes
from routes import *

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
