import flask
import requests

auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


GH_AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
GH_TOKEN_URL = 'https://github.com/login/oauth/access_token'


@auth.route('/github')
def github():
    return flask.redirect(GH_AUTH_URL.format(
        'user:email repo',
        flask.current_app.config['GH_BASIC_CLIENT_ID']
    ), 302)


@auth.route('/github/callback')
def github_callback():
    session_code = flask.request.args.get('code')
    client_id = flask.current_app.config['GH_BASIC_CLIENT_ID']
    client_secret = flask.current_app.config['GH_BASIC_CLIENT_SECRET']
    response = requests.post(
        GH_TOKEN_URL,
        headers = {
            'Accept': 'application/json'
        },
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': session_code,
        }
    )
    if response.status_code == 200:
        # TODO: store scopes and token in session
        # TODO: register/retrieve user (DB)
        # TODO: store user ID in session
        # TODO: redirect with flash success msg
        return flask.jsonify(response.json())
    else:
        # TODO: log error
        # TODO: redirect with flash error msg
        return flask.jsonify(response.status_code)
