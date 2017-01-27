import pytest


@pytest.fixture
def auth_cfg():
    return {
        'github': {
            'client_id': 'SOME_CLIENT_ID',
            'client_secret': 'SOME_CLIENT_SECRET',
            'webhooks_secret': 'SOME_WEBHOOKS_SECRET',
        },
        'flask': {
            'secret_key': 'FLASK_SECRET_KEY'
        }
    }


@pytest.fixture
def repocribro_app(auth_cfg):
    """Flask web application test client"""
    from repocribro.repocribro import create_app
    app, manager = create_app(auth_cfg)
    return app.test_client()
