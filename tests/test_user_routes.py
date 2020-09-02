import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from unittest import TestCase
from app import app, current_user
from models import *

app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///BBCG_test'


class UserRouteTestCase(TestCase):
    """ Tests for user routes """

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        user_type=User_Type(type='admin')
        db.session.add(user_type)
        db.session.commit()

        self.testuser = User.signup(username="admin", password="testuser", type_id=1)

        self.testuser_id=1
        self.testuser.id=self.testuser_id

        vendor = Vendor(id=1, name="test_vendor")
        color = Color(id=1, name='test_color')
        slabtype = Slab_Type(id=1, name='test_slab_type')

        test_models = [vendor, color, slabtype]

        db.session.add_all(test_models)

        db.session.commit()
        
        slab= Slab(vendor_id=1,color_id=1, batch_num=1, slab_num=1, type_id=1)
        slab.label=1111
        db.session.add(slab)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_login(self):
        """ test login page"""
        
        with self.client as c:
            resp = c.get('/', follow_redirects=True)
            
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/', follow_redirects=True)
            self.assertIn('admin', str(resp.data))
            self.assertIn('slabs', str(resp.data))

    def test_scan(self):
        """ test scan page """
        

        with self.client as c:

            resp = c.get('/scan', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/scan', follow_redirects=True)
            self.assertIn('admin', str(resp.data))
            self.assertIn('scan', str(resp.data))

    def test_recieve(self):
        """ test recieving page """

        with self.client as c:
            resp = c.get('/recieve', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/recieve', follow_redirects=True)
            self.assertIn('admin', str(resp.data))
            self.assertIn('Recieve New Slab', str(resp.data))
            self.assertIn('Picture', str(resp.data))
            self.assertIn('Batch Number', str(resp.data))
            self.assertIn('Slab Number', str(resp.data))

    def test_cut_slab(self):
        """ test cut slab page """

        with self.client as c:
            resp = c.get('/cut_slab/1111', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/cut_slab/1111', follow_redirects=True)
            self.assertIn('Enter', str(resp.data))
            self.assertIn('Amount Left', str(resp.data))
            resp = c.get('/cut_slab/112222', follow_redirects=True)
            self.assertIn('Barcode #', str(resp.data))

    def test_slab_page(self):
        """ test  slab page """

        with self.client as c:
            resp = c.get('/slab/1111', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/slab/1111', follow_redirects=True)
            self.assertIn('test_vendor', str(resp.data))
            self.assertIn('test_color', str(resp.data))
            self.assertIn('Square Feet', str(resp.data))
            resp = c.get('/slab/112222', follow_redirects=True)
            self.assertIn('Barcode #', str(resp.data))

    def test_edit_slab_page(self):
        """ test edit slab page """

        with self.client as c:
            resp = c.get('/slab/1111', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/slab/1111/edit', follow_redirects=True)
            self.assertIn('test_vendor', str(resp.data))
            self.assertIn('test_color', str(resp.data))
            resp = c.get('/slab/112222/edit', follow_redirects=True)
            self.assertIn('Barcode #', str(resp.data))