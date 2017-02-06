import pytest
import flask
import os
import json

from repocribro import create_app
from repocribro.database import db as _db

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
FLASK_CONFIG_FILE = ABS_PATH + '/fixtures/config.cfg'
TESTDB_PATH = '/tmp/repocribro_test.db'
FIXTURES_PATH = ABS_PATH + '/fixtures'
GITHUB_DATA = FIXTURES_PATH + '/github_data/{}.json'

test_errors_bp = flask.Blueprint('test-error', __name__,
                                 url_prefix='/test-error')


@test_errors_bp.route('/<int:err_code>')
def error_invoker(err_code):
    flask.abort(err_code)


# @see http://alexmic.net/flask-sqlalchemy-pytest/
@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    os.environ['REPOCRIBRO_CONFIG_FILE'] = FLASK_CONFIG_FILE
    app = create_app(FLASK_CONFIG_FILE)
    app.register_blueprint(test_errors_bp)

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
    push = Push('abc', 'def', 'refs/heads/changes', datetime.datetime.now(),
                '', 'pusher_name', 'pusher_email', 'sender_login', 'sender_id',
                repo1)
    session.add(push)
    commit = Commit('def', 'tsha', 'Dummy commit', '',
                    '', 'author_name', 'author_email', 'author_login',
                    'committer_name', 'committer_email', 'committer_login',
                    push)
    session.add(commit)
    session.commit()
    return session
