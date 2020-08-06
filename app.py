import os
import requests
import shutil
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from models import *
from forms import *

# CURR_USER_KEY = "curr_user"

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/BBCG'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///BBCG'
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
            User.signup(form.username.data,form.password.data,form.type.data)
            db.session.commit()
            flash('User Created','sucess')
            return redirect('/slabs/1')
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
    user_type=current_user.user_type.type.lower()
    if user_type == 'reciever':
        return redirect('/recieve')
    if user_type == 'fabricator':
        return redirect('/scan')
    slabs=Slab.query.paginate(per_page=20, page=page_num)
    # raise
    return render_template(f'slabs/slabs.html', slabs=slabs, user=current_user, sort_by=None)
    
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
            flash('Slab Found', "success")
            return redirect(f'/cut_slab/{slab.label}')
        return render_template('slabs/scan.html', form=form, user=current_user)
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
            flash('Success', 'success')
            return redirect(f'/scan')
        return render_template('slabs/cut_slab.html', form=form, slab=slab,user=current_user)
    return redirect('/home')

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
            flash("No Slab Found", 'danger')
            return redirect('/scan')
        if form.validate_on_submit():
            slab.length = form.length.data
            slab.width = form.width.data 
            slab.type_id = form.type_id.data
            if form.picture.data:
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
            slab.label = slab.create_label_id()
            db.session.commit()


            return redirect(f'/slab/{slab.label}')
                
        return render_template('/slabs/recieve.html', form = form,user=current_user)

    return redirect('/')

@app.route('/slab/<int:id>/delete')
def deleteSlab(id):
    """ delete slab """

    slab=Slab.query.filter(Slab.label==id).first()
    db.session.delete(slab)
    db.session.commit()
    return redirect('/home')


@app.route('/job/new', methods=['GET','POST'])
def newJob():
    """ create new job """

    if current_user.is_authenticated:
        form=JobForm()
        contractors=[(str(i.id),i.name) for i in Contractor.query.all()]
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
            flash('Success: Job Added', 'success')
            return redirect(f'/job/{job.id}')

        return render_template('jobs/new_job.html', form=form, user=current_user)

    return redirect('/')

@app.route('/job/<int:id>/edit', methods=['GET','POST'])
def editJob(id):
    """ edit existing job """

    if current_user.is_authenticated:
        job=Job.query.join(JobEdge).join(Edge).filter(Job.id==id).first()
        form=JobForm(obj=job)
        contractors=[(str(i.id),i.name) for i in Contractor.query.all()]
        form.contractor_id.choices=contractors
        if form.validate_on_submit():
            job.name=form.name.data
            job.po_number=form.po_number.data
            job.contractor_id=form.contractor_id.data
            job.square_feet=form.sf.data
            job.installation_date=form.installation_date.data
            job.fabrication_date=form.fabrication_date.data
            job.notes=form.notes.data
            db.session.commit()
            flash('Job Edited', 'success')
            return redirect(f'/job/{id}')
        return render_template('/jobs/edit_job.html', form = form, user=current_user)

    
    return redirect('/')

@app.route('/jobs/<int:page_num>')
def view_jobs(page_num):
    """ view all jobs """
    jobs=Job.query.paginate(per_page=30, page=page_num)
    return render_template('/jobs/jobs.html',jobs=jobs, user=current_user,sort_by=None)

@app.route('/job/<int:id>/delete')
def delete_job(id):
    """ delete job """

    job=Job.query.get(id)
    db.session.delete(job)
    db.session.commit()
    return redirect('/jobs/1')


########## Job Page routes ##########
@app.route('/job/<int:id>')
def view_job(id):
    job=Job.query.get_or_404(id)
    cutouts= db.session.query(Cutout.name, JobCutout.cutout_count,JobCutout.id).filter(JobCutout.job_id==job.id).join(Cutout).all()
    edges = db.session.query(JobEdge.lf, Edge.name, JobEdge.id).filter(JobEdge.job_id==job.id).join(Edge).all()
    slabform=ScanBarcodeForm()
    cutoutform=AddCutoutForm()
    cutoutform.cutout.choices = [(str(i.id),i.name) for i in Cutout.query.all()]
    edgeform=AddEdgeForm()
    edgeform.edge.choices = [(str(i.id),i.name) for i in Edge.query.all()]
    forms=[slabform,cutoutform,edgeform]
    return render_template('/jobs/job.html', job=job, cutouts=cutouts, edges=edges, forms=forms, user=current_user)

@app.route('/job/<int:id>/addslab', methods=['POST'])
def add_slab(id):
    """ Add slab to job """

    if current_user.is_authenticated:    
        form = ScanBarcodeForm(request.form)
        if form.validate_on_submit():
            SJ=SlabJob(slab_id=form.label.data,job_id=id)
            db.session.add(SJ)
            db.session.commit()
            flash('Slab Added','success')
            return redirect(f'/job/{id}')
    flash('Error Occured, Try Again', 'danger')
    return redirect(f'/job/{id}')

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

