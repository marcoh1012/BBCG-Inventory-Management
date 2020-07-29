from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
# from forms import

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///BBCG'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"
debug = DebugToolbarExtension(app)

connect_db(app)

db.drop_all()
db.create_all()

@app.route('/')
def homepage():
    """ render homepage """
    return redirect('/login')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ render login page or log in """
    return render_template('login.html')