import hashlib
import hmac
import flask
import json
import requests


class GitHubAPI:
    """Simple GitHub API communication wrapper

    It provides simple way for getting the basic GitHub API
    resources and special methods for working with webhooks.

    :todo: handle if GitHub is out of service, custom errors,
           pagination, better abstraction, work with extensions
    """

    #: URL to GitHub API
    API_URL = 'https://api.github.com'
    #: URL for OAuth request at GitHub
    AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
    #: URL for OAuth token at GitHub
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    #: Scopes for OAuth request
    SCOPES = ['user', 'repo', 'admin:repo_hook']
    #: Required webhooks to be registered
    WEBHOOKS = ['push', 'release', 'repository']
    #: Controller for incoming webhook events
    WEBHOOK_CONTROLLER = 'webhooks.gh_webhook'

    def __init__(self, client_id, client_secret, webhooks_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhooks_secret = webhooks_secret

    @staticmethod
    def _get_auth_header():
        """Prepare auth header fields (empty if no token provided)

        :return: Headers for the request
        :rtype: dict
        """
        if 'github_token' not in flask.session:
            return {}
        return {
            'Authorization': 'token {}'.format(flask.session['github_token'])
        }

    def get_auth_url(self):
        """Create OAuth request URL

        :return: OAuth request URL
        :rtype: str
        """
        return self.AUTH_URL.format(' '.join(self.SCOPES), self.client_id)

    def login(self, session_code):
        """Authorize via OAuth with given session code

        :param session_code: The session code for OAuth
        :type session_code: str
        :return: If the auth procedure was successful
        :rtype: bool

        :todo: check granted scope vs GH_SCOPES
        """
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
        scope = [flask.escape(x) for x in data['scope'].split(',')]
        flask.session['github_token'] = token
        flask.session['github_scope'] = scope
        return True

    @classmethod
    def get_token(cls):
        """Retrieve GitHub OAuth token for current user

        :return: GitHub token for current user
        :rtype: str
        """
        return flask.session['github_token']

    @classmethod
    def get_scope(cls):
        """Retrieve GitHub OAuth scope for current user

        :return: GitHub scope for current user
        :rtype: str
        """
        return flask.session['github_scope']

    @classmethod
    def logout(cls):
        """Logout the current user from GitHub session (destroy token)"""
        for key in ('github_token', 'github_scope'):
            flask.session.pop(key, None)

    @classmethod
    def get(cls, what):
        """Perform GET request on GitHub API

        :param what: URI of requested resource
        :type what: str
        :return: Response to the GET request
        :rtype: ``requests.Response``

        :todo: pagination of content
        """
        return requests.get(
            cls.API_URL + what,
            headers=cls._get_auth_header()
        )

    @classmethod
    def get_data(cls, what):
        """Perform GET request on GitHub API

        :param what: URI of requested resource
        :type what: str
        :return: Data of the response
        :rtype: dict or None

        :todo: pagination of content
        """
        return cls.get(what).json()

    @classmethod
    def webhook_get(cls, full_name, id):
        """Perform GET request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be get
        :type hook_id: int
        :return: Data of the webhook
        :rtype: dict or None
        """
        response = cls.get('/repos/{}/hooks/{}'.format(full_name, id))
        if response.status_code == 200:
            return response.json()
        return None

    @classmethod
    def webhooks_get(cls, full_name):
        """GET all webhooks of the repository

        :param full_name: Full name of repository
        :type full_name: str
        :return: List of returned webhooks
        :rtype: list
        """
        response = cls.get('/repos/{}/hooks'.format(full_name))
        if response.status_code == 200:
            return response.json()
        return []

    def webhook_create(self, full_name, events=None, hook_url=None):
        """Create new webhook for specified repository

        :param full_name: Full name of the repository
        :type full_name: str
        :param events: List of requested events for that webhook
        :type events: list of str
        :param hook_url: URL where the webhook data will be sent
        :type hook_url: str
        :return: The created webhook data
        :rtype: dict or None
        """
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
        """Perform test request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be tested
        :type hook_id: int
        :return: If request was successful
        :rtype: bool
        """
        response = requests.delete(
            cls.API_URL + '/repos/{}/hooks/{}/tests'.format(
                full_name, hook_id
            ),
            headers=cls._get_auth_header()
        )
        return response.status_code == 204

    @classmethod
    def webhook_delete(cls, full_name, hook_id):
        """Perform DELETE request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be deleted
        :type hook_id: int
        :return: If request was successful
        :rtype: bool
        """
        response = requests.delete(
            cls.API_URL + '/repos/{}/hooks/{}'.format(
                full_name, hook_id
            ),
            headers=cls._get_auth_header()
        )
        return response.status_code == 204

    def webhook_verify_signature(self, payload, signature):
        """Verify the content with signature

        :param payload: Data of webhook message
        :type payload: dict
        :param signature: The signature of data
        :type signature: str
        :return: If the content is verified
        :rtype: bool
        """
        h = hmac.new(
            self.webhooks_secret,
            payload,
            hashlib.sha1
        )
        return hmac.compare_digest(h.hexdigest(), signature)
