import flask
import flask_login
import flask_principal

from .models import UserAccount, Anonymous


def init_login_manager(db):
    """Init security extensions (login manager and principal)

    :param db: Database which stores user accounts and roles
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :return: Login manager and principal extensions
    :rtype: (``flask_login.LoginManager``, ``flask_principal.Principal``
    """
    login_manager = flask_login.LoginManager()
    principals = flask_principal.Principal()
    login_manager.anonymous_user = Anonymous

    @login_manager.unauthorized_handler
    def unauthorized():
        flask.abort(403)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(UserAccount).get(int(user_id))

    return login_manager, principals


class Permissions:
    """ Class for prividing various permissions

    :todo: allow extensions provide permissions to others
    """

    #: Administrator role permission
    admin_role = flask_principal.Permission(
        flask_principal.RoleNeed('admin')
    )

#: All permissions in the app
permissions = Permissions()


def login(user_account):
    """Login desired user into the app

    :param user_account: User account to be logged in
    :type user_account: ``repocribro.models.UserAccount``
    """
    flask_login.login_user(user_account)
    flask_principal.identity_changed.send(
        flask_principal.current_app._get_current_object(),
        identity=flask_principal.Identity(user_account.id)
    )


def logout():
    """Logout the current user from the app"""
    flask_login.logout_user()
    clear_session('identity.name', 'identity.auth_type')
    flask_principal.identity_changed.send(
        flask.current_app._get_current_object(),
        identity=flask_principal.AnonymousIdentity()
    )


def clear_session(*args):
    """Simple helper for clearing variables from session

    :param args: names of session variables to remove
    """
    for key in args:
        flask.session.pop(key, None)


@flask_principal.identity_loaded.connect
def on_identity_loaded(sender, identity):
    """Principal helper for loading the identity of logged user

    :param sender: Sender of the signal
    :param identity: Identity container
    :type identity: ``flask_principal.Identity``
    """
    identity.user = flask_login.current_user

    if hasattr(flask_login.current_user, 'id'):
        identity.provides.add(
            flask_principal.UserNeed(flask_login.current_user.id)
        )

    if hasattr(flask_login.current_user, 'roles'):
        for role in flask_login.current_user.roles:
            identity.provides.add(
                flask_principal.RoleNeed(role.name)
            )
