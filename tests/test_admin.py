import pytest

# TODO: check redirect url


@pytest.mark.parametrize(
    'route', [
        '/admin',
        '/admin/account/regular',
        '/admin/repository/regular/repo1',
        '/admin/role/admin'
    ]
)
def test_unauthorized_get(filled_db_session, app_client, route):
    assert app_client.get(route).status == '404 NOT FOUND'


@pytest.mark.parametrize(
    'route', [
        '/admin/account/regular/ban',
        '/admin/account/regular/delete',
        '/admin/repository/regular/repo1/visibility',
        '/admin/repository/regular/repo1/delete',
        '/admin/role/admin/edit',
        '/admin/role/admin/delete',
        '/admin/roles/create',
        '/admin/role/admin/add',
        '/admin/role/admin/remove'
    ]
)
def test_unauthorized_post(filled_db_session, app_client, route):
    assert app_client.post(route).status == '404 NOT FOUND'


@pytest.mark.parametrize(
    'route', [
        '/admin',
        '/admin/account/regular',
        '/admin/repository/regular/repo1',
        '/admin/role/admin'
    ]
)
def test_authorized_get(filled_db_session, app_client, route):
    app_client.get('/test/login/admin')
    assert app_client.get(route).status == '200 OK'
    app_client.get('/test/logout')


@pytest.mark.parametrize(
    'route', [
        '/admin/account/mrNotFound',
        '/admin/repository/mrNotFound/repo1',
        '/admin/repository/regular/repoNotFound',
        '/admin/role/notFound'
    ]
)
def test_authorized_get_unexisting(filled_db_session, app_client, route):
    app_client.get('/test/login/admin')
    assert app_client.get(route).status == '404 NOT FOUND'
    app_client.get('/test/logout')


@pytest.mark.parametrize(
    'route', [
        '/admin/account/mrNotFound/ban',
        '/admin/account/mrNotFound/delete',
        '/admin/repository/mrNotFound/repo1/visibility',
        '/admin/repository/mrNotFound/repo1/delete',
        '/admin/repository/regular/repoNotFound/visibility',
        '/admin/repository/regular/repoNotFound/delete',
        '/admin/role/notFound/edit',
        '/admin/role/notFound/delete',
        '/admin/role/notFound/add',
        '/admin/role/notFound/remove'
    ]
)
def test_authorized_post_unexisting(filled_db_session, app_client, route):
    app_client.get('/test/login/admin')
    assert app_client.post(route).status == '404 NOT FOUND'
    app_client.get('/test/logout')


def test_account_ban_unban(filled_db_session, app_client):
    from repocribro.models import User
    app_client.get('/test/login/admin')
    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert user.user_account.is_active
    ret = app_client.post('/admin/account/regular/ban', data={'active': '0'})
    assert ret.status == '302 FOUND'
    assert not user.user_account.is_active
    ret = app_client.post('/admin/account/regular/ban', data={'active': '0'})
    assert ret.status == '302 FOUND'
    assert not user.user_account.is_active
    ret = app_client.post('/admin/account/regular/ban', data={'active': '1'})
    assert ret.status == '302 FOUND'
    assert user.user_account.is_active
    ret = app_client.post('/admin/account/regular/ban', data={'active': '1'})
    assert ret.status == '302 FOUND'
    assert user.user_account.is_active
    app_client.get('/test/logout')


def test_account_delete(filled_db_session, app_client):
    from repocribro.models import User
    app_client.get('/test/login/admin')
    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert user is not None

    ret = app_client.post('/admin/account/regular/delete')
    assert ret.status == '302 FOUND'

    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert user is None

    app_client.get('/test/logout')


