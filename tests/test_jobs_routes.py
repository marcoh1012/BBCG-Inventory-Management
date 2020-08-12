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

        contractor = Contractor(id=1, name='test contractor')

        db.session.add(contractor)

        db.session.commit()
        
        test_job = Job(id=1, name='test job', contractor_id=1)
        db.session.add(test_job)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_new_job(self):
        """ test new job page """

        with self.client as c:

            resp = c.get('/job/new', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/job/new', follow_redirects=True)
            self.assertIn('Add New Job', str(resp.data))
            self.assertIn('Name', str(resp.data))
            self.assertIn('Enter', str(resp.data))

    def test_edit_job(self):
        """ test edit job page """

        with self.client as c:

            resp = c.get('/job/1/edit', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/job/1/edit', follow_redirects=True)
            self.assertIn('Edit Job', str(resp.data))
            self.assertIn('Name', str(resp.data))
            self.assertIn('PO Number', str(resp.data))

    def test_jobs_page(self):
        """ test jobs page """

        with self.client as c:

            resp = c.get('/jobs/1', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/jobs/1', follow_redirects=True)
            self.assertIn('test job', str(resp.data))
            self.assertIn('jobs', str(resp.data))
            self.assertIn('PO Number', str(resp.data))

    def test_view_job(self):
        """ test jobs page """

        with self.client as c:

            resp = c.get('/job/1', follow_redirects=True)
        
            self.assertIn('Please Sign In First', str(resp.data))
            self.assertIn('username',str(resp.data))
            self.assertIn('password',str(resp.data))

            resp = c.post('/login', data={'username': 'admin', 'password': 'testuser'})
            self.assertEqual(resp.status_code,302)
            resp = c.get('/job/1', follow_redirects=True)
            self.assertIn('TEST JOB', str(resp.data))
            self.assertIn('Slabs', str(resp.data))
            self.assertIn('Cutouts', str(resp.data))
            self.assertIn('Edges', str(resp.data))
            self.assertIn('PO Number', str(resp.data))