import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Brand, Choice, Record
from app.forms import LoginForm
from app.forms import RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "test.db")
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all() 
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    #HELPER FUNCTIONS
    def register(self, username, email, password, password2, preference):
        return self.app.post("/register", data=dict(username=username, 
        email=email,
        password=password,
        password2=password2,
        preference=preference),
        follow_redirects = True)

    def login(self, username, password):
        return self.app.post("/register", data=dict(username=username,
        password=password), follow_redirects = True)
    
#REGISTRATION FUNCTIONALITY TESTS
    #Tests a valid registration attempt
    def test_valid_registration(self):
        response = self.register("user", "user@email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)
    
    #Tests an invalid registration attempt where passwords do not match
    def test_invalid_registration_passwords(self):
        response = self.register("user", "grae@email.com", "password", "invalid password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be equal to password', response.data)

    #Tests an invalid registration attempt where email is invalid
    def test_invalid_registration_email(self):
        #missing @ symbol
        response = self.register("user", "invalid email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email address', response.data)

        #missing domain
        response = self.register("user", "invalid@email", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email address', response.data)

        #invalid space inserted
        response = self.register("user", "invalid@ email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email address', response.data)
    
    #Tests an invalid registration where the username and/or email are already taken
    def test_invalid_registration_duplicates(self):
        u1 = User(username = "existing_user", email = "existing_user@email.com", preference = "lambo")
        db.session.add(u1)
        db.session.commit()

        #duplicate username
        response = self.register("existing_user", "user@email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User name has been used', response.data)

        #duplicate email
        response = self.register("user", "existing_user@email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email has been used', response.data)
    
    #Tests an invalid registration where one of the fields has been left blank
    def test_invalid_registration_missing(self):
        response = self.register("", "user@email.com", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data) #redirected to register page
        self.assertIn(b'value=""', response.data) #at least 1 field has been left empty

        response = self.register("user", "", "password", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

        response = self.register("user", "user@email.com", "", "password", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

        response = self.register("user", "user@email.com", "password", "", "Lambo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

#LOGIN FUNCTIONALITY TESTS
    #Tests functionality of password check at login
    def test_login_password(self):
        u1 = User(username="Grae", email="grae@hotmail.com", preference="Lambo")
        u1.set_password('password')
        self.assertFalse(u1.check_password('invalid password'))
        self.assertTrue(u1.check_password('password'))
        db.session.add(u1)
        db.session.commit()
        user = User.query.filter_by(username='Grae')
        
        response = self.login("Grae", "password")
        self.assertEqual(response.status_code, 200)
        #self.assertIn(b'Hello, Grae', response.data)
        print(response.data)

    

    if __name__ == '__main__':
        unittest.main()
