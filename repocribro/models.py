import flask_sqlalchemy
import sqlalchemy
import flask_login
import datetime

from .database import db

Base = flask_sqlalchemy.declarative_base()

# TODO: docstrings for attributes


class SearchableMixin:
    """Mixin for models that support fulltext query"""

    #: List of names of string/text attributes used for fulltext
    __searchable__ = []

    @classmethod
    def fulltext_query(cls, query_str, db_query):
        """Add fulltext filter to the DB query

        :param query_str: String to be queried
        :type query_str: str
        :param db_query: Database query object
        :type db_query: ``sqlalchemy.orm.query.Query``
        :return: Query with fulltext filter added
        :rtype: ``sqlalchemy.orm.query.Query``
        """
        query_str = '%{}%'.format(query_str)
        condition = sqlalchemy.or_(
            *[getattr(cls, col).like(query_str) for col in cls.__searchable__]
        )
        return db_query.filter(condition)


class RoleMixin:
    """Mixin for models representing roles"""

    def __eq__(self, other):
        """Equality of roles is based on names

        :param other: Role or its name to be compared with
        :type other: ``repocribro.models.RoleMixin`` or str
        :return: If names are equal
        :rtype: bool
        """
        return (self.name == other or
                self.name == getattr(other, 'name', None))

    def __ne__(self, other):
        """Inequality of roles is based on names

        :param other: Role or its name to be compared with
        :type other: ``repocribro.models.RoleMixin`` or str
        :return: If names are not equal
        :rtype: bool
        """
        return not self.__eq__(other)

    def __hash__(self):
        """Standard hashing via name

        :return: Hash of role
        :rtype: int
        """
        return hash(self.name)


class Anonymous(flask_login.AnonymousUserMixin):
    """Anonymous (not logged) user representation"""

    @property
    def is_active(self):
        """Check whether is user active

        :return: False, anonymous is not active
        :rtype: bool
        """
        return False

    def has_role(self, role):
        """Check whether has the role

        :param role: Role to be checked
        :type role: ``repocribro.models.RoleMixin``
        :return: False, anonymous has no roles
        :rtype: bool
        """
        return False

    @property
    def rolenames(self):
        """Get names of all roles of that user

        :return: Empty list, anonymous has no roles
        :rtype: list of str
        """
        return []

    def owns_repo(self, repo):
        """Check if user owns the repository

        :param repo: Repository which shoudl be tested
        :type repo: ``repocribro.models.Repository``
        :return: False, anonymous can not own repository
        :rtype: bool
        """
        return False

    def sees_repo(self, repo):
        """Check if user is allowed to see the repo

        Anonymous can see only public repos

        :param repo: Repository which user want to see
        :type repo: ``repocribro.models.Repository``
        :return: If user can see repo
        :rtype: bool
        """
        return repo.is_public


class UserMixin(flask_login.UserMixin):

    @property
    def is_active(self):
        """Check whether is user active

        :return: If user is active (can login)
        :rtype: bool
        """
        return self.active

    def has_role(self, role):
        """Check whether has the role

        :param role: Role to be checked
        :type role: str
        :return: If user has a role
        :rtype: bool
        """
        return role in (role.name for role in self.roles)

    @property
    def rolenames(self):
        """Get names of all roles of that user

        :return: List of names of roles of user
        :rtype: list of str
        """
        return [role.name for role in self.roles]

    def owns_repo(self, repo):
        """Check if user owns the repository

        :param repo: Repository which shoudl be tested
        :type repo: ``repocribro.models.Repository``
        :return: If user owns repo
        :rtype: bool
        """
        return repo.owner.github_id == self.github_user.github_id

    def sees_repo(self, repo):
        """Check if user is allowed to see the repo

        Must be admin or owner to see not public repo

        :param repo: Repository which user want to see
        :type repo: ``repocribro.models.Repository``
        :return: If user can see repo
        :rtype: bool
        """
        return repo.is_public or self.has_role('admin') or self.owns_repo(repo)


#: Many-to-many relationship between user accounts and roles
roles_users = db.Table(
    'RolesAccounts',
    sqlalchemy.Column('account_id',
                      sqlalchemy.Integer(),
                      sqlalchemy.ForeignKey('UserAccount.id')),
    sqlalchemy.Column('role_id',
                      sqlalchemy.Integer(),
                      sqlalchemy.ForeignKey('Role.id'))
)


