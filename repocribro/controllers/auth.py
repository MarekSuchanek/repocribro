import flask
import flask_login
import requests
from ..models import User, UserAccount, db
from ..extensions import login_manager

auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


GH_API = 'https://api.github.com'
GH_AUTH_URL = 'https://github.com/login/oauth/authorize?scope={}&client_id={}'
GH_TOKEN_URL = 'https://github.com/login/oauth/access_token'


@login_manager.unauthorized_handler
def unauthorized():
    flask.abort(403)


@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))


@auth.route('/github')
def github():
    return flask.redirect(GH_AUTH_URL.format(
        'user repo',
        flask.current_app.config['GH_BASIC_CLIENT_ID']
    ))


def github_callback_get_account():
    response = requests.get(
        GH_API + '/user',
        params={'access_token': flask.session['github_token']}
    )
    gh_user = User.query.filter(
        User.github_id == response.json()['id']
    ).first()
    is_new = False
    if gh_user is None:
        user_account = UserAccount()
        db.session.add(user_account)
        gh_user = User.create_from_dict(response.json(), user_account)
        db.session.add(gh_user)
        db.session.commit()
        is_new = True
    return gh_user.user_account, is_new


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
    # TODO: check granted scopes
    if response.status_code == 200:
        data = response.json()
        token = flask.escape(data['access_token'])
        scopes = [flask.escape(x) for x in data['scope'].split(',')]
        flask.session['github_token'] = token
        flask.session['github_scope'] = scopes
        user_account, is_new = github_callback_get_account()
        flask_login.login_user(user_account)
        if is_new:
            flask.flash('You account has been created via GitHub.'
                        'Welcome in repocribro!', 'success')
        else:
            flask.flash('You are now logged in via GitHub.', 'success')
        return flask.redirect(flask.url_for('user.dashboard'))
    else:
        # TODO: log error
        flask.flash('Woops, we are not able to authenticate '
                    'you via GitHub now!', 'danger')
        return flask.redirect(flask.url_for('core.index'))


@auth.route('/logout')
def logout():
    flask_login.logout_user()
    # TODO: store info about user_attrs somewhere else
    for user_attr in ['github_token', 'github_scope']:
        flask.session.pop(user_attr, None)
    flask.flash('You are now logged out, see you soon!', 'info')
    return flask.redirect(flask.url_for('core.index'))
