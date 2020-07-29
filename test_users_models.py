from unittest import TestCase
from app import app
from models import db, User, User_Type

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/BBCG_test'

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        User_Type.query.delete()
        type = User_Type(type='test')
        self.type=type

        db.session.add(type)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
   
    def test_user_model(self):
        """Test basic user model"""

        u = User(
            username="test",
            password="testuser"
        )

        db.session.add(u)
        db.session.commit()

        self.assertIsNone(u.user_type_id)

    def test_signup(self):
        """ test a sign up new user """

        User.signup('testuser','password',self.type.id)
        db.session.commit()

        u = User.query.first()
        self.assertEqual(u.username,'testuser')
        self.assertEqual(u.user_type.type,self.type.type)

    def test_authenticate(self):
        """ test authenticating a user """
        
        User.signup('testuser','password',self.type.id)
        db.session.commit()

        u = User.authenticate('testuser', 'password')
        self.assertEqual(u.username,'testuser')
        self.assertEqual(u.user_type.type,self.type.type)

        u = User.authenticate('testuser', 'wrongpassword')
        self.assertFalse(u)
        
    def test_user_type(self):
        """ test creating user types """

        t = User_Type.query.all()

        self.assertEqual(len(t),1)
        self.assertEqual(t[0].type,'test')

    def test_user_with_type(self):
        """ test user attached to correct type """

        u = User(
            username="test",
            password="testuser",
            user_type_id=self.type.id
        )

        db.session.add(u)
        db.session.commit()

        user=User.query.get(u.id)

        self.assertIsNotNone(user.user_type)
        self.assertEqual(user.user_type.type,'test')