class UserAccount(db.Model, UserMixin, SearchableMixin):
    """UserAccount in the repocribro app"""
    __tablename__ = 'UserAccount'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now()
    )
    active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    github_user = sqlalchemy.orm.relationship(
        'User', back_populates='user_account',
        uselist=False, cascade='all, delete-orphan'
    )
    roles = sqlalchemy.orm.relationship(
        'Role', back_populates='user_accounts',
        secondary=roles_users,
    )

    @property
    def login(self):
        """Get login name for user account from related GH user

        :return: Login name
        :rtype: str
        """
        if self.github_user is None:
            return '<unknown>'
        return self.github_user.login

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<UserAccount (#{})>'.format(self.id)


class Role(db.Model, RoleMixin):
    """User account role in the application"""
    __tablename__ = 'Role'

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(80), unique=True)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText)
    user_accounts = sqlalchemy.orm.relationship(
        'UserAccount', back_populates='roles', secondary=roles_users
    )

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<Role {} (#{})>'.format(
            self.name, self.id
        )


class RepositoryOwner(db.Model):
    """RepositoryOwner (User or Organization) from GitHub"""
    __tablename__ = 'RepositoryOwner'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    github_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    login = sqlalchemy.Column(sqlalchemy.String(40), unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(255))
    name = sqlalchemy.Column(sqlalchemy.UnicodeText)
    company = sqlalchemy.Column(sqlalchemy.UnicodeText)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText)
    location = sqlalchemy.Column(sqlalchemy.UnicodeText)
    blog_url = sqlalchemy.Column(sqlalchemy.UnicodeText)
    avatar_url = sqlalchemy.Column(sqlalchemy.String(255))
    type = sqlalchemy.Column(sqlalchemy.String(30))
    repositories = sqlalchemy.orm.relationship(
        'Repository', back_populates='owner', cascade='all, delete-orphan'
    )
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'RepositoryOwner'
    }


