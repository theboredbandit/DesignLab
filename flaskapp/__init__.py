from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

App = Flask(__name__)
App.config['SECRET_KEY'] ='10403ae9f5298025268b94a4110e8eba'
#App.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'#//site.db is path relative to app.py 
App.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vifmodmavbbtly:cf0a18581984f14cf96638297d032b87a61c2d6bb4637af62e3493ea00428735@ec2-3-219-135-162.compute-1.amazonaws.com:5432/d70q8vrvhglnr8'

db = SQLAlchemy(App)
bcrypt=Bcrypt(App)
login_manager=LoginManager(App)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from flaskapp import routes