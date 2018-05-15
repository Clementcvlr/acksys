from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_method
#from flask_login import UserMixin
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin


db = SQLAlchemy()

class User(UserMixin, db.Model):
        __tablename__ = 'users'
	
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	email_confirmed_at = db.Column(db.DateTime())
	password = db.Column(db.String(80))
	roles = db.relationship('Role', secondary='user_roles')

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
     
