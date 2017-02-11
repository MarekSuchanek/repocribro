import flask
import flask_sqlalchemy

from ..models import User, UserAccount
from ..security import login as security_login, logout as security_logout

#: Auth controller blueprint
auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/github')
def github():
    """Redirect to GitHub OAuth gate (GET handler)"""
    gh_api = flask.current_app.container.get('gh_api')

    return flask.redirect(gh_api.get_auth_url())


def github_callback_get_account(db, gh_api):
    """Processing GitHub callback action

    :param db: Database for storing GitHub user info
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :param gh_api: GitHub API client ready for the communication
    :type gh_api: ``repocribro.github.GitHubAPI``
    :return: User account and flag if it's new one
    :rtype: tuple of ``repocribro.models.UserAccount``, bool
    """
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
def github_callback():
    """Callback gate for GitHub OAUTH (GET handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get('gh_api')

    session_code = flask.request.args.get('code')
    if gh_api.login(session_code):
        flask.session['github_token'] = gh_api.token
        flask.session['github_scope'] = gh_api.scope
        user_account, is_new = github_callback_get_account(db, gh_api)
        security_login(user_account)
        if not user_account.active:
            flask.flash('Sorry, but your account is deactivated. '
                        'Please contact admin for details', 'error')
            security_logout()
            flask.session.pop('github_token')
            flask.session.pop('github_scope')
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
def logout():
    """Logout currently logged user (GET handler)"""
    security_logout()
    flask.session.pop('github_token')
    flask.session.pop('github_scope')
    flask.flash('You are now logged out, see you soon!', 'info')
    return flask.redirect(flask.url_for('core.index'))
