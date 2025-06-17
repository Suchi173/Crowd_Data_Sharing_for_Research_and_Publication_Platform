import os
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

from app import app, db
from forms import (
    RoleSelectionForm, LoginForm, RegistrationForm, UpdateProfileForm,
    UploadDocumentForm, EditDocumentForm, CollaborationForm, FundingForm
)
from models import User, Document, Notification, Collaboration, Funding
from utils import allowed_file, save_file, get_file_size, get_file_type, create_notification, has_permission


@app.route('/')
def index():
    """Home page route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/role-selection', methods=['GET', 'POST'])
def role_selection():
    """Role selection page for registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RoleSelectionForm()
    
    if form.validate_on_submit():
        role = request.form.get('role')
        if role in ['student', 'professor', 'company']:
            return redirect(url_for('register', role=role))
        else:
            flash('Invalid role selected.', 'danger')
    
    return render_template('role_selection.html', form=form)


@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    """Registration page for specific roles."""
    if role not in ['student', 'professor', 'company']:
        return redirect(url_for('role_selection'))
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    # Remove irrelevant fields based on role
    if role == 'student':
        del form.field
        del form.company_name
    elif role == 'professor':
        del form.company_name
    elif role == 'company':
        del form.college
        del form.date_of_birth
        del form.field
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=role
        )
        user.set_password(form.password.data)
        
        # Set role-specific fields
        if role == 'student' or role == 'professor':
            user.college = form.college.data
            user.date_of_birth = form.date_of_birth.data
        
        if role == 'professor':
            user.field = form.field.data
        
        if role == 'company':
            user.company_name = form.company_name.data
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, role=role)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """User logout."""
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    # Import necessary modules
    from sqlalchemy import func
    user_documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.uploaded_at.desc()).all()
    
    # Get documents shared with the user
    collaborations = Collaboration.query.filter_by(user_id=current_user.id).all()
    shared_documents = [collab.document for collab in collaborations]
    
    # Get recent notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get funding-eligible documents for company users
    funding_eligible_documents = None
    if current_user.role == 'company':
        # Find documents that are public, have funding enabled, and don't belong to the current user
        funding_eligible_documents = Document.query.join(User).\
            filter(Document.is_public == True).\
            filter(Document.is_funding_enabled == True).\
            filter(Document.user_id != current_user.id).\
            filter(User.role.in_(['student', 'professor'])).\
            order_by(Document.uploaded_at.desc()).limit(5).all()
    
    
    return render_template(
        'dashboard.html', 
        user_documents=user_documents, 
        shared_documents=shared_documents,
        notifications=notifications,
        funding_eligible_documents=funding_eligible_documents,
        Document=Document,
        func=func,
        Funding=Funding,
        User=User
    )
    


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    # Remove irrelevant fields based on role
    if current_user.role == 'student':
        del form.field
        del form.company_name
    elif current_user.role == 'professor':
        del form.company_name
    elif current_user.role == 'company':
        del form.college
        del form.field
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if current_user.role == 'student' or current_user.role == 'professor':
            current_user.college = form.college.data
        
        if current_user.role == 'professor':
            current_user.field = form.field.data
        
        if current_user.role == 'company':
            current_user.company_name = form.company_name.data
        
        # Handle profile image upload
        if form.profile_image.data:
            try:
                filename, file_path = save_file(form.profile_image.data, 'static/uploads')
                current_user.profile_image = filename
            except Exception as e:
                flash(f'Error uploading profile image: {str(e)}', 'danger')
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
        if current_user.role == 'student' or current_user.role == 'professor':
            form.college.data = current_user.college
        
        if current_user.role == 'professor':
            form.field.data = current_user.field
        
        if current_user.role == 'company':
            form.company_name.data = current_user.company_name
    
    # Get recent documents for the profile page
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.uploaded_at.desc()).limit(5).all()
    
    return render_template('profile.html', form=form, documents=documents, Document=Document, User=User)


