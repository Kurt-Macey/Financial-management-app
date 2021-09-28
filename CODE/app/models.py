from app import db
from app import login_manager
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
Base = declarative_base()
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import app
from sqlalchemy.dialects import mysql
from sqlalchemy import Numeric

Integer = mysql.INTEGER 

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

###############################################################################################################
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    child = relationship("account")

    def get_reset_token(self, expires_sec=15):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
            

    def __init__(self,username, email, password):
              self.username = username
              self.email = email
              self.password = password
###############################################################################################################              
              
              
        
###############################################################################################################         
class account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer,db.ForeignKey('user.id', ondelete='CASCADE'))
    accountNum = db.Column(db.Integer, primary_key=True)
    accountBalance = db.Column(db.Float, nullable=True)
    role = db.Column(db.Integer)
    goal = db.Column(db.Float)
    split = db.Column(db.Boolean, default=False)
    autoTransaction_date = db.Column(db.DateTime, nullable=True)
    autoTransaction_amount = db.Column(db.Float, default='0')
        
    def transaction(self,amount, senderAccountNumber, recieverAccountNumber):
        try:
             senderAccount = account.query.filter_by(accountNum=senderAccountNumber).first()
             senderBalance = float(senderAccount.accountBalance)
             senderBalanceUpdate = senderBalance - amount
             c = account.query.filter_by(accountNum = senderAccountNumber).update(dict(accountBalance=senderBalanceUpdate))


             recieverAccount = account.query.filter_by(accountNum=recieverAccountNumber).first()
             recieverBalance = float(recieverAccount.accountBalance)
             recieverBalanceUpdate = recieverBalance + amount
             d = account.query.filter_by(accountNum = recieverAccountNumber).update(dict(accountBalance=recieverBalanceUpdate))

             transaction = transactions(senderAccountNumber,recieverAccountNumber,'',amount)
             db.session.add(transaction)
             db.session.commit()
             
        except Exception:
              db.session.rollback()
              flash("Transaction failed!", 'warning')
              return redirect(url_for('transaction'))

    def splitFeature(self, amount, senderAccountNumber, userSAccount):
        try:
          senderAccount = account.query.filter_by(accountNum=senderAccountNumber).first()
          recieverAccount = account.query.filter_by(accountNum=userSAccount).first()
        
          amountRound = float(round(amount + .5))
          diff = amountRound - amount
               
          split = senderAccount.accountBalance - diff
          split1 = recieverAccount.accountBalance + diff
               
          c = account.query.filter_by(accountNum = senderAccountNumber).update(dict(accountBalance=split))
          d = account.query.filter_by(accountNum = recieverAccount.accountNum).update(dict(accountBalance=split1))
          db.session.commit()
        except Exception:
            print(Exception)
        

    def __init__(self,id,accountBalance, role, goal):
              self.id = id
              self.accountBalance = accountBalance
              self.role = role
              self.goal = goal
###############################################################################################################              
              
              
###############################################################################################################
class accountRole(db.Model):
    __tablename__ = 'accountRole'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __init__(self,id,name):
              self.id = id
              self.name = name
###############################################################################################################              
              
              
###############################################################################################################        
class transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = Column(Integer, db.ForeignKey('account.accountNum', ondelete='CASCADE'))
    recipient_id = Column(db.Integer, db.ForeignKey('account.accountNum', ondelete='CASCADE'))
    date = db.Column(db.String(20))
    amount = db.Column(db.Float)
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)


    def __init__(self, parent_id, recipient_id, date, amount):
              self.parent_id = parent_id  
              self.date = date
              self.amount = amount
              self.recipient_id = recipient_id
###############################################################################################################

###############################################################################################################
class log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    ip_address = db.Column(db.String(60))


    def __init__(self,user_id, ip_address):
              self.user_id = user_id
              self.ip_address = ip_address
###############################################################################################################    
                   
