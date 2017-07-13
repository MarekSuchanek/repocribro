import os
import pytest

from repocribro import create_app

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
FLASK_CONFIG_FILE = ABS_PATH + '/fixtures/config_subdir.cfg'


@pytest.fixture(scope='session')
def subdir_app(request):
    os.environ['REPOCRIBRO_CONFIG_FILE'] = FLASK_CONFIG_FILE
    app = create_app(FLASK_CONFIG_FILE)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def subdir_app_client(subdir_app):
    return subdir_app.test_client()


def test_landing(subdir_app_client):
    assert subdir_app_client.get('/repocribro/').status == '200 OK'
    assert '<h1>repocribro</h1>' in \
           subdir_app_client.get('/repocribro/').data.decode('utf-8')
    assert '/repocribro/static/style.css' in \
           subdir_app_client.get('/repocribro/').data.decode('utf-8')
