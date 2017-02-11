import betamax
import datetime
import pytest
import flask
import os
import json
from betamax.cassette import cassette

from repocribro import create_app
from repocribro.database import db as _db
from repocribro.github import GitHubAPI

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
FLASK_CONFIG_FILE = ABS_PATH + '/fixtures/config.cfg'
TESTDB_PATH = '/tmp/repocribro_test.db'
FIXTURES_PATH = ABS_PATH + '/fixtures'
GITHUB_DATA = FIXTURES_PATH + '/github_data/{}.json'


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = FIXTURES_PATH + '/cassettes'
    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')
    if 'GITHUB_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'all'
    else:
        config.default_cassette_options['record_mode'] = 'none'
    config.define_cassette_placeholder('<TOKEN>', token)


@pytest.fixture
def github_api(betamax_session):
    """GitHub API client with betamax session"""
    betamax_session.headers.update({'accept-encoding': 'identity'})
    api_key = 'fake_key'
    api_secret = 'fake_secret'
    webhooks_secret = 'webhooks_secret'
    token = os.environ.get('GITHUB_TOKEN', 'GitHub TOKEN')
    return GitHubAPI(api_key, api_secret, webhooks_secret,
                     session=betamax_session, token=token)


test = flask.Blueprint('test', __name__, url_prefix='/test')


@test.route('/error/<int:err_code>')
def error_invoker(err_code):
    flask.abort(err_code)


@test.route('/login/<username>')
def fake_login(username):
    from repocribro.security import login
    from repocribro.models import User
    db = flask.current_app.container.get('db')
    user = db.session.query(User).filter_by(login=username).first()
    login(user.user_account)
    return 'OK'


@test.route('/logout')
def fake_logout():
    from repocribro.security import logout
    logout()
    return 'OK'


@test.route('/fake-github')
def fake_github():
    gh_api = flask.current_app.container.get('gh_api')
    flask.current_app.container.set_singleton('real_gh_api', gh_api)
    flask.current_app.container.set_singleton('gh_api', FakeGitHubAPI())
    return 'OK'


@test.route('/unfake-github')
def unfake_github():
    gh_api = flask.current_app.container.get('real_gh_api')
    flask.current_app.container.set_singleton('gh_api', gh_api)
    return 'OK'


# @see http://alexmic.net/flask-sqlalchemy-pytest/
@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    os.environ['REPOCRIBRO_CONFIG_FILE'] = FLASK_CONFIG_FILE
    app = create_app(FLASK_CONFIG_FILE)
    app.register_blueprint(test)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def app_client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='session')
def github_data_loader():
    def get_github_data(name):
        with open(GITHUB_DATA.format(name)) as f:
            return json.load(f)

    return get_github_data


@pytest.fixture(scope='function')
def empty_db_session(db):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    return db.session


