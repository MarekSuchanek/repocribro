import pytest


@pytest.fixture
def repocribro_app():
    """Flask web application test client"""
    from repocribro import app
    return app.test_client()