def test_role_create_edit_delete(filled_db_session, app_client):
    from repocribro.models import Role
    app_client.get('/test/login/admin')
    existing_role = {'name': 'admin', 'description': ''}
    ret = app_client.post('/admin/roles/create', data=existing_role)
    assert ret.status == '302 FOUND'

    bad_role = {'name': '', 'description': ''}
    ret = app_client.post('/admin/roles/create', data=bad_role)
    assert ret.status == '302 FOUND'

    role = filled_db_session.query(Role).filter_by(name='testadmin').first()
    assert role is None
    new_role = {'name': 'testadmin', 'description': ''}
    ret = app_client.post('/admin/roles/create', data=new_role)
    assert ret.status == '302 FOUND'
    role = filled_db_session.query(Role).filter_by(name='testadmin').first()
    assert role is not None
    assert role.name == 'testadmin'

    ret = app_client.post('/admin/role/testadmin/edit', data=existing_role)
    assert ret.status == '302 FOUND'
    role = filled_db_session.query(Role).filter_by(name='testadmin').first()
    assert role.name == 'testadmin'

    ret = app_client.post('/admin/role/testadmin/edit', data=bad_role)
    assert ret.status == '302 FOUND'
    role = filled_db_session.query(Role).filter_by(name='testadmin').first()
    assert role.name == 'testadmin'

    role = filled_db_session.query(Role).filter_by(name='test_admin').first()
    assert role is None
    edit_role = {'name': 'test_admin', 'description': ''}
    ret = app_client.post('/admin/role/testadmin/edit', data=edit_role)
    assert ret.status == '302 FOUND'
    role = filled_db_session.query(Role).filter_by(name='test_admin').first()
    assert role.name == 'test_admin'

    ret = app_client.post('/admin/role/test_admin/delete')
    assert ret.status == '302 FOUND'
    role = filled_db_session.query(Role).filter_by(name='test_admin').first()
    assert role is None

    app_client.get('/test/logout')


def test_role_add_remove(filled_db_session, app_client):
    from repocribro.models import Role, User
    app_client.get('/test/login/admin')
    role = filled_db_session.query(Role).filter_by(name='admin').first()
    user = filled_db_session.query(User).filter_by(login='regular').first()
    account = user.user_account
    assert role not in account.roles
    assert not account.has_role('admin')

    data = {'login': 'regular'}
    ret = app_client.post('/admin/role/admin/add', data=data)
    assert ret.status == '302 FOUND'
    assert role in account.roles
    assert account.has_role('admin')

    ret = app_client.post('/admin/role/admin/add', data=data)
    assert ret.status == '302 FOUND'
    assert role in account.roles
    assert account.has_role('admin')

    ret = app_client.post('/admin/role/admin/remove', data=data)
    assert ret.status == '302 FOUND'
    assert role not in account.roles
    assert not account.has_role('admin')

    ret = app_client.post('/admin/role/admin/remove', data=data)
    assert ret.status == '302 FOUND'
    assert role not in account.roles
    assert not account.has_role('admin')

    app_client.get('/test/logout')


def test_repo_visibility(filled_db_session, app_client):
    from repocribro.models import Repository
    app_client.get('/test/login/admin')
    repo = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo.is_public

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': Repository.VISIBILITY_HIDDEN})
    assert ret.status == '302 FOUND'
    assert repo.is_hidden
    assert repo.secret is not None
    old_secret = repo.secret

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': '666 YOLO'})
    assert ret.status == '302 FOUND'
    assert repo.is_hidden
    assert repo.secret == old_secret

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': Repository.VISIBILITY_HIDDEN})
    assert ret.status == '302 FOUND'
    assert repo.is_hidden
    assert repo.secret is not None
    assert repo.secret != old_secret

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': Repository.VISIBILITY_PRIVATE})
    assert ret.status == '302 FOUND'
    assert repo.is_private

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': Repository.VISIBILITY_PRIVATE})
    assert ret.status == '302 FOUND'
    assert repo.is_private

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': Repository.VISIBILITY_PUBLIC})
    assert ret.status == '302 FOUND'
    assert repo.is_public

    ret = app_client.post('/admin/repository/regular/repo1/visibility',
                          data={'enable': '666 YOLO'})
    assert ret.status == '302 FOUND'
    assert repo.is_public

    app_client.get('/test/logout')


def test_repo_delete(filled_db_session, app_client):
    from repocribro.models import Repository
    app_client.get('/test/login/admin')
    repo = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo is not None

    ret = app_client.post('/admin/repository/regular/repo1/delete')
    assert ret.status == '302 FOUND'
    repo = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo is None

    app_client.get('/test/logout')


# TODO: learn how to teardown (its weird)
def test_dummy_last(empty_db_session, app_client):
    app_client.get('/test/logout')
