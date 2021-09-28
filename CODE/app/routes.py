import os
from flask import Flask, render_template, redirect, flash, url_for, request,session, abort, request
from app.forms import RegistrationForm, LoginForm, TransactionForm, RequestResetForm, ResetPasswordForm, accountForm, withdraw_sTransactionForm, deposit_sTransactionForm, setGoalForm, autoTransactionForm
from flask_sqlalchemy import SQLAlchemy
from app.models import User, transactions, account, log
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import smtplib
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
from flask_security import Security, SQLAlchemyUserDatastore
from sqlalchemy import func,  Numeric
from contextlib import contextmanager
from sqlalchemy.sql import exists
from flask_wtf.csrf import CSRFProtect


###CSRF PROTECTION###
csrf = CSRFProtect(app)
csrf = CSRFProtect()
csrf.init_app(app)


class userView(ModelView):
  #column_display_pk = True
  #can_delete = False
  #can_edit = False
  #can_create = False
  
  def is_accessible(self):
      if current_user.admin == True:
        return current_user.is_authenticated
      else:
          return abort(404)
  def not_auth(self):
      return "You are not authorised."


class accountView(ModelView):
  column_display_pk = True
  can_delete = False
  can_edit = False
  can_create = False
  def is_accessible(self):
      if current_user.admin == True:
        return current_user.is_authenticated
      else:
          return abort(404)
  def not_auth(self):
      return "You are not authorised."

class transactionView(ModelView):
  column_display_pk = True
  can_delete = False
  can_edit = False
  can_create = False
  def is_accessible(self):
      if current_user.admin == True:
        return current_user.is_authenticated
      else:
          return abort(404)
  def not_auth(self):
      return "You are not authorised."

    
    
#Initiate flask_admin and pass the model view    
admin = Admin(app)
admin.add_view(userView(User, db.session))
admin.add_view(accountView(account, db.session))
admin.add_view(transactionView(transactions, db.session))
######################################################################################################################################
'''Users register an acount with a username, email and password. A current account, distinguished by setting "role" to "1", is created for the user.
In addition, a savings account, distinguished by setting "role" to "2" is created for the user. Data is commited to the database.'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        accounts = account(id=user.id, accountBalance = '500', role='1', goal='0')
        db.session.add(accounts)
        db.session.commit()
        saccounts = account(id=user.id,accountBalance = '0', role='2', goal = '0')
        db.session.add(saccounts)
        db.session.commit()
        flash("Account was suceccfully registered!", 'success')
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('register.html', title='Register', form=form)
######################################################################################################################################
'''User logs into the application. The database is checked to veirfy if the user is on record. The user is asked to verify his account using the email he registered with.
The user is unable to view any content until he has verified his account. The ip address of the user is logged for security reasons. If the user accesses his account from a new ip address,
he is ntoified via his email. Admin who access their accounts from a new ip address, i.e not the companies ip address, are logged out automatically.'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homehome'))
    form = LoginForm()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user and bcrypt.check_password_hash(user.password, form.password.data):
             login_user(user, remember=form.remember.data)
             flash("Logged in successfully!", 'success')

             
             logg = log(user_id=user.id, ip_address=request.remote_addr)
             q = log.query.filter_by(ip_address=request.remote_addr, user_id=user.id).count()
             if user.admin == 0 and q < 1:
               ###send_newIpAddressWarning_email(user)
               db.session.add(logg)
               db.session.commit()
             if user.admin == 1 and q < 1:
               ###send_newAdminIpAddressWarning_email(user)
               logout_user()
             elif current_user.admin == 1:
               return redirect(url_for('admin.index'))
             return redirect(url_for('homehome'))
       else:
         flash("Incorrect login details! Please try again.", 'warning')
    return render_template('login.html', title='Login', form=form)
######################################################################################################################################
'''Log user out.'''
@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully!", 'success')
    return redirect(url_for('homehome'))

######################################################################################################################################
'''Reset users password. Send a link to users email.'''
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

######################################################################################################################################
'''Confirm CSRF token and allow user to reset password.'''
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

######################################################################################################################################
'''DIsplay transaction history of the selected current account.'''

