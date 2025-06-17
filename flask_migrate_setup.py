from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/research_platform')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import your models
from models import User, Document, Collaboration, Notification, Funding

if __name__ == '__main__':
    # Create all tables
    with app.app_context():
        db.create_all()
        print('Database tables created.')