class User(RepositoryOwner, SearchableMixin):
    """User from GitHub"""
    __searchable__ = ['login', 'email', 'name', 'company',
                      'description', 'location']

    hireable = sqlalchemy.Column(sqlalchemy.Boolean)
    user_account_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('UserAccount.id')
    )
    user_account = sqlalchemy.orm.relationship(
        'UserAccount', back_populates='github_user'
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
        """Create new user from GitHub data and related user account

        :param user_dict: GitHub data containing user
        :type user_dict: dict
        :param user_account: User account in app for GH user
        :type user_account: ``repocribro.models.UserAccount``
        :return: Created new user
        :rtype: ``repocribro.models.User``
        """
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

    def update_from_dict(self, user_dict):
        """Update user from GitHub data

        :param user_dict: GitHub data containing user
        :type user_dict: dict
        """
        self.login = user_dict['login']
        self.email = user_dict['email']
        self.name = user_dict['name']
        self.company = user_dict['company']
        self.location = user_dict['location']
        self.description = user_dict['bio']
        self.blog_url = user_dict['blog']
        self.avatar_url = user_dict['avatar_url']
        self.hireable = user_dict['hireable']

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH User {}, {} (#{})>'.format(
            self.login, self.github_id, self.id
        )


class Organization(RepositoryOwner, SearchableMixin):
    """Organization from GitHub"""
    __searchable__ = ['login', 'email', 'name', 'company',
                      'description', 'location']

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
        """Create new organization from GitHub data

        :param org_dict: GitHub data containing organization
        :type org_dict: dict
        :return: Created new organization
        :rtype: ``repocribro.models.Organization``
        """
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
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH Organization {}, {} (#{})>'.format(
            self.login, self.github_id, self.id
        )

    __mapper_args__ = {
        'polymorphic_identity': 'Organization'
    }


class Repository(db.Model, SearchableMixin):
    """Repository from GitHub"""
    __tablename__ = 'Repository'
    __searchable__ = ['full_name', 'languages', 'description']

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    github_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    fork_of = sqlalchemy.Column(sqlalchemy.Integer)
    full_name = sqlalchemy.Column(sqlalchemy.String(150), unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(100))
    languages = sqlalchemy.Column(sqlalchemy.UnicodeText)
    url = sqlalchemy.Column(sqlalchemy.UnicodeText)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText)
    private = sqlalchemy.Column(sqlalchemy.Boolean)
    visibility_type = sqlalchemy.Column(sqlalchemy.Integer)
    secret = sqlalchemy.Column(sqlalchemy.String(255), unique=True)
    webhook_id = sqlalchemy.Column(sqlalchemy.Integer)
    owner_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('RepositoryOwner.id')
    )
    owner = sqlalchemy.orm.relationship(
        'RepositoryOwner', back_populates='repositories'
    )
    pushes = sqlalchemy.orm.relationship(
        'Push', back_populates='repository',
        cascade='all, delete-orphan'
    )
    releases = sqlalchemy.orm.relationship(
        'Release', back_populates='repository',
        cascade='all, delete-orphan'
    )

    #: Constant representing public visibility within app
    VISIBILITY_PUBLIC = 0
    #: Constant representing private visibility within app
    VISIBILITY_PRIVATE = 1
    #: Constant representing hidden visibility within app
    VISIBILITY_HIDDEN = 2

    def __init__(self, github_id, fork_of, full_name, name, languages, url,
                 description, private, webhook_id, owner, visibility_type,
                 secret=None):
        self.github_id = github_id
        self.fork_of = fork_of
        self.full_name = full_name
        self.name = name
        self.languages = languages
        self.url = url
        self.description = description
        self.private = private
        self.webhook_id = webhook_id
        self.owner = owner
        self.visibility_type = visibility_type
        self.secret = secret

    @staticmethod
    def create_from_dict(repo_dict, owner, webhook_id=None,
                         visibility_type=0, secret=None):
        """Create new repository from GitHub and additional data

        :param repo_dict: GitHub data containing repository
        :type repo_dict: dict
        :param owner: Owner of this repository
        :type owner: ``repocribro.model.RepositoryOwner``
        :param webhook_id: ID of registered webhook (if available)
        :type webhook_id: int
        :param visibility_type: Visibility type within app (default: public)
        :type visibility_type: int
        :param secret: Secret for hidden URL (if available)
        :type secret: str
        :return: Created new repository
        :rtype: ``repocribro.models.Repository``

        :todo: work with fork_of somehow
        """
        fork_of = None
        if 'parent' in repo_dict:
            fork_of = repo_dict['parent']['id']
        return Repository(
            repo_dict['id'],
            fork_of,
            repo_dict['full_name'],
            repo_dict['name'],
            repo_dict['language'],
            repo_dict['html_url'],
            repo_dict['description'],
            repo_dict['private'],
            webhook_id,
            owner,
            visibility_type,
            secret
        )

    def update_from_dict(self, repo_dict):
        """Update repository attributes from GitHub data dict

        :param repo_dict: GitHub data containing repository
        :type repo_dict: dict
        """
        self.full_name = repo_dict['full_name']
        self.name = repo_dict['name']
        self.languages = repo_dict['language']
        self.url = repo_dict['html_url']
        self.description = repo_dict['description']
        self.private = repo_dict['private']

    @staticmethod
    def make_full_name(login, reponame):
        """Create full name from owner login name and repository name

        :param login: Owner login
        :type login: str
        :param reponame: Name of repository (without owner login)
        :type reponame: str
        :return: Full name of repository
        :rtype: str
        """
        return '{}/{}'.format(login, reponame)

    @property
    def owner_login(self):
        """Get owner login from full name of repository

        :return: Owner login
        :rtype: str
        """
        return self.full_name.split('/')[0]

    def generate_secret(self):
        """Generate new unique secret code for repository"""
        import uuid
        import hashlib
        self.secret = ''.join([
            uuid.uuid4().hex,
            hashlib.sha1(self.full_name.encode('utf-8')).hexdigest()
        ])

    @property
    def is_public(self):
        """Check if repository is public within app"""
        return self.visibility_type == self.VISIBILITY_PUBLIC

    @property
    def is_private(self):
        """Check if repository is private within app"""
        return self.visibility_type == self.VISIBILITY_PRIVATE

    @property
    def is_hidden(self):
        """Check if repository is hidden within app"""
        return self.visibility_type == self.VISIBILITY_HIDDEN

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH Repository {}, {} (#{})>'.format(
            self.full_name, self.github_id, self.id
        )