@app.route('/currentAccount', methods=['GET', 'POST'])
@login_required
def home():

    form = TransactionForm()
    changeAccount = form.example.data
    form5 = accountForm(request.form)
    form5.example.choices = [(probot.accountNum) for probot in account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()]
    user = account.query.filter_by(accountNum = changeAccount).first()
    user123 = account.query.filter_by(id=current_user.id).all()
    usersAccounts = []
    usersAccounts.append(user123)
    userCon = User.query.filter_by(id=current_user.id).first()
    if userCon.confirmed == False:
      flash("Click on the link sent to your email to activate your account. If this link has timed out, refresh the page to recieve a new link via your email.", 'primary') 
      send_confirm_email(userCon)
    users = User.query.all()
    transaction1 = transactions.query.filter_by(parent_id=changeAccount).filter(account.role.like('1')).all()
    transaction2 = transactions.query.filter_by(recipient_id=changeAccount).filter(account.role.like('1')).all()
    
    if changeAccount == None:
      account1001 = account.query.filter_by(id=current_user.id).filter(account.role.like('1')).first()
      changeAccount = account1001.accountNum
      transaction1 = transactions.query.filter_by(parent_id=changeAccount).filter(account.role.like('1')).all()
      transaction2 = transactions.query.filter_by(recipient_id=changeAccount).filter(account.role.like('1')).all()
      user = account.query.filter_by(accountNum = changeAccount).first()
      return render_template('home.html', users=users, transaction1=transaction1, user=user,transaction2=transaction2,user123=user123, form=form5)
    return render_template('home.html', users=users, transaction1=transaction1, user=user,transaction2=transaction2,user123=user123, form=form5)

######################################################################################################################################
'''User is able to create up to three current accounts in total.'''    

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    amountAccount = account.query.filter_by(id=current_user.id).filter(account.role.like('1')).count()  
    if amountAccount < 3 and current_user.admin == False: 
      createAccount = account(id=current_user.id, accountBalance = '0', role = '1', goal='0')
      db.session.add(createAccount)
      db.session.commit()
      flash("Account created!", 'success')
    else:
      flash("Account failed to create! users may only register 3 accounts online. Contact the bank to create additional accounts.", 'warning')
    return redirect(url_for('home'))
######################################################################################################################################
'''User can conduct transactions between other acounts recorded on the database.'''
@app.route('/transaction', methods=['GET', 'POST'])
@login_required
def transaction():
    form = TransactionForm()
    form.example.choices = [(probot.accountNum) for probot in account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()]
    if form.validate_on_submit():
      
      chosenAccount = form.example.data
      account11 = account.query.filter_by(accountNum = chosenAccount).first()
      amount = float(round(form.amount.data, 2))
      userSAccount = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
      if account11.accountBalance >= amount:
        acca = account(50,0,0,0)
        acca.transaction(amount,account11.accountNum,form.accountNum.data)
        if account11.split == 1:
          acca.splitFeature(amount,account11.accountNum, userSAccount.accountNum)
        flash("Transaction complete!", 'success')
        return redirect(url_for('home'))
      else:
        flash("Transaction failed! You have insufficient funds.", 'warning')
        return redirect(url_for('transaction'))     
    return render_template('transaction.html', title='Transaction', form=form)

######################################################################################################################################

'''Display transaction history of the users savings account'''

@app.route('/savings')
def savings():
    user = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
    account99 = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
    
    transaction1 = transactions.query.filter_by(parent_id=account99.accountNum).all() 
    transaction2 = transactions.query.filter_by(recipient_id=account99.accountNum).all()

    goal = account99.goal
    balance = account99.accountBalance
    percent = 0;
    if account99.goal > 0:
      percent = round((balance/goal) * 100, 1)
      if percent >= 100:
        flash("You have achieved your goal!", 'success')
        
    userCon = User.query.filter_by(id=current_user.id).first()
    if userCon.confirmed == False:
      flash("Click on the link sent to your email to activate your account. If this link has timed out, refresh the page to recieve a new link via your email.", 'primary')
      ###send_confirm_email(userCon)

    
      
    return render_template('savings.html', user=user, transaction1=transaction1, transaction2=transaction2, percent=percent )

######################################################################################################################################
'''User is able to set a goal that he wishes to achieve in his savings account.'''

@app.route('/setGoal', methods=['GET', 'POST'])
def setGoal():
   form = setGoalForm()
   userSAccount = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first() 
   if form.validate_on_submit():
     amount = form.amount.data 
     a = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).update(dict(goal=amount), synchronize_session=False)
     db.session.commit()    
     return redirect(url_for('savings'))
   return render_template('setGoal.html', form=form )
######################################################################################################################################
'''Reset the goal to 0.'''
@app.route('/resetGoal', methods=['GET', 'POST'])
def resetGoal():
    a = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).update(dict(goal=0), synchronize_session=False)
    db.session.commit()    
    return redirect(url_for('savings'))
