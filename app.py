import os
import requests
import shutil
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user, login_user, logout_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from models import *
from forms import *
from reports import *
from sqlalchemy import exc

# CURR_USER_KEY = "curr_user"

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/BBCG'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///BBCG')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/pictures/slabs/'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','secret')
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

@app.route('/slabs')
def home():
    """ redirect to first page of slabs """
    return redirect('/slabs/1')

######### User Routes ########
@app.route('/signup', methods=['GET','POST'])
def signup():
    """ Create Account """
    if current_user.is_authenticated:
        form = CreateUserForm()
        types = [(str(i.id),i.type) for i in User_Type.query.all()]
        form.type.choices=types
        if form.validate_on_submit():
            try:
                User.signup(form.username.data,form.password.data,form.type.data)
                db.session.commit()
                flash('User Created','sucess')
                return redirect('/slabs/1')
            except exc.IntegrityError:
                db.session.rollback()
                flash('User already','danger')
                return redirect ('/signup')

        return render_template('users/newuser.html', form = form, user=current_user)
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ render login page or log in """

    if current_user.is_authenticated:
        return redirect('/slabs/1')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,form.password.data)

        if not user:
            flash("Invalid Credentials Try Again", 'danger')
            return redirect('/login')
        login_user(user)
        flash('Logged In','success')
        return redirect('/slabs/1')
        

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """ logout user """

    logout_user()
    flash('logged out', 'success')
    return redirect('/')

@app.route('/slabs/<int:page_num>')
def slabs(page_num):
    if current_user.is_authenticated: 
        user_type=current_user.user_type.type.lower()
        if user_type == 'reciever':
            return redirect('/recieve')
        if user_type == 'fabricator':
            return redirect('/scan')
        slabs=Slab.query.paginate(per_page=20, page=page_num)
        return render_template(f'slabs/slabs.html', slabs=slabs, user=current_user, sort_by=None)
    return redirect('/')
    
##### Slab Routes #####

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if current_user.is_authenticated:    
        form = ScanBarcodeForm()

        if form.validate_on_submit():

            slab = Slab.query.filter(Slab.label==form.label.data).first()

            if slab is None:
                flash("No Slab Found", 'danger')
                return redirect('/scan')
            flash('Slab Found', "success")
            return redirect(f'/cut_slab/{slab.label}')
        return render_template('slabs/scan.html', form=form, user=current_user)
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/cut_slab/<int:id>', methods = ['GET', 'POST'])
def cut_slab(id):
    """ form for slab that is cut """
    if current_user.is_authenticated:
        slab = Slab.query.filter(Slab.label==id).first()    
        form = CutSlabForm()
        jobs = [(str(i.id),i.name) for i in Job.query.all()]
        form.job.choices=jobs

        if slab is None:
            flash("No Slab Found",'danger')
            return redirect('/scan')

        if form.validate_on_submit():
            job = Job.query.get_or_404(form.job.data)
            
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
            flash('Success', 'success')
            return redirect(f'/scan')
        return render_template('slabs/cut_slab.html', form=form, slab=slab,user=current_user)
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/slab/<int:id>')
def slab(id):
    """ slab info """
    if current_user.is_authenticated:  
        slab = Slab.query.filter(Slab.label==id).first()

        if slab is None:
            flash("No Slab Found", 'danger')
            return redirect('/scan')
        flash('Slab Found', 'success')
        return render_template('slabs/slab.html', slab=slab, user=current_user)
    flash('Please Sign In First', 'danger')
    return redirect('/')

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
            flash("No Slab Found", 'danger')
            return redirect('/scan')
        if form.validate_on_submit():
            slab.length = form.length.data
            slab.width = form.width.data 
            slab.type_id = form.type_id.data
            if form.picture.data and not isinstance(form.picture.data,str):
                f = form.picture.data
                filename = secure_filename(f.filename)
                f.save(os.path.join(
                    'static/pics', filename
                ))
                slab.picture = f'/static/pics/{filename}'
            db.session.commit()
            flash('Edited','success')
            return redirect(f'/slab/{id}')
        flash('Slab Found','success')
        return render_template('slabs/edit_slab.html', form=form, slab=slab,user=current_user)

    return redirect('/home')

@app.route('/recieve', methods=['GET','POST'])
def recieve():
    """ reviece new slab and add to db """

    if current_user.is_authenticated:
        form = SlabForm()
        vendors=[(str(i.id),i.name) for i in Vendor.query.all()]
        colors=[(str(i.id),i.name)for i in Color.query.all()]
        types = [(str(i.id),i.name) for i in Slab_Type.query.all()]
        form.vendor.choices=vendors
        form.color.choices=colors
        form.type_id.choices=types
        if form.validate_on_submit():
            try:
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
                slab.label = slab.create_label_id()
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Slab Already Exist, Try Again','danger')
                return redirect ('/recieve')


            return redirect(f'/slab/{slab.label}')
                
        return render_template('/slabs/recieve.html', form = form,user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/slab/<int:id>/delete')
def deleteSlab(id):
    """ delete slab """

    slab=Slab.query.filter(Slab.label == id).first()
    db.session.delete(slab)
    db.session.commit()
    flash("Slab Deleted",'success')
    return redirect('/slabs/1')

##### Jobs Routes ####
@app.route('/job/new', methods=['GET','POST'])
def newJob():
    """ create new job """

    if current_user.is_authenticated:
        form=JobForm()
        contractors=[(str(i.id),i.name) for i in Contractor.query.all()]
        form.contractor_id.choices=contractors
        if form.validate_on_submit():
            try:
                job=Job(
                    name=form.name.data,
                    po_number=form.po_number.data,
                    contractor_id=form.contractor_id.data,
                    square_feet=form.square_feet.data,
                    installation_date=form.installation_date.data,
                    fabrication_date=form.fabrication_date.data,
                    notes=form.notes.data
                )
                db.session.add(job)
                db.session.commit()
                flash('Success: Job Added', 'success')
            except exc.IntegrityError:
                db.session.rollback()
                flash('Job Already Exist','danger')
                return redirect ('/job/new')
            return redirect(f'/job/{job.id}')

        return render_template('jobs/new_job.html', form=form, user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/edit', methods=['GET','POST'])
def editJob(id):
    """ edit existing job """

    if current_user.is_authenticated:
        job=Job.query.filter(Job.id==id).first()
        form=JobForm(obj=job)
        contractors=[(str(i.id),i.name) for i in Contractor.query.all()]
        form.contractor_id.choices=contractors
        if form.validate_on_submit():
            job.name=form.name.data
            job.po_number=form.po_number.data
            job.contractor_id=form.contractor_id.data
            job.square_feet=form.square_feet.data
            job.installation_date=form.installation_date.data
            job.fabrication_date=form.fabrication_date.data
            job.notes=form.notes.data
            db.session.commit()
            flash('Job Edited', 'success')
            return redirect(f'/job/{id}')
        return render_template('/jobs/edit_job.html', form = form, user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/jobs/<int:page_num>')
def view_jobs(page_num):
    """ view all jobs """
    if current_user.is_authenticated:
        jobs=Job.query.paginate(per_page=30, page=page_num)
        return render_template('/jobs/jobs.html',jobs=jobs, user=current_user,sort_by=None)
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/delete')
def delete_job(id):
    """ delete job """

    if current_user.is_authenticated:
        job=Job.query.get(id)
        db.session.delete(job)
        db.session.commit()
        return redirect('/jobs/1')

    flash('Please Sign In First', 'danger')
    return redirect('/')


@app.route('/job/<int:id>')
def view_job(id):
    """ view job """

    if current_user.is_authenticated:
        job=Job.query.get_or_404(id)
        slabs= db.session.query(Slab, Vendor.name, Color.name, SlabJob.job_sf).join(Vendor).join(Color).join(SlabJob).filter(SlabJob.job_id == job.id)
        cutouts= db.session.query(Cutout.name, JobCutout.cutout_count,JobCutout.cutout_id).filter(JobCutout.job_id==job.id).join(Cutout).all()
        edges = db.session.query(JobEdge.lf, Edge.name, JobEdge.edge_id).filter(JobEdge.job_id==job.id).join(Edge).all()
        slabform=BarcodeAndSFForm()
        slabsfform = AddSlabSF()
        cutoutform=AddCutoutForm()
        cutoutform.cutout.choices = [(str(i.id),i.name) for i in Cutout.query.all()]
        edgeform=AddEdgeForm()
        edgeform.edge.choices = [(str(i.id),i.name) for i in Edge.query.all()]
        forms=[slabform,cutoutform,edgeform,slabsfform]
        return render_template('/jobs/job.html', slabs=slabs, job=job, cutouts=cutouts, edges=edges, forms=forms, user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

########## Job Page routes ##########
@app.route('/job/<int:id>/addslab', methods=['POST'])
def add_slab(id):
    """ Add slab to job """

    if current_user.is_authenticated:    
        form = BarcodeAndSFForm(request.form)
        if form.validate_on_submit():
            SJ=SlabJob(slab_id=form.label.data,job_id=id, job_sf=form.job_sf.data)
            db.session.add(SJ)
            db.session.commit()
            flash('Slab Added','success')
            return redirect(f'/job/{id}')
        flash('Error Occured, Try Again', 'danger')
        return redirect(f'/job/{id}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/addcutout', methods=['POST'])
def addcutout(id):
    """ Add Cutout to job """

    if current_user.is_authenticated:    
        form = AddCutoutForm(request.form)
        form.cutout.choices = [(str(i.id),i.name) for i in Cutout.query.all()]
        if form.validate_on_submit():
            JC=JobCutout(job_id=id, cutout_id=form.cutout.data, cutout_count=form.number.data)
            db.session.add(JC)
            db.session.commit()
            flash('Cutout Added','success')
            return redirect(f'/job/{id}')
        flash('Error Occured, Try Again', 'danger')
        return redirect(f'/job/{id}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/addedge', methods=['POST'])
def addedge(id):
    """ Add Edge to Job """

    if current_user.is_authenticated:    
        form = AddEdgeForm(request.form)
        form.edge.choices = [(str(i.id),i.name) for i in Edge.query.all()]
        if form.validate_on_submit():
            JE=JobEdge(job_id=id, edge_id=form.edge.data, lf=form.lf.data)
            db.session.add(JE)
            db.session.commit()
            flash('Cutout Added','success')
            return redirect(f'/job/{id}')
        flash('Error Occured, Try Again', 'danger')
        return redirect(f'/job/{id}')
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/slab/<int:label>/delete')
def remove_JobSlab(id, label):
    """ remove relationship from slabjob """

    if current_user.is_authenticated:   
        slab=Slab.query.filter(Slab.label==label).first()
        SJ = SlabJob.query.filter(SlabJob.job_id==id, SlabJob.slab_id==label).first()
        slab.amount_left=slab.amount_left + SJ.percent_used
        db.session.delete(SJ)
        db.session.commit()
        return redirect(f'/job/{id}')
    
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/cutout/<int:cutout_id>/delete')
def remove_JobCutout(id, cutout_id):
    """ remove relationship from jobcutout """

    if current_user.is_authenticated:  
        JC=JobCutout.query.filter(JobCutout.job_id==id, JobCutout.cutout_id==cutout_id).first()
        db.session.delete(JC)
        db.session.commit()
        return redirect(f'/job/{id}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/edge/<int:edge_id>/delete')
def remove_JobEdge(id, edge_id):
    """ remove relationship from jobedge """

    if current_user.is_authenticated:  
        JE=JobEdge.query.filter(JobEdge.job_id==id, JobEdge.edge_id==edge_id).first()
        db.session.delete(JE)
        db.session.commit()
        return redirect(f'/job/{id}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/job/<int:id>/<int:slab_id>/addslabsf', methods=['POST'])
def add_slab_sf(id, slab_id):
    """ add sf used from this slab """

    if current_user.is_authenticated:
        form=AddSlabSF(request.form)
        if form.validate_on_submit():    
            sj=SlabJob.query.get([slab_id,id])
            sj.job_sf=form.job_sf.data
            db.session.commit()
            flash('Job square footage added/edited', 'success')
        return redirect(f'/job/{id}')
    
    flash('Please Sign In First', 'danger')
    return redirect('/')
    


######### Sorting Routes########
@app.route('/slabs/search/<int:page_num>', methods=['GET','POST'])
def search_slabs(page_num):
    """ search for slabs with keywords """

    if current_user.is_authenticated:
        term=request.form.get('search-term')
        return redirect(f'/slabs/search/{term}/{page_num}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

        

@app.route('/slabs/search/<term>/<int:page_num>')
def search_slabs_term(term,page_num):
    """ search for slabs with keywords and pagination """

    if current_user.is_authenticated:  
        if term.isnumeric():
             full_results=Slab.query.filter(Slab.label==term).paginate(per_page=20,page=page_num, error_out=False)
        else:
            full_results=Slab.query.join(Vendor).join(Color).join(Slab_Type).filter(or_(Vendor.name.ilike(term), Color.name.ilike(term),Slab_Type.name.ilike(term))).paginate(per_page=16,page=page_num, error_out=False)
        
        return render_template('/slabs/slabs.html', slabs=full_results, user=current_user, sort_by='search', search_term=term)

    flash('Please Sign In First', 'danger')
    return redirect('/')
       
@app.route('/slabs/sort/<sort_type>/<int:page_num>')
def sort_slabs(sort_type,page_num):
    """ Slabs Sort By """
    
    if current_user.is_authenticated:
        if sort_type == 'name-asc':
            slabs=Slab.query.join(Vendor).order_by(Vendor.name).paginate(per_page=20, page=page_num)
        elif sort_type == 'name-desc':
            slabs=Slab.query.join(Vendor).order_by(Vendor.name.desc()).paginate(per_page=20, page=page_num)
        elif sort_type == 'date-asc':
            slabs=Slab.query.order_by(Slab.created).paginate(per_page=20, page=page_num)
        elif sort_type == 'date-desc':
            slabs=Slab.query.order_by(Slab.created.desc()).paginate(per_page=20, page=page_num)
        elif sort_type == 'completed':
            slabs=Slab.query.filter(Slab.completed==True).paginate(per_page=20, page=page_num)
        else:
            flash("Not a Valid Sort Type", 'danger')
            return redirect('/')

        return render_template('/slabs/slabs.html',slabs=slabs, user=current_user, sort_by= sort_type)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/jobs/search/<int:page_num>', methods=['POST'])
def search_jobs(page_num):
    """ search for slabs with keywords """

    if current_user.is_authenticated:
        term=request.form.get('search-term')
        return redirect(f'/jobs/search/{term}/{page_num}')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/jobs/search/<term>/<int:page_num>')
def search_jobs_term(term,page_num):
    """ search jobs useing term """
        
    if current_user.is_authenticated:
        full_results=Job.query.join(Contractor).join(JobEdge).join(Edge).filter(or_(Job.name.ilike(term),Contractor.name.ilike(term),(Edge.name.ilike(term)))).paginate(per_page=16,page=page_num, error_out=False)
    
        return render_template('/jobs/jobs.html', jobs=full_results, user=current_user, sort_by='search', search_term=term)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/jobs/sort/<sort_type>/<int:page_num>')
def sort_jobs(sort_type,page_num):
    """ Jobs Sort By """
    
    if current_user.is_authenticated:
        if sort_type == 'name-asc':
            jobs=Job.query.order_by(Job.name).paginate(per_page=30, page=page_num)
        elif sort_type == 'name-desc':
            jobs=Job.query.order_by(Job.name.desc()).paginate(per_page=30, page=page_num)
        elif sort_type == 'date-asc':
            jobs=Job.query.order_by(Job.installation_date).paginate(per_page=30, page=page_num)
        elif sort_type == 'date-desc':
            jobs=Job.query.order_by(Job.installation_date.desc()).paginate(per_page=30, page=page_num)
        elif sort_type == 'cust-asc':
            jobs=Job.query.join(Contractor).order_by(Contractor.name).paginate(per_page=30, page=page_num)
        elif sort_type == 'cust-desc':
            jobs=Job.query.join(Contractor).order_by(Contractor.name.desc()).paginate(per_page=30, page=page_num)
        else:
            flash("Not a Valid Sort Type", 'danger')
            return redirect('/home')

        return render_template('/jobs/jobs.html',jobs=jobs, user=current_user, sort_by= sort_type)

    flash('Please Sign In First', 'danger')
    return redirect('/')
##### Other Admin Page Routes ######

@app.route('/admin_page')
def admin_page():
    """ Page for admin tools """

    if current_user.is_authenticated:
        form = adminPageForm()
        edgeform=EdgeForm()
        sections={}
        vendors= Vendor.query.all()
        sections['vendors']=vendors
        colors=Color.query.all()
        sections['colors']=colors
        slabtypes=Slab_Type.query.all()
        sections['slabtypes']=slabtypes
        contractors=Contractor.query.all()
        sections['contractors']=contractors
        cutouts=Cutout.query.all()
        sections['cutouts']=cutouts
        edges=Edge.query.all()
        sections['edges']=edges
        users=User.query.all()
        sections['users']=users

        return render_template('/users/admin_page.html', form=form, edgeform=edgeform, sections=sections, user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/vendors/add', methods=['POST'])
def create_vendor():
    """ create a vendor """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            try:
                vendor=Vendor(id=form.id.data,name=form.name.data)
                db.session.add(vendor)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Vendor Already Exists','danger')
                return redirect ('/vendors/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

    

@app.route('/colors/add', methods=['POST'])
def create_color():
    """ create a slab color """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            try:
                color=Color(id=form.id.data,name=form.name.data)
                db.session.add(color)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Slab Color Already Exists','danger')
                return redirect ('/colors/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/slabtypes/add', methods=['POST'])
def create_slabtype():
    """ create a slab type """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            try:
                slabtype=Slab_Type(id=form.id.data,name=form.name.data)
                db.session.add(slabtype)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Slab Type Already Exists','danger')
                return redirect ('/slabtypes/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/contractors/add', methods=['POST'])
def create_contractor():
    """ create a contractor """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            try:
                contractor=Contractor(id=form.id.data,name=form.name.data)
                db.session.add(contractor)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Contractor Already Exists','danger')
                return redirect ('/contractors/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/cutouts/add', methods=['POST'])
def create_cutout():
    """ create a cutout """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            try:
                cutout=Cutout(id=form.id.data,name=form.name.data)
                db.session.add(cutout)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Cutout Already Exists','danger')
                return redirect ('/cutouts/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/edges/add', methods=['POST'])
def create_edge():
    """ create a edge """
    if current_user.is_authenticated:
    
        form=EdgeForm()
        if form.validate_on_submit():
            try:
                edge=Edge(id=form.id.data,name=form.name.data, type=form.type.data)
                db.session.add(edge)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                flash('Edge Detal Already Exists','danger')
                return redirect ('/edges/add')
            return redirect('/admin_page')

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/admin/<section>/<int:id>/delete')
def deleteitem(section,id):
    """ delete item from admin page and db """

    if current_user.is_authenticated:
        
        if section=='vendors':
            to_be_deleted=Vendor.query.get(id)
        elif section=='colors':
            to_be_deleted=Color.query.get(id)
        elif section=='slabtypes':
            to_be_deleted=Slab_Type.query.get(id)
        elif section=='contractors':
            to_be_deleted=Contractor.query.get(id)
        elif section=='cutouts':
            to_be_deleted=Cutout.query.get(id)
        elif section=='edges':
            to_be_deleted=Edge.query.get(id)
        else:
            flash('That item cannot be deleted', 'danger')
        db.session.delete(to_be_deleted)
        db.session.commit()
        return redirect('/admin_page')
    
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/users/<int:id>/delete')
def deleteaccount(id):
    """ Delete account cannot delete admin """

    if current_user.is_authenticated:
        if id == 1:
            flash('Sorry You cannot delete the admin account', 'danger')
            return redirect('/admin_page')
        else:
            user = User.query.get(id)
            db.session.delete(user)
            db.session.commit()
            flash('Account Deleted', 'success')
            return redirect('/admin_page')
    
    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/barcodes/<int:page_num>')
def barcodes(page_num):
    """ select barcodes to print """
    if current_user.is_authenticated:
        slabs=Slab.query.order_by(Slab.created.desc()).paginate(per_page=15, page=page_num)
        return render_template('/slabs/barcodes.html', slabs=slabs, user=current_user)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/barcodes/print', methods=['POST'])
def print_barcodes():
    """ print friendly multiple bacodes """
    if current_user.is_authenticated:
        barcodes=request.form.getlist('barcode')
        slabs=Slab.query.filter(Slab.label.in_(barcodes)).all()
        return render_template('/slabs/print_barcodes.html', slabs=slabs)

    flash('Please Sign In First', 'danger')
    return redirect('/')

@app.route('/Reports')
def reports():
    """ reports page """

    if current_user.is_authenticated:
        week = datetime.today() - timedelta(days = 8)

        jobs= Job.query.filter(Job.installation_date>=week, Job.installation_date<=datetime.today() ).all()
        edge_totals=total_lf_job(jobs)
        data=get_report(jobs)
        return render_template('/users/reports.html', jobs=jobs, user=current_user, data=data, edgeslf=edge_totals) 


    flash('Please Sign In First', 'danger')
    return redirect('/')