class Push(db.Model, SearchableMixin):
    """Push from GitHub"""
    __tablename__ = 'Push'
    __searchable__ = ['after', 'before', 'sender_login', 'pusher_name',
                      'pusher_email']

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    after = sqlalchemy.Column(sqlalchemy.Integer)
    before = sqlalchemy.Column(sqlalchemy.Integer)
    ref = sqlalchemy.Column(sqlalchemy.String(255))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime())
    compare_url = sqlalchemy.Column(sqlalchemy.UnicodeText())
    pusher_name = sqlalchemy.Column(sqlalchemy.UnicodeText())
    pusher_email = sqlalchemy.Column(sqlalchemy.String(255))
    sender_login = sqlalchemy.Column(sqlalchemy.String(40))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer())
    repository_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('Repository.id')
    )
    repository = sqlalchemy.orm.relationship(
        'Repository', back_populates='pushes'
    )
    commits = sqlalchemy.orm.relationship(
        'Commit', back_populates='push',
        cascade='all, delete-orphan'
    )

    def __init__(self, after, before, ref, timestamp, compare_url, pusher_name,
                 pusher_email, sender_login, sender_id, repository):
        self.after = after
        self.before = before
        self.ref = ref
        self.timestamp = timestamp
        self.compare_url = compare_url
        self.pusher_name = pusher_name
        self.pusher_email = pusher_email
        self.sender_login = sender_login
        self.sender_id = sender_id
        self.repository = repository

    @staticmethod
    def create_from_dict(push_dict, sender_dict, repo):
        """Create new push from GitHub and additional data

        This also creates commits of this push

        :param push_dict: GitHub data containing push
        :type push_dict: dict
        :param sender_dict: GitHub data containing sender
        :type sender_dict: dict
        :param repo: Repository where this push belongs
        :type repo: ``repocribro.models.Repository``
        :return: Created new push
        :rtype: ``repocribro.models.Push``
        """
        push = Push(
            push_dict['after'],
            push_dict['before'],
            push_dict['ref'],
            datetime.datetime.now(),
            push_dict['compare'],
            push_dict['pusher']['name'],
            push_dict['pusher']['email'],
            sender_dict['login'],
            sender_dict['id'],
            repo
        )
        for commit_data in push_dict.get('commits', []):
            Commit.create_from_dict(commit_data, push)
        return push

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH Push {}-{} (#{})>'.format(
            self.before[0:7], self.after[0:7], self.id
        )


class Commit(db.Model, SearchableMixin):
    """Commit from GitHub"""
    __tablename__ = 'Commit'
    __searchable__ = ['sha', 'message', 'tree_sha',
                      'author_name', 'author_name', 'author_login',
                      'committer_name', 'committer_email', 'committer_login']

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sha = sqlalchemy.Column(sqlalchemy.String(40))
    tree_sha = sqlalchemy.Column(sqlalchemy.String(40))
    message = sqlalchemy.Column(sqlalchemy.UnicodeText())
    timestamp = sqlalchemy.Column(sqlalchemy.String(60))
    url = sqlalchemy.Column(sqlalchemy.UnicodeText())
    author_name = sqlalchemy.Column(sqlalchemy.UnicodeText())
    author_email = sqlalchemy.Column(sqlalchemy.String(255))
    author_login = sqlalchemy.Column(sqlalchemy.String(40))
    committer_name = sqlalchemy.Column(sqlalchemy.UnicodeText())
    committer_email = sqlalchemy.Column(sqlalchemy.String(255))
    committer_login = sqlalchemy.Column(sqlalchemy.String(40))
    push_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('Push.id')
    )
    push = sqlalchemy.orm.relationship('Push', back_populates='commits')

    def __init__(self, sha, tree_sha, message, timestamp, url,
                 author_name, author_email, author_login,
                 committer_name, committer_email, committer_login, push):
        self.sha = sha
        self.tree_sha = tree_sha
        self.message = message
        self.timestamp = timestamp
        self.url = url
        self.author_name = author_name
        self.author_email = author_email
        self.author_login = author_login
        self.committer_name = committer_name
        self.committer_email = committer_email
        self.committer_login = committer_login
        self.push = push

    @staticmethod
    def create_from_dict(commit_dict, push):
        """Create new commit from GitHub and additional data

        :param commit_dict: GitHub data containing commit
        :type commit_dict: dict
        :param push: Push where this commit belongs
        :type push: ``repocribro.models.Push``
        :return: Created new commit
        :rtype: ``repocribro.models.Commit``

        :todo: verify, there are some conflict in GitHub docs
        """
        return Commit(
            commit_dict['sha'],
            commit_dict['tree_sha'],
            commit_dict['message'],
            commit_dict['timestamp'],
            commit_dict['html_url'],
            commit_dict['author']['name'],
            commit_dict['author']['email'],
            commit_dict['author']['login'],
            commit_dict['committer']['name'],
            commit_dict['committer']['email'],
            commit_dict['committer']['login'],
            push
        )

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH Commit {}, (#{})>'.format(
            self.sha, self.id
        )