######################################################################################################################################   
'''User is able to deposit money into his savings account'''
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    depositForm = deposit_sTransactionForm()
    depositForm.example.choices = [(probot.accountNum) for probot in account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()]
    userSAccount = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
    if depositForm.validate_on_submit():
       chosenAccount = depositForm.example.data
       user = account.query.filter_by(accountNum = depositForm.example.data).first()
       user1 = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
       amount = float(round(depositForm.amount.data, 2))
       if user.accountBalance >= amount:
        acca = account(50,0,0,0)
        acca.transaction(amount,user.accountNum,user1.accountNum)
        flash("You have successfully deposited money into your savings account!", 'success')
        return redirect(url_for('savings'))

    return render_template('savings_deposit.html', user=userSAccount, form=depositForm )
######################################################################################################################################
'''User is able to withdraw money from his savings account'''
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    depositForm = withdraw_sTransactionForm()
    depositForm.example.choices = [(probot.accountNum) for probot in account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()]
    userSAccount = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
    if depositForm.validate_on_submit():
       chosenAccount = depositForm.example.data
       user = account.query.filter_by(accountNum = depositForm.example.data).first()
       user1 = account.query.filter_by(id=current_user.id).filter(account.role.like('2')).first()
       amount = float(round(depositForm.amount.data, 2))
       if user1.accountBalance >= amount:
          acca = account(50,0,0,0)
          acca.transaction(amount,user1.accountNum,user.accountNum)
          flash("You have successfully withdrawn money from your savings account!", 'success')
          return redirect(url_for('savings'))
       else:
          flash("You have insufficient funds!", 'warning')
    
    return render_template('savings_withdraw.html', user=userSAccount, form=depositForm )
######################################################################################################################################
'''Activate "split" feature, whereby every transaction is rounded up to the nearest pound sterling, and the different is stored into the users savings account.'''
@app.route("/split", methods=['GET', 'POST'])
def split():

  account17 = account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()
  for x in account17:
    if current_user.admin == False:
      account18 = account.query.filter_by(accountNum = x.accountNum).update(dict(split=True))
      db.session.commit()
    
      
    
  return redirect(url_for('home'))
    
######################################################################################################################################
'''Set a date for a transaction to occur automatically'''
@app.route("/autoTransaction", methods=['GET', 'POST'])
def autoTransaction():
  dt = datetime.datetime.today()
  form = autoTransactionForm()
  form.example.choices = [(probot.accountNum) for probot in account.query.filter_by(id=current_user.id).filter(account.role.like('1')).all()]
  chosenAccount = form.example.data
  date = form.startdate.data
  if form.validate_on_submit():
    account987 = account.query.filter_by(accountNum = form.example.data).update(dict(autoTransaction_date=date))
    db.session.commit()
    flash("Task complete. You will start to save!" + "5" + "date", 'success')
    return redirect(url_for('savings'))    
    
  return render_template('autoTransaction.html', form=form)

######################################################################################################################################  

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message()
    msg.subject = "Email Subject"
    msg.recipients = [user.email]
    msg.sender = 'c1545729@gmail.com'
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
######################################################################################################################################  


def send_confirm_email(user):
    token = user.get_reset_token()
    msg = Message()
    msg.subject = "Email Subject"
    msg.recipients = [user.email]
    msg.sender = 'c1545729@gmail.com'
    msg.body = f'''To confirm your email, visit the following link:
{url_for('confirm_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
######################################################################################################################################  
def send_newIpAddressWarning_email(user):
    msg = Message()
    msg.subject = "Email Subject"
    msg.recipients = [user.email]
    msg.sender = 'c1545729@gmail.com'
    msg.body = f'''Someone has recently tried to access your account from a new location. Please verify us if this was not you.
'''
    mail.send(msg)
######################################################################################################################################  
def send_newAdminIpAddressWarning_email(user):
    user.email='c1545729@gmail.com'
    msg = Message()
    msg.subject = "Email Subject"
    msg.recipients = [user.email]
    msg.sender = 'c1545729@gmail.com'
    msg.body = f'''An admin with with the user id {user.id}, has recently tried to access his website from an external device. 
'''
    mail.send(msg)
    
######################################################################################################################################  
@app.route("/login/<token>", methods=['GET', 'POST'])
def confirm_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        return redirect(url_for('home'))
    else:
        rows_changed = User.query.filter_by(id=current_user.id).update(dict(confirmed=True))
        db.session.commit()
    flash ('You have activated your account', 'success')    
    return redirect(url_for('home'))
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def homehome():
  return render_template('homehome.html')





