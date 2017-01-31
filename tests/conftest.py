import pytest
import os
import json

from repocribro import create_app
from repocribro.database import db as _db

FLASK_CONFIG_FILE = 'tests/fixtures/config.cfg'
TESTDB_PATH = '/tmp/repocribro_test.db'
FIXTURES_PATH = os.path.abspath(os.path.dirname(__file__)) + '/fixtures'
GITHUB_DATA = FIXTURES_PATH + '/github_data/{}.json'

# @see http://alexmic.net/flask-sqlalchemy-pytest/


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app(FLASK_CONFIG_FILE)

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
