import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from models import *
from forms import *

# CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/BBCG'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///BBCG'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/pictures/slabs/'
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
        return render_template('users/newuser.html', form = form)
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
            return redirect('/login')
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
    return render_template(f'users/{user_type}.html')
    
##### Slab Routes #####

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if current_user.is_authenticated:    
        form = ScanBarcodeForm()

        if form.validate_on_submit():
            slab = Slab.query.filter(Slab.label==form.label.data).first()

            if slab is None:
                flash("No Slab Found")
                return redirect('/scan')
            flash('Slab Found')
            return redirect(f'/cut_slab/{slab.label}')
        return render_template('slabs/scan.html', form=form)
    return redirect('/home')

@app.route('/cut_slab/<int:id>', methods = ['GET', 'POST'])
def cut_slab(id):
    """ form for slab that is cut """
    if current_user.is_authenticated:
        slab = Slab.query.filter(Slab.label==id).first()    
        form = CutSlabForm()
        jobs = [(str(i.id),i.name) for i in Job.query.all()]
        form.job.choices=jobs

        if form.validate_on_submit():
            job = Job.query.get_or_404(form.job.data)
            if slab is None:
                flash("No Slab Found")
                return redirect('/scan')
            if form.picture.data:
                f = form.picture.data
                filename = secure_filename(f.filename)
                f.save(os.path.join(
                    'static/pics', filename
                ))
                slab.picture = f'/static/pics/{filename}'
            slab.cut_slab(form.cut_amount.data)
            slab.jobs.append(job)
            slab_job = SlabJob.query.get((slab.label,job.id))
            slab_job.percent_used=form.cut_amount.data
            db.session.commit()
            flash('Success')
            return redirect(f'/scan')
        return render_template('slabs/cut_slab.html', form=form, slab=slab)
    return redirect('/home')

@app.route('/slab/<int:id>')
def slab(id):
    """ slab info """
    if current_user.is_authenticated:  
        slab = Slab.query.filter(Slab.label==id).first()

        if slab is None:
            flash("No Slab Found")
            return redirect('/scan')
        flash('Slab Found')
        return render_template('slabs/slab.html', slab=slab)

    return redirect('/home')

@app.route('/slab/<int:id>/edit', methods=['GET', 'POST'])
def editslab(id):
    """ slab info """
    if current_user.is_authenticated:  
        slab = Slab.query.filter(Slab.label==id).first()
        vendors=[(str(i.id),i.name) for i in Vendor.query.all()]
        colors=[(str(i.id),i.name)for i in Color.query.all()]
        types = [(str(i.id),i.name) for i in Slab_Type.query.all()]
        form=SlabForm(obj=slab)
        form.vendor.choices=vendors
        form.color.choices=colors
        form.type_id.choices=types
        if slab is None:
            flash("No Slab Found")
            return redirect('/scan')
        if form.validate_on_submit():
            slab.vendor_id = form.vendor.data
            slab.color_id = form.color.data
            slab.batch_num = form.batch_num.data
            slab.length = form.length.data
            slab.width = form.width.data 
            slab.type_id = form.type_id.data
            slab.completed = form.completed.data
            return redirect(f'/slab/{id}')
        flash('Slab Found')
        return render_template('slabs/edit_slab.html', form=form, slab=slab)

    return redirect('/home')

@app.route('/recieve', methods=['GET','POST'])
def recieve():
    """ reviece new slabb and add to db """

    if current_user.is_authenticated:
        form = SlabForm()
        vendors=[(str(i.id),i.name) for i in Vendor.query.all()]
        colors=[(str(i.id),i.name)for i in Color.query.all()]
        types = [(str(i.id),i.name) for i in Slab_Type.query.all()]
        form.vendor.choices=vendors
        form.color.choices=colors
        form.type_id.choices=types
        if form.validate_on_submit():
            slab=Slab(
                vendor_id=form.vendor.data,
                color_id=form.color.data,
                batch_num=form.batch_num.data,
                slab_num=form.slab_num.data,
                length=form.length.data,
                width=form.width.data,
                type_id=form.type_id.data
            )
            if form.picture.data:
                f = form.picture.data
                filename = secure_filename(f.filename)
                f.save(os.path.join(
                    'static/pics', filename
                ))
                slab.picture = f'/static/pics/{filename}'
            db.session.add(slab)
            db.session.commit()
            print(f'**********************{form.picture.data}')
            slab.label = slab.create_label_id()
            db.session.commit()
            return redirect(f'/slab/{slab.label}')
                
        return render_template('/slabs/recieve.html', form = form)

    return redirect('/')


@app.route('/slab/<int:id>/barcode')
def barcode(id):
    """ Create barcode and return it """
    resp=requests.get(f'')
    slab = Slab.query.filter(Slab.label==id).first()
    return render_template('/slabs/slab.html',slab=slab, barcode=resp.data)

@app.route('/newjob', methods=['GET','POST'])
def newJob():
    """ create new job """

    if current_user.is_authenticated:
        form=JobForm()
        edges=[(str(i.id),i.name) for i in Edge.query.all()]
        contractors=[(str(i.id),i.name) for i in Contractor.query.all()]
        form.edge_id.choices = edges
        form.contractor_id.choices=contractors
        if form.validate_on_submit():
            job=Job(
                name=form.name.data,
                po_number=form.po_number.data,
                contractor_id=form.contractor_id.data,
                square_feet=form.sf.data,
                installation_date=form.installation_date.data,
                fabrication_date=form.fabrication_date.data,
                notes=form.notes.data
            )
            db.session.add(job)
            db.session.commit()
            jobedge=JobEdge(
                job_id=job.id,
                edge_id=form.edge_id.data
            )
            db.session.add(jobedge)
            db.session.commit()
            flash('Success: Job Added')
            return redirect('/')

        return render_template('jobs/new_job.html',form=form)

    return redirect('/')