# TODO: rearrange app structure
from flask_sqlalchemy import SQLAlchemy
import flask_login
import datetime

db = SQLAlchemy()


# Example model for Flask-SQLAlchemy
class UserAccount(db.Model, flask_login.UserMixin):
    """UserAccount in the repocribro app"""
    __tablename__ = 'UserAccount'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    github_user = db.relationship(
        'User',
        uselist=False,
        back_populates='user_account'
    )

    def __repr__(self):
        return '<UserAccount {}>'.format(id)


class User(db.Model):
    """User from GitHub"""
    __tablename__ = 'GH_User'
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True)
    login = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(255))
    name = db.Column(db.UnicodeText)
    company = db.Column(db.UnicodeText)
    location = db.Column(db.UnicodeText)
    bio = db.Column(db.UnicodeText)
    blog_url = db.Column(db.UnicodeText)
    avatar_url = db.Column(db.String(255))
    hireable = db.Column(db.Boolean)
    user_account_id = db.Column(db.Integer, db.ForeignKey('UserAccount.id'))
    user_account = db.relationship(
        'UserAccount',
        back_populates='github_user'
    )

    def __init__(self, github_id, login, email, name, company, location,
                 bio, blog_url, avatar_url, hireable, user_account):
        self.github_id = github_id
        self.login = login
        self.email = email
        self.name = name
        self.company = company
        self.location = location
        self.bio = bio
        self.blog_url = blog_url
        self.avatar_url = avatar_url
        self.hireable = hireable
        self.user_account = user_account

    @staticmethod
    def create_from_dict(user_dict, user_account):
        return User(
            user_dict['id'],
            user_dict['login'],
            user_dict['email'],
            user_dict['name'],
            user_dict['company'],
            user_dict['location'],
            user_dict['bio'],
            user_dict['blog'],
            user_dict['avatar_url'],
            user_dict['hireable'],
            user_account
        )

    def __repr__(self):
        return '<GH User {} ({})>'.format(self.login, self.github_id)
