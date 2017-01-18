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
    ))


@auth.route('/github/callback')
def github_callback():
    session_code = flask.request.args.get('code')
    client_id = flask.current_app.config['GH_BASIC_CLIENT_ID']
    client_secret = flask.current_app.config['GH_BASIC_CLIENT_SECRET']
    response = requests.post(
        GH_TOKEN_URL,
        headers={
            'Accept': 'application/json'
        },
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': session_code,
        }
    )
    if response.status_code == 200:
        data = response.json()
        token = flask.escape(data['access_token'])
        scopes = [flask.escape(x) for x in data['scope'].split(',')]
        flask.session['github_token'] = token
        flask.session['github_scope'] = scopes
        # TODO: register/retrieve user (DB)
        # TODO: store user ID in session
        flask.flash('You are now logged in via GitHub.', 'success')
        return flask.redirect(flask.url_for('user.dashboard'))
    else:
        # TODO: log error
        flask.flash('Woops, we are not able to authenticate '
                    'you via GitHub now!', 'danger')
        return flask.redirect(flask.url_for('core.index'))


@auth.route('/logout')
def logout():
    # TODO: store info about user_attrs somewhere else
    for user_attr in ['github_token', 'github_scope']:
        flask.session.pop(user_attr, None)
    flask.flash('You are now logged out, see you soon!', 'info')
    return flask.redirect(flask.url_for('core.index'))
