from datetime import datetime
import requests
import os

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to db"""
    db.app = app
    db.init_app(app)

# from app import login_manager



###### Models for users ########
class User(UserMixin, db.Model):
    """ Model for user """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
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
     
###### Models for slabs #######
class Vendor(db.Model):
    """ Model for vendors """
    
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    slabs = db.relationship('Slab')

class Color(db.Model):
    """ Model for slab Color """
    __tablename__ = "colors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    slabs = db.relationship('Slab')



class Slab_Type(db.Model):
    """ Model for slab types """

    __tablename__ = 'slab_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    slabs = db.relationship('Slab')



class Slab(db.Model):
    """ Model for slabs """
    __tablename__ = "slabs"
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), primary_key=True, autoincrement=False)
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'), primary_key=True, autoincrement=False)
    batch_num = db.Column(db.Integer, primary_key=True, autoincrement=False)
    slab_num = db.Column(db.Integer, primary_key=True, autoincrement=False)

    length = db.Column(db.Integer, nullable=True, default=0)
    width = db.Column(db.Integer, nullable=True, default=0)
    picture = db.Column(db.Text, nullable=True, default = '/static/pics/no_image.jpg')
    type_id = db.Column(db.Integer, db.ForeignKey('slab_types.id'), nullable=False)
    label = db.Column(db.Integer, unique=True, nullable=True)
    label_picture = db.Column(db.Text,nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    amount_left = db.Column(db.Integer, default = 100)
    completed = db.Column(db.Boolean, default=False)

    vendor = db.relationship('Vendor')
    color = db.relationship('Color')
    type = db.relationship('Slab_Type')

    jobs = db.relationship('Job', secondary='slabs_jobs', backref=db.backref('slabs'))

    def create_label_id(self):
        """ Create label id number """
        label_id=int(f"{self.vendor_id}{self.color_id}{self.batch_num}{self.slab_num}")
        url=f'https://barcodes4.me/barcode/c39/{label_id}.jpg?IsTextDrawn=1&TextSize=15'
        resp=requests.get(url)
        if resp.status_code == 200:
            with open(os.path.join(
                'static/pics/barcodes', f'{label_id}.jpg'
                ), 'wb') as f:
                f.write(resp.content)
            self.label_picture = os.path.join('/static/pics/barcodes', f'{label_id}.jpg')
        return label_id

    def calculate_area(self):
        """ Calculate square footage of a slab  input is in  inches"""
        sf = round((int(self.length) * int(self.width)) / 144,2)
        return sf
    def cut_slab(self,percent):
        """ calculate the amount of slab left """
        self.amount_left= self.amount_left-percent
        return self.amount_left


######## Models for Jobs ########

class Contractor(db.Model):
    """ Model for contractors """
    __tablename__ = "contractors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)

    jobs = db.relationship('Job')

class Cutout(db.Model):
    """ Model for cutouts """
    __tablename__ = "cutouts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)

class Edge(db.Model):
    """ Model for edges """
    __tablename__ = "edges"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    type = db.Column(db.Text, nullable=False)

class Job(db.Model):
    """Model for Job """
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    square_feet = db.Column(db.Float, nullable=True)
    installation_date = db.Column(db.DateTime, nullable=True)
    fabrication_date = db.Column(db.DateTime, nullable=True)
    po_number = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id'))

    contractor = db.relationship("Contractor")
    edges = db.relationship('Edge', secondary='jobs_edges', backref=db.backref('jobs'))
    cutouts = db.relationship('Cutout', secondary='jobs_cutouts', backref=db.backref('jobs'))

class JobEdge(db.Model):
    """ model for job_edge """
    __tablename__ = 'jobs_edges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    edge_id = db.Column(db.Integer, db.ForeignKey('edges.id'))
    lf = db.Column(db.Float)

class JobCutout(db.Model):
    """ Model for job_cutout """

    __tablename__ = 'jobs_cutouts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    cutout_id = db.Column(db.Integer, db.ForeignKey('cutouts.id'))
    cutout_count = db.Column(db.Integer)

class SlabJob(db.Model):
    """ Model for Slab_Job """
    __tablename__ = 'slabs_jobs'

    slab_id = db.Column(db.Integer, db.ForeignKey('slabs.label'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), primary_key=True)
    percent_used = db.Column(db.Integer)
