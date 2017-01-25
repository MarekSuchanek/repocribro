import flask
import requests
from ..github import GitHubAPI
from ..models import User, UserAccount, db
from ..security import login_manager, clear_session,\
    login as security_login, logout as security_logout


auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.unauthorized_handler
def unauthorized():
    flask.abort(403)


@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))


@auth.route('/github')
def github():
    return flask.redirect(GitHubAPI.get_auth_url())


def github_callback_get_account():
    user_data = GitHubAPI.get_data('/user')
    gh_user = User.query.filter(
        User.github_id == user_data['id']
    ).first()
    is_new = False
    if gh_user is None:
        user_account = UserAccount()
        db.session.add(user_account)
        gh_user = User.create_from_dict(user_data, user_account)
        db.session.add(gh_user)
        db.session.commit()
        is_new = True
    return gh_user.user_account, is_new


@auth.route('/github/callback')
def github_callback():
    session_code = flask.request.args.get('code')
    if GitHubAPI.login(session_code):
        user_account, is_new = github_callback_get_account()
        security_login(user_account)
        if not user_account.active:
            flask.flash('Sorry, but your account is deactivated. '
                        'Please contact admin for details', 'error')
            security_logout()
            GitHubAPI.logout()
            return flask.redirect(flask.url_for('core.index'))
        if is_new:
            flask.flash('You account has been created via GitHub. '
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
    security_logout()
    GitHubAPI.logout()
    flask.flash('You are now logged out, see you soon!', 'info')
    return flask.redirect(flask.url_for('core.index'))
