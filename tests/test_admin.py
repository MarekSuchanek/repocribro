import pytest


@pytest.mark.parametrize(
    'route', [
        '/admin',
        '/admin/account/dummyUser',
        '/admin/repository/dummyUser/dummyRepo',
        '/admin/role/dummyRole'
    ]
)
def test_unauthorized_get(app_client, route):
    assert app_client.get(route).status == '404 NOT FOUND'


@pytest.mark.parametrize(
    'route', [
        '/admin/account/dummyUser/ban'
        '/admin/account/dummyUser/delete',
        '/admin/repository/dummyUser/dummyRepo/visibility',
        '/admin/repository/dummyUser/dummyRepo/delete',
        '/admin/role/dummyRole/edit',
        '/admin/role/dummyRole/delete',
        '/admin/roles/create',
        '/admin/role/dummyRole/add',
        '/admin/role/dummyRole/remove'
    ]
)
def test_unauthorized_post(app_client, route):
    assert app_client.post(route).status == '404 NOT FOUND'
