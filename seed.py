from app import app, db
from models import *

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@127.0.0.1:5432/BBCG'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///BBCG')

connect_db(app)

db.drop_all()
db.create_all()

admin = User_Type(type='Admin')
reciever = User_Type(type='Reciever')
fabricator = User_Type(type='Fabricator')
office = User_Type(type='Office')

user_types = [admin, reciever, fabricator, office]
db.session.add_all(user_types)

user1 = User.signup('admin', 'password', '1')
db.session.add(user1)
db.session.commit()

v1 = Vendor(name='Vicostone')
v2 = Vendor(name='Calaccata')

db.session.add(v1)
db.session.add(v2)

c1 = Color(name='Storm')
c2 = Color(name='Absolute White')

db.session.add(c1)
db.session.add(c2)

st1 = Slab_Type(name='Granite')
st2 = Slab_Type (name='Quartz')

db.session.add(st1)
db.session.add(st2)

slab1 = Slab(vendor_id='1',
   color_id='1',
   batch_num='1',
   slab_num='1',
   length='120',
   width='80',
   type_id='2'
)
db.session.add(slab1)
db.session.commit()
slab1 = Slab.query.first()
slab1.label=slab1.create_label_id()
db.session.commit()

c1=Contractor(name = 'BBCG')

kit_cutout = Cutout(name='Kitchen SinK')
bath_cutout = Cutout(name = 'Bath Cutout')

square = Edge(name='Square', type = 'Standard')
bevel = Edge(name='Bevel', type = 'Standard')

job = Job(
    name='test',
    square_feet='80.0',
    notes='This is just a test',
    contractor_id = '1',
)

models = [c1, kit_cutout, bath_cutout, square, bevel,job]
db.session.add_all(models)
db.session.commit()

jc=JobCutout(job_id=1,cutout_id=1,cutout_count=1)
jc2=JobCutout(job_id=1,cutout_id=2,cutout_count=4)
je=JobEdge(job_id=1,edge_id=2, lf='54.2')
# sl=SlabJob(slab_id=1111,job_id=1)

models = [jc, jc2, je]
db.session.add_all(models)
db.session.commit()