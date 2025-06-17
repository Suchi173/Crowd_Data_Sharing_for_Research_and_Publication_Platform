from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'professor', 'company'
    profile_image = db.Column(db.String(120), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Role-specific fields
    college = db.Column(db.String(120))  # For students and professors
    field = db.Column(db.String(120))  # For professors
    company_name = db.Column(db.String(120))  # For companies
    date_of_birth = db.Column(db.Date)  # For students and professors
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy='dynamic')
    collaborations = db.relationship('Collaboration', backref='collaborator', lazy='dynamic')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref=db.backref('user', uselist=False), lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    is_public = db.Column(db.Boolean, default=False)
    is_funding_enabled = db.Column(db.Boolean, default=False)  # Flag for funding eligibility
    funding_goal = db.Column(db.Float, nullable=True)  # Optional funding goal amount
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    collaborations = db.relationship('Collaboration', backref='document', lazy='dynamic')
    
    def __repr__(self):
        return f'<Document {self.title}>'


class Collaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    permission = db.Column(db.String(20), default='view')  # 'view', 'edit', 'comment'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Collaboration {self.user_id} on {self.document_id}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    related_document = db.relationship('Document', foreign_keys=[related_document_id])
    related_user = db.relationship('User', foreign_keys=[related_user_id], backref=db.backref('related_notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification for {self.user_id}>'


class Funding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    funder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Company providing funding
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text)  # Optional message from funder
    stripe_session_id = db.Column(db.String(255))  # Stripe checkout session ID
    
    # Relationships
    document = db.relationship('Document', backref=db.backref('funding_requests', lazy='dynamic'))
    def __repr__(self):
        return f'<Funding {self.amount} for document {self.document_id} by {self.funder_id}>'