@app.route('/job/<int:id>/slab/<int:label>/delete')
def remove_JobSlab(id, label):
    """ remove relationship from slabjob """

    slab=Slab.query.filter(Slab.label==label).first()
    SJ = SlabJob.query.filter(SlabJob.job_id==id, SlabJob.slab_id==label).first()
    slab.amount_left=slab.amount_left + SJ.percent_used
    db.session.delete(SJ)
    db.session.commit()
    return redirect(f'/job/{id}')

@app.route('/job/<int:id>/cutout/<int:cutout_id>/delete')
def remove_JobCutout(id, cutout_id):
    """ remove relationship from jobcutout """
    JC=JobCutout.query.filter(JobCutout.job_id==id, JobCutout.cutout_id==cutout_id).first()
    db.session.delete(JC)
    db.session.commit()
    return redirect(f'/job/{id}')

@app.route('/job/<int:id>/edge/<int:edge_id>/delete')
def remove_JobEdge(id, edge_id):
    """ remove relationship from jobedge """
    JE=JobEdge.query.filter(JobEdge.job_id==id, JobEdge.edge_id==edge_id).first()
    db.session.delete(JE)
    db.session.commit()
    return redirect(f'/job/{id}')


######### Sorting Routes########
@app.route('/slabs/search/<int:page_num>', methods=['GET','POST'])
def search_slabs(page_num):
    """ search for slabs with keywords """

    if current_user.is_authenticated:
        term=request.form.get('search-term')
        return redirect(f'/slabs/search/{term}/{page_num}')

        

@app.route('/slabs/search/<term>/<int:page_num>')
def search_slabs_term(term,page_num):
    """ search for slabs with keywords and pagination """

    if current_user.is_authenticated:  
        if term.isnumeric():
             full_results=Slab.query.filter(Slab.label==term).paginate(per_page=20,page=page_num, error_out=False)
        else:
            full_results=Slab.query.join(Vendor).join(Color).join(Slab_Type).filter(or_(Vendor.name.ilike(term), Color.name.ilike(term),Slab_Type.name.ilike(term))).paginate(per_page=16,page=page_num, error_out=False)
        
        return render_template('/slabs/slabs.html', slabs=full_results, user=current_user, sort_by='search', search_term=term)

       
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
            return redirect('/home')

        return render_template('/slabs/slabs.html',slabs=slabs, user=current_user, sort_by= sort_type)

@app.route('/jobs/search/<int:page_num>', methods=['POST'])
def search_jobs(page_num):
    """ search for slabs with keywords """

    if current_user.is_authenticated:
        term=request.form.get('search-term')
        return redirect(f'/jobs/search/{term}/{page_num}')

@app.route('/jobs/search/<term>/<int:page_num>')
def search_jobs_term(term,page_num):
    """ search jobs useing term """
    full_results=Job.query.join(Contractor).join(JobEdge).join(Edge).filter(or_(Job.name.ilike(term),Contractor.name.ilike(term),(Edge.name.ilike(term)))).paginate(per_page=16,page=page_num, error_out=False)
    
    return render_template('/jobs/jobs.html', jobs=full_results, user=current_user, sort_by='search', search_term=term)


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

@app.route('/Reports')
def reports():
    """ reports page """

    return render_template('/users/reports.html', user=current_user)

@app.route('/vendors/add', methods=['POST'])
def create_vendor(option):
    """ create a vendor """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            vendor=Vendor(id=form.id.data,name=form.name.data)
            db.session.add(vendor)
            db.session.commit()
            return redirect('/admin_page')

@app.route('/colors/add', methods=['POST'])
def create_color():
    """ create a slab color """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            color=Color(id=form.id.data,name=form.name.data)
            db.session.add(color)
            db.session.commit()
            return redirect('/admin_page')

@app.route('/slabtypes/add', methods=['POST'])
def create_slabtype():
    """ create a slab type """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            slabtype=Slab_Type(id=form.id.data,name=form.name.data)
            db.session.add(slabtype)
            db.session.commit()
            return redirect('/admin_page')

@app.route('/contractors/add', methods=['POST'])
def create_contractor():
    """ create a contractor """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            contractor=Contractor(id=form.id.data,name=form.name.data)
            db.session.add(contractor)
            db.session.commit()
            return redirect('/admin_page')

@app.route('/cutouts/add', methods=['POST'])
def create_cutout():
    """ create a cutout """

    if current_user.is_authenticated:
    
        form=adminPageForm()
        if form.validate_on_submit():
            cutout=Cutout(id=form.id.data,name=form.name.data)
            db.session.add(cutout)
            db.session.commit()
            return redirect('/admin_page')

@app.route('/edges/add', methods=['POST'])
def create_edge():
    """ create a edge """
    if current_user.is_authenticated:
    
        form=EdgeForm()
        if form.validate_on_submit():
            edge=Edge(id=form.id.data,name=form.name.data, type=form.type.data)
            db.session.add(edge)
            db.session.commit()
            return redirect('/admin_page')