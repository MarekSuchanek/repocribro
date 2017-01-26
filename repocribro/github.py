import hashlib
import hmac
import flask
import json
import requests


# TODO: handle if GitHub is out of service
class GitHubAPI:
    API_URL = 'https://api.github.com'
    AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    SCOPES = ['user', 'repo', 'admin:repo_hook']
    WEBHOOKS = ['push', 'release', 'repository']
    WEBHOOK_CONTROLLER = 'webhooks.gh_webhook'

    @staticmethod
    def _get_auth_header():
        return {
            'Authorization': 'token {}'.format(flask.session['github_token'])
        }

    @classmethod
    def get_auth_url(cls):
        return cls.AUTH_URL.format(
            ' '.join(cls.SCOPES),
            flask.current_app.config['GH_BASIC_CLIENT_ID']
        )

    @classmethod
    def login(cls, session_code):
        client_id = flask.current_app.config['GH_BASIC_CLIENT_ID']
        client_secret = flask.current_app.config['GH_BASIC_CLIENT_SECRET']
        response = requests.post(
            cls.TOKEN_URL,
            headers={
                'Accept': 'application/json'
            },
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': session_code,
            }
        )
        if response.status_code != 200:
            return False
        data = response.json()
        token = flask.escape(data['access_token'])
        # TODO: check granted scope vs GH_SCOPES
        scope = [flask.escape(x) for x in data['scope'].split(',')]
        flask.session['github_token'] = token
        flask.session['github_scope'] = scope
        return True

    @classmethod
    def get_token(cls):
        return flask.session['github_token']

    @classmethod
    def get_scope(cls):
        return flask.session['github_scope']

    @classmethod
    def logout(cls):
        for key in ('github_token', 'github_scope'):
            flask.session.pop(key, None)

    @classmethod
    def get(cls, what):
        # TODO: deal with pagination
        return requests.get(
            cls.API_URL + what,
            headers=cls._get_auth_header()
        )

    @classmethod
    def get_data(cls, what):
        return cls.get(what).json()

    @classmethod
    def webhook_get(cls, full_name, id):
        response = cls.get('/repos/{}/hooks/{}'.format(full_name, id))
        if response.status_code == 200:
            return response.json()
        return None

    @classmethod
    def webhooks_get(cls, full_name):
        response = cls.get('/repos/{}/hooks'.format(full_name))
        if response.status_code == 200:
            return response.json()
        return []

    @classmethod
    def webhook_create(cls, full_name, events=None, hook_url=None):
        if events is None:
            events = cls.WEBHOOKS
        if hook_url is None:
            hook_url = flask.url_for(cls.WEBHOOK_CONTROLLER)
        data = {
            'name': 'web',
            'active': True,
            'events': events,
            'config': {
                'url': hook_url,
                'content_type': 'json',
                'secret': flask.current_app.config['GH_BASIC_WEBHOOKS_SECRET']
            }
        }
        response = requests.post(
            cls.API_URL + '/repos/{}/hooks'.format(full_name),
            data=json.dumps(data),
            headers=cls._get_auth_header()
        )
        if response.status_code == 201:
            return response.json()
        return None

    @classmethod
    def webhook_tests(cls, full_name, hook_id):
        response = requests.delete(
            cls.API_URL + '/repos/{}/hooks/{}/tests'.format(
                full_name, hook_id
            ),
            headers=cls._get_auth_header()
        )
        return response.status_code == 204

    @classmethod
    def webhook_delete(cls, full_name, hook_id):
        response = requests.delete(
            cls.API_URL + '/repos/{}/hooks/{}'.format(
                full_name, hook_id
            ),
            headers=cls._get_auth_header()
        )
        return response.status_code == 204

    @staticmethod
    def webhook_verify_signature(payload, signature):
        h = hmac.new(
            flask.current_app.config['GH_BASIC_WEBHOOKS_SECRET'],
            payload,
            hashlib.sha1
        )
        return hmac.compare_digest(h.hexdigest(), signature)
