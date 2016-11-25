from flask_pymongo import PyMongo


class User():


    def __init__(self,email,password, confirmed,paid=False,admin=False,confirmed_on =None):
        self.email = email
        self.password = password
        self.confirmed = confirmed
        self.paid = paid
        self.admin = admin
        self.confirmed_on = confirmed_on

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


