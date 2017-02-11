import pytest


def test_login_bad(github_api):
    assert not github_api.login('random_code')


def test_get_user_self(github_api):
    user = github_api.get('/user')
    assert user.status_code == 200
    user_data = user.json()
    assert 'login' in user_data


def test_get_webhooks(github_api):
    res = github_api.webhooks_get('MarekSuchanek/pyplayground')
    assert isinstance(res, list)


def test_get_webhook_create(github_api):
    res = github_api.webhooks_get('MarekSuchanek/pyplayground'
                                  'http://localhost:5000/test')
    assert res is not None


def compute_signature(payload, secret):
    import hmac
    import hashlib
    h = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha1
    )
    return h.hexdigest()


@pytest.mark.parametrize('payload', [
    'aasas', '["a","b","c"]', '{"nope":"nope"}'
])
def test_get_webhook_verify(github_api, payload):
    sig = compute_signature(payload, github_api.webhooks_secret)
    assert github_api.webhook_verify_signature(
        payload.encode('utf-8'), sig
    )


@pytest.mark.parametrize('payload', [
    'aasas', '["a","b","c"]', '{"nope":"nope"}'
])
def test_get_webhook_unverify(github_api, payload):
    sig = compute_signature(payload, github_api.webhooks_secret) + 'xxx'
    assert not github_api.webhook_verify_signature(
        payload.encode('utf-8'), sig
    )
