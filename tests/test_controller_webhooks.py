import json
import pytest

from repocribro.models import Repository


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


def compute_signature(payload, secret):
    import hmac
    import hashlib
    h = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha1
    )
    return h.hexdigest()


def test_webhook_push(filled_db_session, app_client, github_data_loader, app):
    push_payload = json.dumps(github_data_loader('webhooks/push'))
    secret = app.container.get('gh_api').webhooks_secret

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1

    app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=push_payload,
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
            'X-GitHub-Event': 'push',
            'X-GitHub-Signature': compute_signature(push_payload, secret)
        }
    )
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 2


def test_webhook_release(filled_db_session, app_client,
                         github_data_loader, app):
    push_payload = json.dumps(github_data_loader('webhooks/release'))
    secret = app.container.get('gh_api').webhooks_secret

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.releases) == 1

    app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=push_payload,
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9456dc0958',
            'X-GitHub-Event': 'release',
            'X-GitHub-Signature': compute_signature(push_payload, secret)
        }
    )
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.releases) == 2


@pytest.mark.parametrize(('data', 'visibility'), [
    ('webhooks/repository1', Repository.VISIBILITY_PRIVATE),
    ('webhooks/repository2', Repository.VISIBILITY_PUBLIC),
    ('webhooks/repository3', Repository.VISIBILITY_PRIVATE)
])
def test_webhook_repository(filled_db_session, app_client, github_data_loader,
                            data, visibility, app):
    push_payload = json.dumps(github_data_loader(data))
    secret = app.container.get('gh_api').webhooks_secret

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    repo1.visibility_type = Repository.VISIBILITY_HIDDEN
    filled_db_session.commit()
    assert repo1.visibility_type == Repository.VISIBILITY_HIDDEN

    app_client.post(
        '/webhook/github',
        content_type='application/json',
        data=push_payload,
        headers={
            'User-Agent': 'GitHub-Hookshot/test',
            'X-Github-Delivery': '72d3162e-cc78-11e3-81ab-4c9456dc0958',
            'X-GitHub-Event': 'repository',
            'X-GitHub-Signature': compute_signature(push_payload, secret)
        }
    )
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert repo1.visibility_type == visibility
