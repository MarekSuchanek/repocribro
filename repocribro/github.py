import flask
import requests


# TODO: handle if GitHub is out of service
class GitHubAPI:
    API_URL = 'https://api.github.com'
    AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    SCOPES = ['user', 'repo']

    @classmethod
    def get_auth_url(cls):
        return cls.AUTH_URL.format(
            cls.SCOPES,
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
            params={'access_token': flask.session['github_token']}
        )

    @classmethod
    def get_data(cls, what):
        return cls.get(what).json()

