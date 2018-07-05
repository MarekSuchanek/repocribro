import pytest


@pytest.mark.parametrize(
    'route', [
        '/manage',
        '/manage/profile/update',
        '/manage/repositories',
        '/manage/repository/dummyRepo',
        '/manage/organizations',
        '/manage/organization/org',
        '/manage/organization/org/update'
    ]
)
def test_unauthorized_get(app_client, route):
    assert app_client.get(route).status == '403 FORBIDDEN'


@pytest.mark.parametrize(
    ('route', 'data'), [
        ('/manage/repository/activate', {'full_name': 'dummy/dummyRepo'}),
        ('/manage/repository/deactivate', {'full_name': 'dummy/dummyRepo'}),
        ('/manage/repository/delete', {'full_name': 'dummy/dummyRepo'}),
        ('/manage/repository/update', {'full_name': 'dummy/dummyRepo'})
    ]
)
def test_unauthorized_post(app_client, route, data):
    assert app_client.post(route, data=data).status == '403 FORBIDDEN'


def test_authorized_basic(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')
    res = app_client.get('/manage')
    assert res.status == '200 OK'

    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert user.name == 'Mister Regular'
    res = app_client.get('/manage/profile/update')
    assert res.status == '302 FOUND'
    assert user.name == 'new_n'

    res = app_client.get('/manage/repositories')
    assert res.status == '200 OK'

    res = app_client.get('/manage/organizations')
    assert res.status == '200 OK'


def test_authorized_repo_unexisting(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    res = app_client.get('/manage/repository/guy/yolo')
    assert res.status == '404 NOT FOUND'

    data = {'full_name': '/guy/yolo'}
    res = app_client.post('/manage/repository/update', data=data)
    assert res.status == '404 NOT FOUND'

    data['enable'] = 0
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'

    data['enable'] = 7
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'

    res = app_client.post('/manage/repository/deactivate', data=data)
    assert res.status == '404 NOT FOUND'

    res = app_client.post('/manage/repository/delete', data=data)
    assert res.status == '404 NOT FOUND'


def test_authorized_repos(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    res = app_client.get('/manage/repository/regular/repo1')
    assert res.status == '200 OK'
    assert 'regular/repo1' in res.data.decode('utf-8')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    data = {'full_name': 'regular/repo2'}
    assert repo2.languages == 'Python'
    res = app_client.post('/manage/repository/update', data=data)
    assert res.status == '302 FOUND'
    assert repo2.languages == 'Javascript'

    repo2.webhook_id = 666
    res = app_client.post('/manage/repository/deactivate', data=data)
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is None
    res = app_client.post('/manage/repository/deactivate', data=data)
    assert res.status == '302 FOUND'

    data['enable'] = 0
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is not None
    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2.is_public


def test_authorized_repo_deactivate(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    data = {'full_name': 'regular/repo2'}

    repo2.webhook_id = 666
    res = app_client.post('/manage/repository/deactivate', data=data)
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is None
    res = app_client.post('/manage/repository/deactivate', data=data)
    assert res.status == '302 FOUND'


def test_authorized_repo_activate_public(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    data = {'full_name': 'regular/repo2'}
    assert repo2.is_hidden

    data['enable'] = Repository.VISIBILITY_PUBLIC
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is not None
    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2.is_public


def test_authorized_repo_activate_private(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    data = {'full_name': 'regular/repo1'}
    assert repo1.is_public

    data['enable'] = Repository.VISIBILITY_PRIVATE
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo1.is_private


def test_authorized_repo_activate_new(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo_new = filled_db_session.query(Repository).filter_by(
        full_name='regular/newOne'
    ).first()
    data = {'full_name': 'regular/newOne'}
    assert repo_new is None

    data['enable'] = Repository.VISIBILITY_PRIVATE
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    repo_new = filled_db_session.query(Repository).filter_by(
        full_name='regular/newOne'
    ).first()
    assert repo_new is not None


def test_authorized_repo_activate_hidden(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    data = {'full_name': 'regular/repo1'}
    assert repo1.is_public

    data['enable'] = Repository.VISIBILITY_HIDDEN
    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo1.is_hidden
    assert repo1.secret is not None
    old_secret = repo1.secret

    res = app_client.post('/manage/repository/activate', data=data)
    assert res.status == '302 FOUND'
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo1.is_hidden
    assert repo1.secret is not None
    assert repo1.secret != old_secret


def test_authorized_repo_delete(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    data = {'full_name': 'regular/repo2'}
    repo2.webhook_id = 777
    filled_db_session.commit()
    assert repo2 is not None

    res = app_client.post('/manage/repository/delete', data=data)
    assert res.status == '302 FOUND'
    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2 is None


# TODO: learn how to teardown (its weird)
def test_dummy_last(empty_db_session, app_client):
    app_client.get('/test/unfake-github')
    app_client.get('/test/logout')
