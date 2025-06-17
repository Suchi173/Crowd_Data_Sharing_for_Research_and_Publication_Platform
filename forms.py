from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from datetime import date
from models import User

class RoleSelectionForm(FlaskForm):
    role = HiddenField('Role')
    submit = SubmitField('Continue')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # Fields for students and professors
    college = StringField('College/University', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    
    # Fields for professors only
    field = StringField('Field of Expertise', validators=[Optional()])
    
    # Fields for companies only
    company_name = StringField('Company Name', validators=[Optional()])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')
    
    def validate_date_of_birth(self, date_of_birth):
        if date_of_birth.data and date_of_birth.data > date.today():
            raise ValidationError('Date of birth cannot be in the future.')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Fields for students and professors
    college = StringField('College/University', validators=[Optional()])
    
    # Fields for professors only
    field = StringField('Field of Expertise', validators=[Optional()])
    
    # Fields for companies only
    company_name = StringField('Company Name', validators=[Optional()])
    
    profile_image = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered. Please use a different one.')

class UploadDocumentForm(FlaskForm):
    title = StringField('Document Title', validators=[DataRequired()])
    description = TextAreaField('Document Description')
    document = FileField('Document', validators=[
        FileRequired(), 
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'rtf', 'ppt', 'pptx', 'xls', 'xlsx'], 'Document files only!')
    ])
    is_public = BooleanField('Make public')
    
    # Funding options
    is_funding_enabled = BooleanField('Enable funding for this project')
    funding_goal = StringField('Funding Goal (USD)', validators=[Optional()])
    
    submit = SubmitField('Upload Document')

class EditDocumentForm(FlaskForm):
    title = StringField('Document Title', validators=[DataRequired()])
    description = TextAreaField('Document Description')
    is_public = BooleanField('Make public')
    
    # Funding options
    is_funding_enabled = BooleanField('Enable funding for this project')
    funding_goal = StringField('Funding Goal (USD)', validators=[Optional()])
    
    submit = SubmitField('Update Document')

class CollaborationForm(FlaskForm):
    collaborator_email = StringField('Collaborator Email', validators=[DataRequired(), Email()])
    permission = SelectField('Permission', choices=[
        ('view', 'View Only'), 
        ('edit', 'Edit'), 
        ('comment', 'Comment')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Collaborator')
    
    def validate_collaborator_email(self, collaborator_email):
        user = User.query.filter_by(email=collaborator_email.data).first()
        if not user:
            raise ValidationError('No user found with this email. Please check the email and try again.')


class FundingForm(FlaskForm):
    amount = StringField('Funding Amount (USD)', validators=[DataRequired()])
    message = TextAreaField('Message to Project Owner (Optional)', validators=[Optional()])
    submit = SubmitField('Fund Project')
