import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from unittest import TestCase
from app import app
from models import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///BBCG_test'

db.drop_all()
db.create_all()

class JobsModelTestCase(TestCase):
    

    def setUp(self):
        """ Set up slab for testing cases """
        db.drop_all()
        db.create_all()

        contractor = Contractor(id=1,name='test contractor')
        cutout = Cutout(id=1, name = 'test cutout')
        edge = Edge(id=1, name='test edge', type='test type')

        tests=[contractor, cutout, edge]
        db.session.add_all(tests)
        db.session.commit()

        
    def tearDown(self):
        db.session.rollback()

    def test_contractor_model(self):
        """ Test contractor model create/get"""

        result = Contractor.query.all()
        self.assertEqual(len(result),1)

        result = Contractor.query.get(1)
        self.assertEqual(result.name, 'test contractor')

    def test_cutout_model(self):
        """ Test cutout model create/get"""

        result = Cutout.query.all()
        self.assertEqual(len(result),1)

        result = Cutout.query.get(1)
        self.assertEqual(result.name, 'test cutout')

    def test_edge_model(self):
        """ Test edge model create/get"""

        result = Edge.query.all()
        self.assertEqual(len(result),1)

        result = Edge.query.get(1)
        self.assertEqual(result.name, 'test edge')

    def test_job_model(self):
        """ Test job model """
        vendor = Vendor(id=1, name="test_vendor")
        color = Color(id=1, name='test_color')
        slabtype = Slab_Type(id=1, name='test_slab_type')

        test_models = [vendor, color, slabtype]

        db.session.add_all(test_models)
        slab= Slab(vendor_id=1,color_id=1, batch_num=1, slab_num=1, length=12, width=12, type_id=1)
        slab.label=1111
        db.session.add(slab)
        db.session.commit()
        test_job = Job(id=1, name='test job', contractor_id=1)
        db.session.add(test_job)
        db.session.commit()
        je=JobEdge(job_id=1, edge_id=1)
        jc=JobCutout(job_id=1, cutout_id=1)
        sj=SlabJob(job_id=1, slab_id=1111)

        tests=[je, jc, sj]

        db.session.add_all(tests)
        db.session.commit()

        job=Job.query.get(1)
        self.assertEqual(job.name,'test job')
        self.assertEqual(job.contractor.name, 'test contractor')
        self.assertEqual(len(job.edges),1)
        self.assertEqual(job.edges[0].name, 'test edge')
        self.assertEqual(len(job.cutouts),1)
        self.assertEqual(job.cutouts[0].name, 'test cutout')
        self.assertEqual(len(job.slabs),1)
        self.assertEqual(job.slabs[0].vendor.name, 'test_vendor')
        self.assertEqual(job.slabs[0].color.name, 'test_color')