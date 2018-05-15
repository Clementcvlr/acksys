# Welcome to the Flask-Bootstrap sample application. This will give you a
# guided tour around creating an application using Flask-Bootstrap.
#
# To run this application yourself, please install its requirements first:
#
#   $ pip install -r sample_app/requirements.txt
#
# Then, you can actually run the application.
#
#   $ flask --app=sample_app dev
#
# Afterwards, point your browser to http://localhost:5000, then check out the
# source.

from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_user import UserManager

from .frontend import frontend
from .nav import nav


#db = SQLAlchemy(app)
def create_app(configfile=None):
# We are using the "Application Factory"-pattern here, which is described
# in detail inside the Flask docs:
# http://flask.pocoo.org/docs/patterns/appfactories/
	print("Creating App ...")

	app = Flask(__name__)

	# We use Flask-Appconfig here, but this is not a requirement
	AppConfig(app)

	# Install our Bootstrap extension
	Bootstrap(app)

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database2.db'
	app.config['USER_EMAIL_SENDER_EMAIL'] = 'clementvl@gmail.com'
	app.config['DEBUG'] = True
	#from .users import User
	#login_manager = LoginManager()
#	from sample_app.frontend import login_manager
	#login_manager.init_app(app)
	 
	from sample_app.users import db
	print("Init DataBase")
	db.init_app(app)
	from sample_app.users import User, Role, UserRoles
	user_manager = UserManager(app, db, User)
	app.app_context().push()
	db.create_all()
	print("Adding Roles to db")
	admin_role = Role(name='Admin')
	#db.session.add(admin_role)
	comm_role = Role(name='Com')
	#db.session.add(comm_role)
	#db.session.commit()
	 

	# Our application uses blueprints as well; these go well with the
	# application factory. We already imported the blueprint, now we just need
	# to register it:
	app.register_blueprint(frontend)

	# Because we're security-conscious developers, we also hard-code disabling
	# the CDN support (this might become a default in later versions):
	app.config['BOOTSTRAP_SERVE_LOCAL'] = True
	app.config['SECRET_KEY'] = 'devkey'	

	# We initialize the navigation as well
	nav.init_app(app)
	return app
"""@login_manager.user_loader
def load_user(user_id):
	return User.query.filter(User.id == int(user_id)).first()
"""
