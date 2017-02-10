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

    res = app_client.get('/manage/repos')
    assert res.status == '200 OK'

    res = app_client.get('/manage/orgs')
    assert res.status == '501 NOT IMPLEMENTED'


def test_authorized_repo_unexisting(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    res = app_client.get('/manage/repo/yolo')
    assert res.status == '404 NOT FOUND'

    res = app_client.get('/manage/repo/yolo/update')
    assert res.status == '404 NOT FOUND'

    res = app_client.post('/manage/repo/yolo/activate', data={'enable': '0'})
    assert res.status == '302 FOUND'

    res = app_client.post('/manage/repo/yolo/activate', data={'enable': '7'})
    assert res.status == '302 FOUND'

    res = app_client.post('/manage/repo/yolo/deactivate')
    assert res.status == '404 NOT FOUND'

    res = app_client.post('/manage/repos/delete', data={'reponame': 'none'})
    assert res.status == '404 NOT FOUND'


def test_authorized_repos(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    res = app_client.get('/manage/repo/repo1')
    assert res.status == '200 OK'
    assert 'Python' in res.data.decode('utf-8')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2.languages == 'Python'
    res = app_client.get('/manage/repo/repo2/update')
    assert res.status == '302 FOUND'
    assert repo2.languages == 'Javascript'

    repo2.webhook_id = 666
    res = app_client.post('/manage/repo/repo2/deactivate')
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is None
    res = app_client.post('/manage/repo/repo2/deactivate')
    assert res.status == '302 FOUND'

    res = app_client.post('/manage/repo/repo2/activate', data={'enable': '0'})
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

    repo2.webhook_id = 666
    res = app_client.post('/manage/repo/repo2/deactivate')
    assert res.status == '302 FOUND'
    assert repo2.webhook_id is None
    res = app_client.post('/manage/repo/repo2/deactivate')
    assert res.status == '302 FOUND'


def test_authorized_repo_activate_public(filled_db_session, app_client):
    from repocribro.models import User, Repository
    app_client.get('/test/fake-github')
    app_client.get('/auth/github')
    app_client.get('/auth/github/callback?code=aaa')

    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2.is_hidden

    res = app_client.post('/manage/repo/repo2/activate', data={
        'enable': Repository.VISIBILITY_PUBLIC
    })
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
    assert repo1.is_public

    res = app_client.post('/manage/repo/repo1/activate', data={
        'enable': Repository.VISIBILITY_PRIVATE
    })
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
    assert repo_new is None

    res = app_client.post('/manage/repo/newOne/activate', data={
        'enable': Repository.VISIBILITY_PRIVATE
    })
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
    assert repo1.is_public

    res = app_client.post('/manage/repo/repo1/activate', data={
        'enable': Repository.VISIBILITY_HIDDEN
    })
    assert res.status == '302 FOUND'
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo1.is_hidden
    assert repo1.secret is not None
    old_secret = repo1.secret

    res = app_client.post('/manage/repo/repo1/activate', data={
        'enable': Repository.VISIBILITY_HIDDEN
    })
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
    repo2.webhook_id = 777
    filled_db_session.commit()
    assert repo2 is not None

    res = app_client.post('/manage/repos/delete', data={
        'reponame': 'repo2'
    })
    assert res.status == '302 FOUND'
    repo2 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    assert repo2 is None


# TODO: learn how to teardown (its weird)
def test_dummy_last(empty_db_session, app_client):
    app_client.get('/test/unfake-github')
    app_client.get('/test/logout')
