from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user, login_user, logout_user
from models import db, connect_db, User,User_Type
from forms import *

# CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/BBCG'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"
debug = DebugToolbarExtension(app)


connect_db(app)

login_manager = LoginManager(app)
login_manager.init_app (app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
# db.drop_all()
# db.create_all()

@app.route('/')
def homepage():
    """ render homepage """
    return redirect('/login')

######### User Routes ########
@app.route('/signup', methods=['GET','POST'])
def signup():
    """ Create Account """
    if current_user.is_authenticated:
        form = CreateUserForm()
        types = [(str(i.id),i.type) for i in User_Type.query.all()]
        form.type.choices=types
        if form.validate_on_submit():
            User.signup(form.username.data,form.password.data,form.type.data)
            db.session.commit()
            return redirect('/')
        return render_template('newuser.html', form = form)
    return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ render login page or log in """

    if current_user.is_authenticated:
        return redirect('/home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,form.password.data)

        if not user:
            flash("Invalid Credentials Try Again")
            return redirect('/login', form=form)
        login_user(user)
        flash('Logged In')
        return redirect('/home')
        

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """ logout user """

    logout_user()
    return redirect('/')

@app.route('/home')
def home():
    user_type=current_user.user_type.type.lower()
    return render_template(f'{user_type}.html')
    