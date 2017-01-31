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

    def __init__(self, client_id, client_secret, webhooks_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhooks_secret = webhooks_secret

    @staticmethod
    def _get_auth_header():
        return {
            'Authorization': 'token {}'.format(flask.session['github_token'])
        }

    def get_auth_url(self):
        return self.AUTH_URL.format(' '.join(self.SCOPES), self.client_id)

    def login(self, session_code):
        response = requests.post(
            self.TOKEN_URL,
            headers={
                'Accept': 'application/json'
            },
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
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

    def webhook_create(self, full_name, events=None, hook_url=None):
        if events is None:
            events = self.WEBHOOKS
        if hook_url is None:
            hook_url = flask.url_for(self.WEBHOOK_CONTROLLER, _external=True)
        data = {
            'name': 'web',
            'active': True,
            'events': events,
            'config': {
                'url': hook_url,
                'content_type': 'json',
                'secret': self.webhooks_secret
            }
        }
        response = requests.post(
            self.API_URL + '/repos/{}/hooks'.format(full_name),
            data=json.dumps(data),
            headers=self._get_auth_header()
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

    def webhook_verify_signature(self, payload, signature):
        h = hmac.new(
            self.webhooks_secret,
            payload,
            hashlib.sha1
        )
        return hmac.compare_digest(h.hexdigest(), signature)
