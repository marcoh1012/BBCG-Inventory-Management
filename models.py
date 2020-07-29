from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to db"""
    db.app = app
    db.init_app(app)

# user Models
class User(db.Model):
    """ Model for user """

    __tablename__ = 'users'

    username = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    user_type_id = db.Column(db.Integer,db.ForeignKey('user_types.id'))

    user_type = db.relationship('User_Type')

    @classmethod
    def signup(cls, username, password, type_id):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            user_type_id=type_id,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """ authenticate to login user based on username and password """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class User_Type(db.Model):
    """ Model for types of users """

    __tablename__ = 'user_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Text, unique=True, nullable=False)

    users = db.relationship('User')
     