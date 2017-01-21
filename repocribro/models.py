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


class RepositoryOwner(db.Model):
    """RepositoryOwner (User or Organization) from GitHub"""
    __tablename__ = 'RepositoryOwner'
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True)
    login = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(255))
    name = db.Column(db.UnicodeText)
    company = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)
    location = db.Column(db.UnicodeText)
    blog_url = db.Column(db.UnicodeText)
    avatar_url = db.Column(db.String(255))
    type = db.Column(db.String(30))
    repositories = db.relationship('Repository', back_populates="owner")
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'RepositoryOwner'
    }


class User(RepositoryOwner):
    """User from GitHub"""
    hireable = db.Column(db.Boolean)
    user_account_id = db.Column(db.Integer, db.ForeignKey('UserAccount.id'))
    user_account = db.relationship(
        'UserAccount',
        back_populates='github_user'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'User'
    }

    def __init__(self, github_id, login, email, name, company, location,
                 bio, blog_url, avatar_url, hireable, user_account):
        self.github_id = github_id
        self.login = login
        self.email = email
        self.name = name
        self.company = company
        self.location = location
        self.description = bio
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


class Organization(RepositoryOwner):
    """Organization from GitHub"""

    def __init__(self, github_id, login, email, name, company, location,
                 description, blog_url, avatar_url):
        self.github_id = github_id
        self.login = login
        self.email = email
        self.name = name
        self.company = company
        self.location = location
        self.description = description
        self.blog_url = blog_url
        self.avatar_url = avatar_url

    @staticmethod
    def create_from_dict(org_dict):
        return Organization(
            org_dict['id'],
            org_dict['login'],
            org_dict['email'],
            org_dict['name'],
            org_dict['company'],
            org_dict['location'],
            org_dict['description'],
            org_dict['blog'],
            org_dict['avatar_url']
        )

    def __repr__(self):
        return '<GH Organization {} ({})>'.format(self.login, self.github_id)

    __mapper_args__ = {
        'polymorphic_identity': 'Organization'
    }


class Repository(db.Model):
    """Repository from GitHub"""
    __tablename__ = 'Repository'
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True)
    fork_of = db.Column(db.Integer)
    full_name = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(100))
    languages = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)
    private = db.Column(db.Boolean)
    visibility_type = db.Column(db.Integer)
    secret = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('RepositoryOwner.id'))
    owner = db.relationship('RepositoryOwner', back_populates='repositories')

    VISIBILITY_PUBLIC=0
    VISIBILITY_PRIVATE=1
    VISIBILITY_HIDDEN=2

    def __init__(self, github_id, fork_of, full_name, name, languages,
                 description, private, owner, visibility_type, secret):
        self.github_id = github_id
        self.fork_of = fork_of
        self.full_name = full_name
        self.name = name
        self.languages = languages
        self.description = description
        self.private = private
        self.visibility_type = visibility_type
        self.secret = secret

    @staticmethod
    def create_from_dict(repo_dict, owner,
                         visibility_type = 0, secret = None):
        fork_of = None
        if 'parent' in repo_dict:
            fork_of = repo_dict['parent']['id']
        return Repository(
            repo_dict['id'],
            fork_of,
            repo_dict['full_name'],
            repo_dict['name'],
            repo_dict['language'],
            repo_dict['description'],
            repo_dict['private'],
            owner,
            visibility_type,
            secret
        )

    def is_public(self):
        return self.visibility_type == self.VISIBILITY_PUBLIC

    def is_private(self):
        return self.visibility_type == self.VISIBILITY_PRIVATE

    def is_hidden(self):
        return self.visibility_type == self.VISIBILITY_HIDDEN

    def __repr__(self):
        return '<GH Repository {} ({})>'.format(self.full_name, self.github_id)

