import hashlib
import hmac
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

    def __init__(self, client_id, client_secret, webhooks_secret,
                 session=None, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhooks_secret = webhooks_secret
        self.session = session or requests.Session()
        self.token = token
        self.scope = []

    def _get_auth_header(self):
        """Prepare auth header fields (empty if no token provided)

        :return: Headers for the request
        :rtype: dict
        """
        if self.token is None:
            return {}
        return {
            'Authorization': 'token {}'.format(self.token)
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
        response = self.session.post(
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
        self.token = data['access_token']
        self.scope = [x for x in data['scope'].split(',')]
        return True

    def get(self, what):
        """Perform GET request on GitHub API

        :param what: URI of requested resource
        :type what: str
        :return: Response to the GET request
        :rtype: ``requests.Response``

        :todo: pagination of content
        """
        return self.session.get(
            self.API_URL + what,
            headers=self._get_auth_header()
        )

    def get_data(self, what):
        """Perform GET request on GitHub API

        :param what: URI of requested resource
        :type what: str
        :return: Data of the response
        :rtype: dict or None

        :todo: pagination of content
        """
        return self.get(what).json()

    def webhook_get(self, full_name, id):
        """Perform GET request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be get
        :type hook_id: int
        :return: Data of the webhook
        :rtype: dict or None
        """
        response = self.get('/repos/{}/hooks/{}'.format(full_name, id))
        if response.status_code == 200:
            return response.json()
        return None

    def webhooks_get(self, full_name):
        """GET all webhooks of the repository

        :param full_name: Full name of repository
        :type full_name: str
        :return: List of returned webhooks
        :rtype: list
        """
        response = self.get('/repos/{}/hooks'.format(full_name))
        if response.status_code == 200:
            return response.json()
        return []

    def webhook_create(self, full_name, hook_url, events=None):
        """Create new webhook for specified repository

        :param full_name: Full name of the repository
        :type full_name: str
        :param hook_url: URL where the webhook data will be sent
        :type hook_url: str
        :param events: List of requested events for that webhook
        :type events: list of str
        :return: The created webhook data
        :rtype: dict or None
        """
        if events is None:
            events = self.WEBHOOKS
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
        response = self.session.post(
            self.API_URL + '/repos/{}/hooks'.format(full_name),
            data=json.dumps(data),
            headers=self._get_auth_header()
        )
        if response.status_code == 201:
            return response.json()
        return None

    def webhook_tests(self, full_name, hook_id):
        """Perform test request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be tested
        :type hook_id: int
        :return: If request was successful
        :rtype: bool
        """
        response = self.session.delete(
            self.API_URL + '/repos/{}/hooks/{}/tests'.format(
                full_name, hook_id
            ),
            headers=self._get_auth_header()
        )
        return response.status_code == 204

    def webhook_delete(self, full_name, hook_id):
        """Perform DELETE request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be deleted
        :type hook_id: int
        :return: If request was successful
        :rtype: bool
        """
        response = self.session.delete(
            self.API_URL + '/repos/{}/hooks/{}'.format(
                full_name, hook_id
            ),
            headers=self._get_auth_header()
        )
        return response.status_code == 204

    def webhook_verify_signature(self, data, signature):
        """Verify the content with signature

        :param data: Request data to be verified
        :param signature: The signature of data
        :type signature: str
        :return: If the content is verified
        :rtype: bool
        """
        h = hmac.new(
            self.webhooks_secret.encode('utf-8'),
            data,
            hashlib.sha1
        )
        return hmac.compare_digest(h.hexdigest(), signature)
