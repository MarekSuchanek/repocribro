import json


def test_webhook_fail_user_agent(filled_db_session, app_client):
    res = app_client.post(
        '/webhook/github',
        headers={'User-Agent': 'PythonRulez'}
    )
    assert res.status == '404 NOT FOUND'


def test_webhook_fail_no_data(filled_db_session, app_client):
    res = app_client.post(
        '/webhook/github',
        headers={'User-Agent': 'GitHub-Hookshot/test'}
    )
    assert res.status == '404 NOT FOUND'


def test_webhook_fail_no_repo(filled_db_session, app_client):
    res = app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=json.dumps({
            'action': 'opened',
            'norepo': 'nonono'
        }),
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
            'X-GitHub-Event': 'issues'
        }
    )
    assert res.status == '404 NOT FOUND'


def test_webhook_fail_no_signature(filled_db_session, app_client):
    res = app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=json.dumps({
            'action': 'opened',
            'repository': {'id': 777}
        }),
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
            'X-GitHub-Event': 'issues'
        }
    )
    assert res.status == '404 NOT FOUND'


def test_webhook_fail_bad_signature(filled_db_session, app_client):
    res = app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=json.dumps({
            'action': 'opened',
            'repository': {'id': 777}
        }),
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
            'X-GitHub-Event': 'issues',
            'X-GitHub-Signature': 'nope'
        }
    )
    assert res.status == '404 NOT FOUND'


# TODO: ok test as events