class Release(db.Model, SearchableMixin):
    """Release from GitHub"""
    __tablename__ = 'Release'
    __searchable__ = ['tag_name', 'name', 'body',
                      'author_login', 'sender_login']

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    github_id = sqlalchemy.Column(sqlalchemy.Integer())
    tag_name = sqlalchemy.Column(sqlalchemy.String(255))
    created_at = sqlalchemy.Column(sqlalchemy.String(60))
    published_at = sqlalchemy.Column(sqlalchemy.String(60))
    url = sqlalchemy.Column(sqlalchemy.UnicodeText())
    prerelease = sqlalchemy.Column(sqlalchemy.Boolean())
    draft = sqlalchemy.Column(sqlalchemy.Boolean())
    name = sqlalchemy.Column(sqlalchemy.UnicodeText())
    body = sqlalchemy.Column(sqlalchemy.UnicodeText())
    author_login = sqlalchemy.Column(sqlalchemy.String(40))
    author_id = sqlalchemy.Column(sqlalchemy.Integer())
    sender_login = sqlalchemy.Column(sqlalchemy.String(40))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer())
    repository_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('Repository.id')
    )
    repository = sqlalchemy.orm.relationship(
        'Repository', back_populates='releases'
    )

    def __init__(self, github_id, tag_name, created_at, published_at, url,
                 prerelease, draft, name, body, author_id, author_login,
                 sender_login, sender_id, repository):
        self.github_id = github_id
        self.tag_name = tag_name
        self.created_at = created_at
        self.published_at = published_at
        self.url = url
        self.prerelease = prerelease
        self.draft = draft
        self.name = name
        self.body = body
        self.author_login = author_login
        self.author_id = author_id
        self.sender_login = sender_login
        self.sender_id = sender_id
        self.repository = repository

    @staticmethod
    def create_from_dict(release_dict, sender_dict, repo):
        """Create new release from GitHub and additional data

        :param release_dict: GitHub data containing release
        :type release_dict: dict
        :param sender_dict: GitHub data containing sender
        :type sender_dict: dict
        :param repo: Repository where this release belongs
        :type repo: ``repocribro.models.Repository``
        :return: Created new release
        :rtype: ``repocribro.models.Release``
        """
        return Release(
            release_dict['id'],
            release_dict['tag_name'],
            release_dict['created_at'],
            release_dict['published_at'],
            release_dict['html_url'],
            release_dict['prerelease'],
            release_dict['draft'],
            release_dict['name'],
            release_dict['body'],
            release_dict['author']['login'],
            release_dict['author']['id'],
            sender_dict['login'],
            sender_dict['id'],
            repo
        )

    def __repr__(self):
        """Standard string representation of DB object

        :return: Unique string representation
        :rtype: str
        """
        return '<GH Release {}, {} (#{})>'.format(
            self.tag_name, self.github_id, self.id
        )


#: List of all model classes for simple including
all_models = [
    Commit,
    Push,
    Release,
    Repository,
    Role,
    User,
    UserAccount,
]
