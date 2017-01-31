import pytest

FLASK_CONFIG_FILE = 'tests/fixtures/config.cfg'


@pytest.fixture
def repocribro_app():
    """Flask web application test client"""
    from repocribro.repocribro import create_app
    app = create_app(FLASK_CONFIG_FILE)
    return app.test_client()