@pytest.fixture(scope='function')
def filled_db_session(empty_db_session):
    session = empty_db_session
    import datetime
    from repocribro.models import Role, UserAccount, User, \
        Organization, Repository, Commit, Release, Push

    # Setup admin role
    admin_role = Role('admin', 'Administrators')
    session.add(admin_role)

    account_banned = UserAccount()
    account_banned.active = False
    session.add(account_banned)
    account_user = UserAccount()
    session.add(account_user)
    account_admin = UserAccount()
    account_admin.roles.append(admin_role)
    session.add(account_admin)

    user1 = User(64, 'banned', 'banned@repocribro.yolo', 'Mister Banned',
                 None, 'Cribropolis', 'Trolling everywhere', None, None,
                 None, account_banned)
    session.add(user1)
    user2 = User(65, 'regular', 'regular@repocribro.yolo', 'Mister Regular',
                 None, 'Cribropolis', 'Polite person', None, None,
                 None, account_user)
    session.add(user2)
    user3 = User(66, 'admin', 'admin@repocribro.yolo', 'Mister Admin',
                 None, 'Cribropolis', 'Big boss', None, None,
                 None, account_admin)
    session.add(user3)
    org1 = Organization(69, 'org', 'org@repocribro.yolo', 'Org Dept. 666',
                        'Repocribro', 'Cribropolis', 'Just awesome', None,
                        None)
    session.add(org1)

    repo1 = Repository(100, None, 'regular/repo1', 'repo1', 'Python', '',
                       '', False, None, user2, Repository.VISIBILITY_PUBLIC)
    session.add(repo1)
    repo2 = Repository(101, None, 'regular/repo2', 'repo2', 'Python', '',
                       '', False, None, user2, Repository.VISIBILITY_HIDDEN)
    repo2.generate_secret()
    session.add(repo2)
    repo3 = Repository(102, None, 'regular/repo3', 'repo3', 'Haskell', '',
                       '', False, None, user2, Repository.VISIBILITY_PRIVATE)
    session.add(repo3)

    release = Release(666, 'v1.0', '', '', '', False, False, 'First release',
                      'Some description', 'author_id', 'author_login',
                      'sender_login', 'sender_id', repo1)
    session.add(release)
    push = Push(484, 'refs/heads/changes', 'abc', 'def', 1, 1,
                datetime.datetime.now(), 'sender_login', 'sender_id', repo1)
    session.add(push)
    commit = Commit('def', 'Dummy commit', 'author_name', 'author_email',
                    True, push)
    session.add(commit)
    session.commit()
    return session


