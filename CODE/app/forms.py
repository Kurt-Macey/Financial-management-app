from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms import FloatField
from wtforms import validators
from wtforms import RadioField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError
from wtforms.fields.html5 import DateField
from app.models import User
from app.models import account
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Enter your full name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already taken. Please try again.')
    


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class TransactionForm(FlaskForm):
    example = RadioField('Current account', choices=[])
    amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    accountNum = IntegerField('Account number', validators = [DataRequired()])
    submit = SubmitField('Send')

    def validate_accountNum(self,accountNum):
        ownAccount = account.query.filter_by(id=current_user.id).all()
        existingAccount = account.query.filter_by(accountNum=accountNum.data).count()
        for x in ownAccount:
          if x.accountNum == accountNum.data:
              raise ValidationError('You have entered the wrong details. Please try again.')

        if existingAccount == 0:
            raise ValidationError('This account does not exist. Please try again.')


class deposit_sTransactionForm(FlaskForm):
    example = RadioField('Current account', choices=[])
    amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    submit = SubmitField('Send')




class withdraw_sTransactionForm(FlaskForm):
    example = RadioField('Current account', choices=[])
    amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    submit = SubmitField('Send')





class accountForm(FlaskForm):
    example = RadioField('Select Current Account', choices=[])
    submit = SubmitField('Enter')

    def validate_example(self,example):
        amountAccount = account.query.filter_by(id=current_user.id).count()
        if amountAccount > 3:
            raise ValidationError('Youre only allowed to register three accounts online. Please contact the bank to open additional accounts.')
            

class setGoalForm(FlaskForm):
    amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    submit = SubmitField('Send')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
    

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class autoTransactionForm(FlaskForm):
    example = RadioField('Select Current Account', choices=[], validators=[])
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    submit = SubmitField('Submit')

class adminCreateUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('submit')

    #def validate_email(self,email):
        #user = User.query.filter_by(email=email.data).first()
        #if user:
            #raise ValidationError('Email is already taken. Please try again.')
    



class deleteUserForm(FlaskForm):
     user_id = IntegerField('User ID', validators = [DataRequired()])
     submit = SubmitField('submit')

class rollbackTransactionForm(FlaskForm):
     transaction_id = IntegerField('Transaction ID', validators = [DataRequired()])
     submit = SubmitField('submit')
     
class addMoneyForm(FlaskForm):
     accountNum = IntegerField('Account number', validators = [DataRequired()])
     amount = FloatField('Enter amount', validators = [DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
     submit = SubmitField('submit')
