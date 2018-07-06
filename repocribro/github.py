import hashlib
import hmac
import json
import requests


class GitHubResponse:
    """Wrapper for GET request response from GitHub"""

    def __init__(self, response):
        self.response = response

    @property
    def is_ok(self):
        """Check if request has been successful

        :return: if it was OK
        :rtype: bool
        """
        return self.response.status_code < 300

    @property
    def data(self):
        """Response data as dict/list

        :return: data of response
        :rtype: dict|list
        """
        return self.response.json()

    @property
    def url(self):
        """URL of the request leading to this response

        :return: URL origin
        :rtype: str
        """
        return self.response.url

    @property
    def links(self):
        """Response header links

        :return: URL origin
        :rtype: dict
        """
        return self.response.links

    @property
    def is_first_page(self):
        """Check if this is the first page of data

        :return:  if it is the first page of data
        :rtype: bool
        """
        return 'first' not in self.links

    @property
    def is_last_page(self):
        """Check if this is the last page of data

        :return:  if it is the last page of data
        :rtype: bool
        """
        return 'last' not in self.links

    @property
    def is_only_page(self):
        """Check if this is the only page of data

        :return: if it is the only page page of data
        :rtype: bool
        """
        return self.is_first_page and self.is_last_page

    @property
    def total_pages(self):
        """Number of pages

        :return: number of pages
        :rtype: int
        """
        if 'last' not in self.links:
            return self.actual_page
        return self.parse_page_number(self.links['last']['url'])

    @property
    def actual_page(self):
        """Actual page number

        :return: actual page number
        :rtype: int
        """
        return self.parse_page_number(self.url)

    @staticmethod
    def parse_page_number(url):
        """Parse page number from GitHub GET URL

        :param url: URL used for GET request
        :type url: str
        :return: page number
        :rtype: int
        """
        if '?' not in url:
            return 1
        params = url.split('?')[1].split('=')
        params = {k: v for k, v in zip(params[0::2], params[1::2])}
        if 'page' not in params:
            return 1
        return int(params['page'])


class GitHubAPI:
    """Simple GitHub API communication wrapper

    It provides simple way for getting the basic GitHub API
    resources and special methods for working with webhooks.

    .. todo:: handle if GitHub is out of service, custom errors,
             better abstraction, work with extensions
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
    #: URL for checking connections within GitHub
    CONNECTIONS_URL = 'https://github.com/settings/connections/applications/{}'

    def __init__(self, client_id, client_secret, webhooks_secret,
                 session=None, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhooks_secret = webhooks_secret
        self.session = session or requests.Session()
        self.token = token
        self.scope = []

    def _get_headers(self):
        """Prepare auth header fields (empty if no token provided)

        :return: Headers for the request
        :rtype: dict
        """
        if self.token is None:
            return {}
        return {
            'Authorization': 'token {}'.format(self.token),
            'Accept': 'application/vnd.github.mercy-preview+json'
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

        .. todo:: check granted scope vs GH_SCOPES
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

    def get(self, what, page=0):
        """Perform GET request on GitHub API

        :param what: URI of requested resource
        :type what: str
        :param page: Number of requested page
        :type page: int
        :return: Response from the GitHub
        :rtype: ``repocribro.github.GitHubResponse``
        """
        uri = self.API_URL + what
        if page > 0:
            uri += '?page={}'.format(page)
        return GitHubResponse(self.session.get(
            uri,
            headers=self._get_headers()
        ))

    def webhook_get(self, full_name, hook_id):
        """Perform GET request for repo's webhook

        :param full_name: Full name of repository that contains the hook
        :type full_name: str
        :param hook_id: GitHub ID of hook to be get
        :type hook_id: int
        :return: Data of the webhook
        :rtype: ``repocribro.github.GitHubResponse``
        """
        return self.get('/repos/{}/hooks/{}'.format(full_name, hook_id))

    def webhooks_get(self, full_name):
        """GET all webhooks of the repository

        :param full_name: Full name of repository
        :type full_name: str
        :return: List of returned webhooks
        :rtype: ``repocribro.github.GitHubResponse``
        """
        return self.get('/repos/{}/hooks'.format(full_name))

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
            headers=self._get_headers()
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
            headers=self._get_headers()
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
            headers=self._get_headers()
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

    @property
    def app_connections_link(self):
        return self.CONNECTIONS_URL.format(self.client_id)
