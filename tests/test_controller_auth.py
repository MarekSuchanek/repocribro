

def test_login_existing_active(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    res = app_client.get('/auth/github')
    assert res.status == '302 FOUND'
    res = app_client.get('/auth/github/callback?code=aaa')
    assert res.status == '302 FOUND'

    res = app_client.get('/manage')
    assert res.status == '200 OK'

    res = app_client.get('/auth/logout')
    assert res.status == '302 FOUND'
    res = app_client.get('/manage')
    assert res.status == '403 FORBIDDEN'


def test_login_existing_inactive(filled_db_session, app_client):
    from repocribro.models import User
    app_client.get('/test/fake-github')
    user = filled_db_session.query(User).filter_by(login='regular').first()
    user.user_account.active = False
    filled_db_session.commit()
    assert not user.user_account.is_active

    res = app_client.get('/auth/github')
    assert res.status == '302 FOUND'
    res = app_client.get('/auth/github/callback?code=aaa')
    assert res.status == '302 FOUND'

    res = app_client.get('/manage')
    assert res.status == '403 FORBIDDEN'


def test_login_new(empty_db_session, app_client):
    from repocribro.models import User
    app_client.get('/test/fake-github')
    user = empty_db_session.query(User).filter_by(login='regular').first()
    assert user is None

    res = app_client.get('/auth/github')
    assert res.status == '302 FOUND'
    res = app_client.get('/auth/github/callback?code=aaa')
    assert res.status == '302 FOUND'

    user = empty_db_session.query(User).filter_by(login='regular').first()
    assert user is not None

    res = app_client.get('/manage')
    assert res.status == '200 OK'


def test_login_new_bad_code(empty_db_session, app_client):
    from repocribro.models import User
    app_client.get('/test/fake-github')
    user = empty_db_session.query(User).filter_by(login='regular').first()
    assert user is None

    res = app_client.get('/auth/github')
    assert res.status == '302 FOUND'
    res = app_client.get('/auth/github/callback?code=bad_code')
    assert res.status == '302 FOUND'

    user = empty_db_session.query(User).filter_by(login='regular').first()
    assert user is None

    res = app_client.get('/manage')
    assert res.status == '403 FORBIDDEN'


# TODO: learn how to teardown (its weird)
def test_dummy_last(app_client):
    app_client.get('/test/unfake-github')
