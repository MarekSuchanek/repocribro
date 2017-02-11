import pytest

REPOSITORY = 'MarekSuchanek/pyplayground'
NOT_REPOSITORY = 'MarekSuchanek/pyplaygroundzzzz7'


def test_login_bad(github_api):
    assert not github_api.login('random_code')


def test_get_user_self(github_api):
    user = github_api.get('/user')
    assert user.status_code == 200
    user_data = user.json()
    assert 'login' in user_data


def test_get_webhooks_bad(github_api):
    res = github_api.webhooks_get(NOT_REPOSITORY)
    assert res == []


def test_get_webhook_bad(github_api):
    res = github_api.webhook_get(REPOSITORY, 666)
    assert res is None


def test_get_webhook_create_check(github_api):
    res = github_api.webhook_create(
        REPOSITORY, 'http://localhost:5000/test'
    )
    assert res is not None
    webhook_id = res['id']

    res = github_api.webhooks_get(REPOSITORY)
    assert len(res) >= 1
    found = False
    for webhook in res:
        if webhook['id'] == webhook_id:
            found = True
            break
    assert found

    res = github_api.webhook_get(REPOSITORY, webhook_id)
    assert res is not None
    assert res['id'] == webhook_id

    # Delivery on localhost must fail
    assert not github_api.webhook_tests(REPOSITORY, webhook_id)

    res = github_api.webhook_delete(REPOSITORY, webhook_id)
    assert res


def test_get_webhook_delete_check(github_api):
    res = github_api.webhook_create(
        REPOSITORY, 'http://localhost:5000/test'
    )
    assert res is not None
    webhook_id = res['id']

    res = github_api.webhook_delete(REPOSITORY, webhook_id)
    assert res

    res = github_api.webhook_get(REPOSITORY, webhook_id)
    assert res is None


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
