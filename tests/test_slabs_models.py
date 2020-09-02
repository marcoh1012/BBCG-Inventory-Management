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

class SlabModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """ Set up slab for testing cases """
        db.drop_all()
        db.create_all()

        vendor = Vendor(id=1, name="test_vendor")
        color = Color(id=1, name='test_color')
        slabtype = Slab_Type(id=1, name='test_slab_type')

        test_models = [vendor, color, slabtype]

        db.session.add_all(test_models)

        
    def tearDown(self):
        db.session.rollback()

    def test_vendor_model(self):
        """ Test vendor model create/get"""

        result = Vendor.query.all()
        self.assertEqual(len(result),1)

        result = Vendor.query.get(1)
        self.assertEqual(result.name, 'test_vendor')



    def test_slab_type_model(self):
        """ Test slab type model create/get"""

        result = Slab_Type.query.all()
        self.assertEqual(len(result),1)
        
        result = Slab_Type.query.get(1)
        self.assertEqual(result.name, 'test_slab_type')


    def test_color_model(self):
        """ Test color model create/get"""

        result = Color.query.all()
        self.assertEqual(len(result),1)
        
        result = Color.query.get(1)
        self.assertEqual(result.name, 'test_color')

    def test_slab_model(self):
        """ Tests for slab model """

        slab= Slab(vendor_id=1,color_id=1, batch_num=1, slab_num=1, type_id=1)
        db.session.add(slab)
        db.session.commit()

        test_slab=Slab.query.all()
        self.assertEqual(len(test_slab),1)
        self.assertEqual(slab.vendor_id,1)
        self.assertEqual(slab.color_id,1)
        self.assertEqual(slab.batch_num,1)
        self.assertEqual(slab.slab_num,1)
        self.assertEqual(slab.type_id,1)


    def test_slab_functions(self):
        """ Tests for functions in slab model """

        slab= Slab(vendor_id=1,color_id=1, batch_num=1, slab_num=1, length=12, width=12, type_id=1)
        db.session.add(slab)
        db.session.commit()

        test_slab=Slab.query.first()
        self.assertEqual(test_slab.calculate_area(),1)
        self.assertEqual(test_slab.amount_left,100)
        test_slab.cut_slab(50)
        self.assertEqual(test_slab.amount_left,50)
        self.assertEqual(test_slab.vendor.id,1)
        self.assertEqual(test_slab.color.id,1)
        self.assertEqual(test_slab.type.id,1)