class FakeGitHubAPI:
    """Fake GitHub API"""
    DATA = {
        '/user': {
            'id': 65, 'login': 'regular', 'email': 'new@mail.com',
            'name': 'new_n', 'company': 'new_c', 'location': 'new_l',
            'bio': 'new_b', 'blog': 'new_u', 'avatar_url': 'a',
            'hireable': True
        },
        '/user/repos': [
            {
                'id': 100, 'full_name': 'regular/repo1', 'name': 'repo1',
                'language': 'Python', 'html_url': '', 'description': '',
                'private': False
            },
            {
                'id': 101, 'full_name': 'regular/repo2', 'name': 'repo2',
                'language': 'Python', 'html_url': '', 'description': '',
                'private': False
            },
            {
                'id': 102, 'full_name': 'regular/repo3', 'name': 'repo3',
                'language': 'Haskell', 'html_url': '', 'description': '',
                'private': False
            }
        ],
        '/repos/regular/repo1': {
            'id': 100, 'full_name': 'regular/repo1', 'name': 'repo1',
            'language': 'Python', 'html_url': '', 'description': '',
            'private': False
        },
        '/repos/regular/repo2': {
            'id': 101, 'full_name': 'regular/repo2', 'name': 'repo2',
            'language': 'Javascript', 'html_url': '', 'description': '',
            'private': False
        },
        '/repos/regular/repo3': {
            'id': 102, 'full_name': 'regular/repo3', 'name': 'repo3',
            'language': 'Haskell', 'html_url': '', 'description': '',
            'private': False
        },
        '/repos/regular/newOne': {
            'id': 103, 'full_name': 'regular/newOne', 'name': 'newOne',
            'language': 'C++', 'html_url': '', 'description': '',
            'private': False
        },
        '/repos/regular/repo1/events': [
            {
                'id': 118818, 'type': 'PushEvent',
                'created_at': '2017-03-04T21:08:12Z',
                'public': True,
                'actor': {'id': 65, 'login': 'regular'},
                'repo': {'id': 100, 'name': 'regular/repo1'},
                'payload': {
                    'push_id': 77777, 'size': 2, 'distinct_size': 1,
                    'ref': 'refs/heads/master',
                    'head': 'a31bf2212be0f567ed863a28ed16f6f9adecb694',
                    'before': 'f7ed038c532687aee14102c0e30c49e30204165c',
                    'commits': [
                        {
                            'sha': 'dea9a21cc8ebb1fdeff29f948eb485519acdc99e',
                            'author': {
                                'email': 'regular@mail.com',
                                'name': 'Mister Regular'
                            },
                            'message': 'MSG COMMIT 2',
                            'distinct': False,
                        },
                        {
                            'sha': 'a31bf2212be0f567ed863a28ed16f6f9adecb694',
                            'author': {
                                'email': 'regular@mail.com',
                                'name': 'Mister Regular'
                            },
                            'message': 'MSG COMMIT 1',
                            'distinct': True,
                        }
                    ]
                }
            },
            {
                'id': 7777541, 'type': 'ReleaseEvent',
                'created_at': '2017-02-04T21:08:12Z',
                'public': True,
                'actor': {'id': 65, 'login': 'regular'},
                'repo': {'id': 100, 'name': 'regular/repo1'},
                'payload': {
                    'action': 'published',
                    'release': {
                        'id': 8461516,
                        'tag_name': '0.0.7',
                        'name': 'Yolo Release',
                        'body': 'Some long text body',
                        'draft': False,
                        'prerelease': True,
                        'html_url': 'URL',
                        'created_at': '2017-02-04T21:08:12Z',
                        'published_at': '2017-02-04T21:08:12Z',
                        'author': {'id': 65, 'login': 'regular'},
                    }
                }
            },
            {
                'id': 7454542, 'type': 'RepositoryEvent',
                'created_at': '2017-01-04T21:08:12Z',
                'public': True,
                'actor': {'id': 65, 'login': 'regular'},
                'repo': {'id': 100, 'name': 'regular/repo1'},
                'payload': {
                    'action': 'publicized',
                    'repository': {}
                }
            },
            {
                'id': 7454542, 'type': 'RepositoryEvent',
                'created_at': '2017-01-04T21:08:12Z',
                'public': True,
                'actor': {'id': 65, 'login': 'regular'},
                'repo': {'id': 100, 'name': 'regular/repo1'},
                'payload': {
                    'action': 'privatized',
                    'repository': {}
                }
            },
            {
                'id': 7454542, 'type': 'RepositoryEvent',
                'created_at': '2017-01-04T21:08:12Z',
                'public': True,
                'actor': {'id': 65, 'login': 'regular'},
                'repo': {'id': 100, 'name': 'regular/repo1'},
                'payload': {
                    'action': 'deleted',
                    'repository': {}
                }
            }
        ]
    }
    #: URL to GitHub API
    API_URL = 'https://api.github.com'
    #: URL for OAuth request at GitHub
    AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
    #: URL for OAuth token at GitHub
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    #: Scopes for OAuth request
    SCOPES = ['user', 'repo', 'admin:repo_hook']
    #: Required webhooks to be registered
    WEBHOOKS = ['push', 'release', 'repository']
    #: Controller for incoming webhook events
    WEBHOOK_CONTROLLER = 'webhooks.gh_webhook'

    def __init__(self, client_id='', client_secret='', webhooks_secret='',
                 session=None, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhooks_secret = webhooks_secret
        self.session = session
        self.token = token
        self.scope = []

    @staticmethod
    def _get_auth_header():
        if 'github_token' not in flask.session:
            return {}
        return {
            'Authorization': 'token {}'.format(flask.session['github_token'])
        }

    def get_auth_url(self):
        return flask.url_for('auth.github_callback')

    def login(self, session_code):
        if session_code == 'bad_code':
            return False
        flask.session['github_token'] = 'GH_TOKEN'
        flask.session['github_scope'] = 'GH_SCOPE'
        return True

    def get_token(self):
        return flask.session['github_token']

    def get_scope(self):
        return flask.session['github_scope']

    def logout(self):
        for key in ('github_token', 'github_scope'):
            flask.session.pop(key, None)

    def get(self, what):
        if what in self.DATA:
            return FakeResponse(200, self.DATA[what])
        return FakeResponse(404, {'message': 'Not Found'})

    def get_data(self, what):
        return self.get(what).json()

    def webhook_get(self, full_name, id):
        return None

    def webhooks_get(self, full_name):
        return []

    def webhook_create(self, full_name, events=None, hook_url=None):
        return {'id': 777}

    def webhook_tests(self, full_name, hook_id):
        return True

    def webhook_delete(self, full_name, hook_id):
        return True

    def webhook_verify_signature(self, payload, signature):
        return True


class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data
