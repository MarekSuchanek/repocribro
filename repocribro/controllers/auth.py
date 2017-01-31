import flask
import flask_sqlalchemy
import injector

from ..github import GitHubAPI
from ..models import User, UserAccount
from ..security import login as security_login, logout as security_logout

auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/github')
@injector.inject(gh_api=GitHubAPI)
def github(gh_api):
    return flask.redirect(gh_api.get_auth_url())


def github_callback_get_account(db, gh_api):
    user_data = gh_api.get_data('/user')
    gh_user = db.session.query(User).filter(
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
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def github_callback(db, gh_api):
    session_code = flask.request.args.get('code')
    if gh_api.login(session_code):
        user_account, is_new = github_callback_get_account(db, gh_api)
        security_login(user_account)
        if not user_account.active:
            flask.flash('Sorry, but your account is deactivated. '
                        'Please contact admin for details', 'error')
            security_logout()
            gh_api.logout()
            return flask.redirect(flask.url_for('core.index'))
        if is_new:
            flask.flash('You account has been created via GitHub. '
                        'Welcome in repocribro!', 'success')
        else:
            flask.flash('You are now logged in via GitHub.', 'success')
        return flask.redirect(flask.url_for('manage.dashboard'))
    else:
        flask.flash('Whoops, we are not able to authenticate '
                    'you via GitHub now!', 'error')
        return flask.redirect(flask.url_for('core.index'))


@auth.route('/logout')
@injector.inject(gh_api=GitHubAPI)
def logout(gh_api):
    security_logout()
    gh_api.logout()
    flask.flash('You are now logged out, see you soon!', 'info')
    return flask.redirect(flask.url_for('core.index'))
