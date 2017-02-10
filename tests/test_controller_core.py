

def test_landing(app_client):
    assert app_client.get('/').status == '200 OK'
    assert '<h1>repocribro</h1>' in \
           app_client.get('/').data.decode('utf-8')


def test_search(app_client):
    res = app_client.get('/search')
    assert res.status == '200 OK'
    assert '<h1>Search</h1>' in res.data.decode('utf-8')

    res = app_client.get('/search/yolo')
    assert '<h1>Search</h1>' in res.data.decode('utf-8')
    assert 'yolo' in res.data.decode('utf-8')


def test_user_detail(filled_db_session, app_client):
    res = app_client.get('/user/regular')
    assert res.status == '200 OK'
    assert 'Mister Regular' in res.data.decode('utf-8')

    res = app_client.get('/user/notFound')
    assert res.status == '404 NOT FOUND'

    res = app_client.get('/user/org')
    assert res.status == '302 FOUND'


def test_org_detail(filled_db_session, app_client):
    res = app_client.get('/org/org')
    assert res.status == '200 OK'
    assert 'Org Dept. 666' in res.data.decode('utf-8')

    res = app_client.get('/org/notFound')
    assert res.status == '404 NOT FOUND'

    res = app_client.get('/org/regular')
    assert res.status == '302 FOUND'


def test_repo_owner(filled_db_session, app_client):
    res = app_client.get('/repo/org')
    assert res.status == '302 FOUND'

    res = app_client.get('/repo/regular')
    assert res.status == '302 FOUND'


def test_repo_detail(filled_db_session, app_client):
    res = app_client.get('/repo/regular/repo1')  # PUBLIC
    assert res.status == '200 OK'
    assert 'Python' in res.data.decode('utf-8')

    res = app_client.get('/repo/regular/repo666')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/repo/regular/repo2')  # HIDDEN
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/repo/regular/repo3')  # PRIVATE
    assert res.status == '404 NOT FOUND'


def test_repo_own(filled_db_session, app_client):
    app_client.get('/test/login/admin')

    res = app_client.get('/repo/regular/repo2')  # HIDDEN
    assert res.status == '200 OK'
    res = app_client.get('/repo/regular/repo3')  # PRIVATE
    assert res.status == '200 OK'

    app_client.get('/test/logout')


def test_repo_hidden(filled_db_session, app_client):
    from repocribro.models import Repository
    repo = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo2'
    ).first()
    secret_url = '/hidden-repo/' + repo.secret
    res = app_client.get(secret_url)
    assert res.status == '200 OK'
    assert 'Python' in res.data.decode('utf-8')


# TODO: learn how to teardown (its weird)
def test_dummy_last(empty_db_session, app_client):
    app_client.get('/test/logout')
