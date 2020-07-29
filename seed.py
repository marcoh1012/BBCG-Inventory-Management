from app import app, db
from models import User, connect_db, User_Type

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@127.0.0.1:5432/BBCG'

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
