import os
from flask import Flask
from flask import render_template
from flask import redirect
from flask import flash
from flask import url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from smtplib import SMTP
import smtplib
from datetime import timedelta
from sqlalchemy import  create_engine



#Stores an instance of the flask class
app = Flask(__name__)

#Secret key is used for token authentication
app.config['SECRET_KEY'] = '566a882c5bb71415c6587b425b010acb'

#database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

#engine = create_engine("mysql+pymysql://root:password@localhost/test")
#engine.connect()

#Create an instance of the SQLAlchemy class
db = SQLAlchemy(app)

#initiate Bcrypt functionality
bcrypt = Bcrypt(app)

#inititate flask_login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#Flask_mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ""
app.config['MAIL_PASSWORD'] = ""

#log the user out after a 15 minute session
app.permanent_session_lifetime = timedelta(minutes=15) 
app.PRESERVE_CONTEXT_ON_EXCEPTION = True
mail = Mail(app)

from app import routes
from app.models import User
from app.models import transactions
from app.models import account
from flask_login import current_user


