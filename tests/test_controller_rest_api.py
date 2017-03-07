import json


def test_get_user(filled_db_session, app_client):
    res = app_client.get('/api/user/noone')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/user/regular')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['login'] == 'regular'
    assert data['name'] == 'Mister Regular'


def test_get_org(filled_db_session, app_client):
    res = app_client.get('/api/org/noorg')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/org/org')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['login'] == 'org'
    assert data['company'] == 'Repocribro'


def test_get_repo(filled_db_session, app_client):
    res = app_client.get('/api/repo/regular/nope')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/repo/regular/repo1')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['full_name'] == 'regular/repo1'
    assert data['github_id'] == 100
    res = app_client.get('/api/repo/regular/repo2')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/repo/regular/repo3')
    assert res.status == '404 NOT FOUND'


def test_get_repo_by_id(filled_db_session, app_client):
    res = app_client.get('/api/repo/666')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/repo/1')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['full_name'] == 'regular/repo1'
    assert data['github_id'] == 100
    res = app_client.get('/api/repo/2')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/repo/3')
    assert res.status == '404 NOT FOUND'


def test_get_push(filled_db_session, app_client):
    res = app_client.get('/api/push/666')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/push/1')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['before'] == 'def'
    assert data['after'] == 'abc'
    assert data['github_id'] == 484
    assert data['repository_id'] == 1


def test_get_commit(filled_db_session, app_client):
    res = app_client.get('/api/commit/666')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/commit/1')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['sha'] == 'def'
    assert data['message'] == 'Dummy commit'
    assert data['push_id'] == 1


def test_get_release(filled_db_session, app_client):
    res = app_client.get('/api/release/666')
    assert res.status == '404 NOT FOUND'
    res = app_client.get('/api/release/1')
    assert res.status == '200 OK'
    data = json.loads(res.data.decode('utf-8'))
    assert data['github_id'] == 666
    assert data['tag_name'] == 'v1.0'
    assert data['repository_id'] == 1
