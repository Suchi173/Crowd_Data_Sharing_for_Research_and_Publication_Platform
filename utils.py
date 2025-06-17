import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, flash
from flask_login import current_user
from models import Notification, db

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, upload_folder=None):
    """Save a file to the server with a secure unique filename"""
    if upload_folder is None:
        upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Make sure the upload folder exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Generate a secure filename with a UUID to prevent collisions
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    filename = f"{uuid.uuid4().hex}.{extension}" if extension else f"{uuid.uuid4().hex}"
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    return filename, file_path

def get_file_size(file_path):
    """Get the size of a file in bytes"""
    return os.path.getsize(file_path)

def get_file_type(filename):
    """Get the file extension from a filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def format_date(date):
    """Format a date object to string"""
    if date:
        return date.strftime('%Y-%m-%d')
    return None

def create_notification(user_id, content, related_document_id=None, related_user_id=None):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        content=content,
        related_document_id=related_document_id,
        related_user_id=related_user_id
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def has_permission(user, document, permission_level):
    """Check if a user has a specific permission on a document"""
    # If user is the owner, they have all permissions
    if document.user_id == user.id:
        return True
    
    # Check if there's a collaboration with the required permission
    collaboration = next(
        (collab for collab in document.collaborations if collab.user_id == user.id),
        None
    )
    
    if not collaboration:
        return False
    
    # Define permission hierarchy
    permission_hierarchy = {
        'view': ['view', 'comment', 'edit'],
        'comment': ['comment', 'edit'],
        'edit': ['edit']
    }
    
    return collaboration.permission in permission_hierarchy.get(permission_level, [])
