import pytest


@pytest.mark.parametrize(
    'route', [
        '/manage',
        '/manage/profile/update',
        '/manage/repos',
        '/manage/repo/dummyRepo',
        '/manage/repo/dummyRepo/update',
        '/manage/orgs'
    ]
)
def test_unauthorized_get(app_client, route):
    assert app_client.get(route).status == '403 FORBIDDEN'


@pytest.mark.parametrize(
    'route', [
        '/manage/repo/dummyRepo/activate',
        '/manage/repo/dummyRepo/deactivate',
        '/manage/repos/delete'
    ]
)
def test_unauthorized_post(app_client, route):
    assert app_client.post(route).status == '403 FORBIDDEN'