@app.route('/upload-document', methods=['GET', 'POST'])
@login_required
def upload_document():
    """Upload a new document."""
    form = UploadDocumentForm()
    
    if form.validate_on_submit():
        if form.document.data and allowed_file(form.document.data.filename):
            try:
                # Save the file
                filename, file_path = save_file(form.document.data, 'static/uploads/documents')
                
                # Create document record
                document = Document(
                    title=form.title.data,
                    description=form.description.data,
                    file_path=filename,
                    file_type=get_file_type(form.document.data.filename),
                    file_size=get_file_size(file_path),
                    is_public=form.is_public.data,
                    user_id=current_user.id,
                    # Add funding options
                    is_funding_enabled=form.is_funding_enabled.data if current_user.role in ['student', 'professor'] else False,
                    funding_goal=float(form.funding_goal.data) if form.funding_goal.data and form.is_funding_enabled.data else None
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Your document has been uploaded!', 'success')
                return redirect(url_for('dashboard'))
            
            except Exception as e:
                flash(f'Error uploading document: {str(e)}', 'danger')
        else:
            flash('Invalid file type. Please upload a valid document.', 'danger')
    
    return render_template('upload_document.html', form=form, Document=Document, User=User)



@app.route('/document/<int:document_id>')
@login_required
def view_document(document_id):
    """View a document."""
    document = Document.query.get_or_404(document_id)
    
    # Check if user has permission to view
    if not document.is_public and document.user_id != current_user.id:
        if not has_permission(current_user, document, 'view'):
            abort(403)
    
    # Get collaborators
    collaborators = User.query.join(Collaboration).filter(
        Collaboration.document_id == document.id
    ).all()
    
    # Check for funding success message
    funding_success = request.args.get('funding_success') == 'true'
    funding_id = request.args.get('funding_id')
    
    if funding_success and funding_id and current_user.role == 'company':
        funding = Funding.query.get(funding_id)
        if funding and funding.funder_id == current_user.id:
            flash(f'Thank you for funding this project with ${funding.amount:,.2f}! Your payment is being processed.', 'success')
    
    # Check for funding cancellation
    funding_canceled = request.args.get('funding_canceled') == 'true'
    if funding_canceled and current_user.role == 'company':
        flash('Funding process was canceled. You can try again when you are ready.', 'info')
    
    return render_template('document_view.html', document=document, collaborators=collaborators, Document=Document, User=User, Funding=Funding)


@app.route('/document/<int:document_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(document_id):
    """Edit a document."""
    document = Document.query.get_or_404(document_id)
    
    # Check if user has permission to edit
    if document.user_id != current_user.id and not has_permission(current_user, document, 'edit'):
        abort(403)
    
    form = EditDocumentForm()
    
    if form.validate_on_submit():
        document.title = form.title.data
        document.description = form.description.data
        document.is_public = form.is_public.data
        document.last_modified = datetime.utcnow()
        
        # Update funding options if user is student or professor
        if current_user.role in ['student', 'professor']:
            document.is_funding_enabled = form.is_funding_enabled.data
            document.funding_goal = float(form.funding_goal.data) if form.funding_goal.data and form.is_funding_enabled.data else None
        
        
        db.session.commit()
        
        flash('Document has been updated!', 'success')
        return redirect(url_for('view_document', document_id=document.id))
    
    elif request.method == 'GET':
        form.title.data = document.title
        form.description.data = document.description
        form.is_public.data = document.is_public
        
        # Populate funding fields if applicable
        if hasattr(form, 'is_funding_enabled'):
            form.is_funding_enabled.data = document.is_funding_enabled
        if hasattr(form, 'funding_goal') and document.funding_goal:
            form.funding_goal.data = str(document.funding_goal)
    
        
    return render_template('edit_document.html', form=form, document=document, Document=Document, User=User)


@app.route('/document/<int:document_id>/download')
@login_required
def download_document(document_id):
    """Download a document."""
    document = Document.query.get_or_404(document_id)
    
    # Check if user has permission to download
    if not document.is_public and document.user_id != current_user.id:
        if not has_permission(current_user, document, 'view'):
            abort(403)
    
    return send_from_directory(
        os.path.join(app.root_path, 'static/uploads/documents'),
        document.file_path,
        as_attachment=True,
        download_name=f"{document.title.replace('{', '').replace('}', '')}.{document.file_type}"
    )



@app.route('/document/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """Delete a document."""
    document = Document.query.get_or_404(document_id)
    
    # Only the owner can delete
    if document.user_id != current_user.id:
        abort(403)
    
    # Delete the file
    try:
        os.remove(os.path.join(app.root_path, 'static/uploads/documents', document.file_path))
    except Exception as e:
        # If file doesn't exist, continue with deletion from DB
        app.logger.error(f"Error removing file: {str(e)}")
        pass
    
    try:
        # Delete related collaborations
        Collaboration.query.filter_by(document_id=document.id).delete()
        
        # Delete related notifications
        Notification.query.filter_by(related_document_id=document.id).delete()
        
        # Delete the document record
        db.session.delete(document)
        db.session.commit()
        
        flash('Document has been deleted!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting document: {str(e)}")
        flash('An error occurred while deleting the document. Please try again.', 'danger')
        return redirect(url_for('dashboard'))



@app.route('/document/<int:document_id>/collaborate', methods=['GET', 'POST'])
@login_required
def collaborate(document_id):
    """Add collaborators to a document."""
    document = Document.query.get_or_404(document_id)
    
    # Only the owner can add collaborators
    if document.user_id != current_user.id:
        abort(403)
    
    form = CollaborationForm()
    
    if form.validate_on_submit():
        collaborator = User.query.filter_by(email=form.collaborator_email.data).first()
        
        # Check if user is already a collaborator
        existing_collab = Collaboration.query.filter_by(
            document_id=document.id,
            user_id=collaborator.id
        ).first()
        
        if existing_collab:
            existing_collab.permission = form.permission.data
            db.session.commit()
            flash(f'Collaboration with {collaborator.username} has been updated!', 'success')
        else:
            # Create new collaboration
            collaboration = Collaboration(
                document_id=document.id,
                user_id=collaborator.id,
                permission=form.permission.data
            )
            
            db.session.add(collaboration)
            db.session.commit()
            
            # Create notification for the collaborator
            create_notification(
                collaborator.id,
                f"{current_user.username} has shared a document '{document.title.replace('{', '').replace('}', '')}' with you.",
                related_document_id=document.id,
                related_user_id=current_user.id
            )
            
            flash(f'Document has been shared with {collaborator.username}!', 'success')
        
        return redirect(url_for('view_document', document_id=document.id))
    
    # Get existing collaborators
    collaborations = Collaboration.query.filter_by(document_id=document.id).all()
    collaborators = [(collab, User.query.get(collab.user_id)) for collab in collaborations]
    
    return render_template('collaborate.html', form=form, document=document, collaborators=collaborators, Document=Document, User=User)



@app.route('/document/<int:document_id>/remove-collaborator/<int:user_id>', methods=['POST'])
@login_required
def remove_collaborator(document_id, user_id):
    """Remove a collaborator from a document."""
    document = Document.query.get_or_404(document_id)
    
    # Only the owner can remove collaborators
    if document.user_id != current_user.id:
        abort(403)
    
    collaboration = Collaboration.query.filter_by(
        document_id=document.id,
        user_id=user_id
    ).first_or_404()
    
    collaborator = User.query.get(user_id)
    
    db.session.delete(collaboration)
    db.session.commit()
    
    # Create notification for the collaborator
    create_notification(
        collaborator.id,
        f"{current_user.username} has removed you from the document '{document.title.replace('{', '').replace('}', '')}'.",
        related_document_id=document.id,
        related_user_id=current_user.id
    )
    
    flash(f'Collaborator has been removed!', 'success')
    return redirect(url_for('collaborate', document_id=document.id))



@app.route('/notifications')
@login_required
def notifications():
    """User notifications page."""
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    read_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=True
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template(
        'notifications.html',
        unread_notifications=unread_notifications,
        read_notifications=read_notifications,
        Document=Document,
        User=User
    )



@app.route('/notification/<int:notification_id>/mark-read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        abort(403)
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('notifications'))



@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({Notification.is_read: True})
    
    db.session.commit()
    
    flash('All notifications marked as read!', 'success')
    return redirect(url_for('notifications'))



@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('404.html'), 404



@app.errorhandler(403)
def forbidden(e):
    """403 error handler."""
    return render_template('403.html'), 403


@app.route('/document/<int:document_id>/fund', methods=['GET', 'POST'])
@login_required
def fund_project(document_id):
    """Fund a project/document."""
    import stripe
    import os
    import logging
    
    # Add more detailed logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.info(f"Starting fund_project for document_id={document_id}")
    
    # Ensure we have the Stripe key
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_key:
        app.logger.error("STRIPE_SECRET_KEY is not set in environment variables")
        flash('Payment processing is unavailable. Please contact the administrator.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Set the Stripe API key
    stripe.api_key = stripe_key
    app.logger.info("Stripe API key set successfully")
    
    # Only companies can fund projects
    if current_user.role != 'company':
        app.logger.warning(f"User {current_user.id} with role {current_user.role} attempted to fund a project")
        flash('Only companies can fund research projects.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        document = Document.query.get_or_404(document_id)
        app.logger.info(f"Found document: {document.id} - {document.title}")
        
        # Check if document is eligible for funding
        if not document.is_funding_enabled:
            app.logger.warning(f"Document {document.id} is not enabled for funding")
            flash('This project is not open for funding.', 'danger')
            return redirect(url_for('view_document', document_id=document.id))
        
        # Get document owner
        owner = User.query.get(document.user_id)
        if not owner:
            app.logger.error(f"Owner (user_id={document.user_id}) not found for document {document.id}")
            flash('Document owner information could not be retrieved.', 'danger')
            return redirect(url_for('dashboard'))
            
        app.logger.info(f"Document owner: {owner.id} - {owner.username}")
        
        form = FundingForm()
        
        if form.validate_on_submit():
            app.logger.info("Form submitted and validated")
            try:
                amount = float(form.amount.data)
                app.logger.info(f"Funding amount: ${amount}")
                
                if amount <= 0:
                    flash('Funding amount must be greater than zero.', 'danger')
                    return render_template('fund_project.html', form=form, document=document, owner=owner)
                
                # Create funding record
                funding = Funding(
                    document_id=document.id,
                    funder_id=current_user.id,
                    amount=amount,
                    message=form.message.data
                )
                
                # Save funding record first so we have an ID to reference
                db.session.add(funding)
                db.session.commit()
                app.logger.info(f"Created funding record with ID: {funding.id}")
                
                try:
                    # Get domain for success/cancel URLs
                    YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', request.host)
                    if not YOUR_DOMAIN.startswith('http'):
                        YOUR_DOMAIN = f"https://{YOUR_DOMAIN}"
                    
                    app.logger.info(f"Using domain: {YOUR_DOMAIN}")
                    
                    # Create Stripe checkout session
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': f'Funding for {document.title}',
                                    'description': f'Provided by {current_user.company_name or current_user.username}',
                                },
                                'unit_amount': int(amount * 100),  # Convert to cents
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=f"{YOUR_DOMAIN}{url_for('view_document', document_id=document.id)}?funding_success=true&funding_id={funding.id}",
                        cancel_url=f"{YOUR_DOMAIN}{url_for('fund_project', document_id=document.id)}?funding_canceled=true",
                        metadata={
                            'funding_id': funding.id,
                            'document_id': document.id,
                            'funder_id': current_user.id,
                        },
                    )
                    
                    app.logger.info(f"Created Stripe checkout session: {checkout_session.id}")
                    
                    # Save checkout session ID to funding record
                    funding.stripe_session_id = checkout_session.id
                    db.session.commit()
                    
                    # Create notification for the document owner
                    create_notification(
                        owner.id,
                        f"{current_user.username} {' from ' + current_user.company_name if current_user.company_name else ''} has initiated funding for your project '{document.title}' with ${amount:,.2f}.",
                        related_document_id=document.id,
                        related_user_id=current_user.id
                    )
                    
                    app.logger.info(f"Redirecting to Stripe checkout: {checkout_session.url}")
                    # Redirect to Stripe checkout
                    return redirect(checkout_session.url)
                    
                except Exception as e:
                    # Handle errors with Stripe
                    app.logger.error(f"Stripe error: {str(e)}")
                    flash(f'An error occurred during payment processing: {str(e)}', 'danger')
                    return redirect(url_for('fund_project', document_id=document.id))
            
            except ValueError:
                app.logger.warning(f"Invalid amount entered: {form.amount.data}")
                flash('Please enter a valid amount.', 'danger')
        elif request.method == 'POST':
            app.logger.warning(f"Form validation failed. Errors: {form.errors}")
    except Exception as e:
        app.logger.error(f"Unexpected error in fund_project: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('fund_project.html', form=form, document=document, owner=owner)


@app.route('/dashboard/funded-projects')
@login_required
def funded_projects():
    """Show projects funded by the company."""
    import logging
    
    # Add more detailed logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.info(f"Starting funded_projects route for user: {current_user.id}")
    
    if current_user.role != 'company':
        app.logger.warning(f"User {current_user.id} with role {current_user.role} attempted to access funded projects")
        flash('Only companies can view funded projects.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Initialize empty dict
    funded_documents = {}
    
    try:
        # Get all funding records for the company
        app.logger.info(f"Fetching funding records for user {current_user.id}")
        fundings = Funding.query.filter_by(funder_id=current_user.id).order_by(Funding.created_at.desc()).all()
        app.logger.info(f"Found {len(fundings)} funding records")
        
        # Group funding by document
        for funding in fundings:
            try:
                app.logger.info(f"Processing funding ID: {funding.id} for document {funding.document_id}")
                
                document = Document.query.get(funding.document_id)
                if not document:
                    app.logger.warning(f"Document {funding.document_id} not found for funding {funding.id}")
                    continue
                
                owner = User.query.get(document.user_id)
                if not owner:
                    app.logger.warning(f"Owner not found for document {document.id}")
                    owner_name = "Unknown"
                else:
                    owner_name = owner.username
                
                app.logger.info(f"Found document: {document.title} by {owner_name}")
                
                if funding.document_id not in funded_documents:
                    funded_documents[funding.document_id] = {
                        'document': document,
                        'owner': owner,
                        'total_amount': 0,
                        'fundings': []
                    }
                
                funded_documents[funding.document_id]['total_amount'] += funding.amount
                funded_documents[funding.document_id]['fundings'].append(funding)
                
            except Exception as e:
                app.logger.error(f"Error processing funding {funding.id}: {str(e)}")
    
    except Exception as e:
        app.logger.error(f"Error in funded_projects route: {str(e)}")
        flash("There was an error loading your funded projects. Please try again later.", "danger")
    
    app.logger.info(f"Rendering funded_projects template with {len(funded_documents)} documents")
    return render_template('funded_projects.html', funded_documents=funded_documents, Document=Document, User=User, Funding=Funding)


@app.route('/dashboard/my-project-funding')
@login_required
def my_project_funding():
    """Show funding received for student/professor projects."""
    # Import necessary modules
    from sqlalchemy import func
    import logging
    
    # Add more detailed logging
    logging.basicConfig(level=logging.DEBUG)
    
    if current_user.role not in ['student', 'professor']:
        flash('Only students and professors can view received funding.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create empty dictionary to avoid errors
    document_funding = {}
    
    try:
        # Debug output
        app.logger.info(f"Current user ID: {current_user.id}")
        
        # Get all documents owned by the user - removed is_funding_enabled filter for testing
        documents = Document.query.filter_by(user_id=current_user.id).all()
        app.logger.info(f"Found {len(documents)} documents for user")
        
        # Get funding data for each document
        for document in documents:
            app.logger.info(f"Processing document: {document.id} - {document.title}")
            
            if document.is_funding_enabled:
                app.logger.info(f"Document {document.id} has funding enabled")
                try:
                    fundings = Funding.query.filter_by(document_id=document.id).order_by(Funding.created_at.desc()).all()
                    app.logger.info(f"Found {len(fundings)} funding entries for document {document.id}")
                    document_funding[document] = fundings
                except Exception as e:
                    app.logger.error(f"Error fetching fundings for document {document.id}: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error in my_project_funding route: {str(e)}")
        flash("There was an error loading your funding data. Please try again later.", "danger")
    
    # Render with minimal dependencies
    return render_template('my_project_funding.html', document_funding=document_funding)


@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    import stripe
    import os
    import json
    
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    
    try:
        # Verify webhook signature and extract the event
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            # If no webhook secret is set (e.g., in development), parse the event data from the webhook payload
            payload_data = json.loads(payload)
            event = stripe.Event.construct_from(payload_data, stripe.api_key)
        
        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Get metadata from the session
            funding_id = session.get('metadata', {}).get('funding_id')
            
            if funding_id:
                # Update the funding record
                funding = Funding.query.get(funding_id)
                if funding:
                    funding.status = 'approved'
                    db.session.commit()
                    
                    # Create a notification for the document owner
                    document = Document.query.get(funding.document_id)
                    owner = User.query.get(document.user_id)
                    funder = User.query.get(funding.funder_id)
                    
                    create_notification(
                        owner.id,
                        f"{funder.username} from {funder.company_name} has funded your project '{document.title}' with ${funding.amount:,.2f}.",
                        related_document_id=document.id,
                        related_user_id=funder.id
                    )
        
        return '', 200
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return str(e), 400



@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('500.html'), 500