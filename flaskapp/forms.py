from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flaskapp.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    contact_number = StringField('Contact number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_contact_number(self, contact_number):
        user = User.query.filter_by(contact_number=contact_number.data).first()
        if user:
            raise ValidationError('That contact is taken. Please choose a different one.') 
        if len(contact_number.data)!=10:
            raise ValidationError('Please enter a valid 10-digit contact number.')                 
        for c in contact_number.data:
            if(c<'0' or c>'9'):
                raise ValidationError('Please enter a valid 10-digit contact number.')      

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    #picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    contact_number = StringField('Contact number', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
    
    def validate_contact_number(self, contact_number):
        user = User.query.filter_by(contact_number=contact_number.data).first()
        if user:
            raise ValidationError('That contact is taken. Please choose a different one.') 
        if len(contact_number.data)!=10:
            raise ValidationError('Please enter a valid 10-digit contact number.')                 
        for c in contact_number.data:
            if(c<'0' or c>'9'):
                raise ValidationError('Please enter a valid 10-digit contact number.')

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    quantity_kg =  IntegerField('kg',validators=[NumberRange(min=0)])
    quantity_grams =  IntegerField('grams', validators=[NumberRange(min=0, max=900)]) 
    rate = DecimalField('Rate (per kg)',places=2, validators=[DataRequired()])
    additional_info = TextAreaField('Additional Info')
    submit = SubmitField('Post')
    
class BookingForm(FlaskForm):
    quantity_kg =  IntegerField('kg',validators=[NumberRange(min=0)])
    quantity_grams =  IntegerField('grams', validators=[NumberRange(min=0, max=900)])    
    payment_type = RadioField('Payment Method', choices=[('1','Online Payment'),('2','Cash On Delivery')], validators=[DataRequired()])
    submit = SubmitField('Book')


class BankAccountForm(FlaskForm):
    account_number =  StringField('Account Number')
    ifsc_code =  StringField('IFSC Code')    
    submit = SubmitField('Update')