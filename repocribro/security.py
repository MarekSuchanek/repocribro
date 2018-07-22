import flask
import flask_login
import flask_principal

from .models import UserAccount, Anonymous, Role


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


class PermissionsContainer:

    def __init__(self, name):
        self.x_name = name
        self.x_dict = dict()

    def __getattr__(self, key):
        return flask_principal.Permission(*self.x_dict[key])


class Permissions:
    """ Class for prividing various permissions"""

    def __init__(self):
        self.roles = PermissionsContainer('roles')
        self.actions = PermissionsContainer('actions')

    def register_role(self, role_name):
        self.roles.x_dict[role_name] = \
            (flask_principal.RoleNeed(role_name),)

    def register_action(self, priv_name):
        self.actions.x_dict[priv_name] = \
            (flask_principal.ActionNeed(priv_name),)

    @property
    def all_roles(self):
        return set(self.roles.x_dict.keys())

    @property
    def all_actions(self):
        return set(self.actions.x_dict.keys())


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


def reload_anonymous_role(app, db):
    with app.app_context():
        anonymous_role = db.session.query(Role).filter_by(
            name=Anonymous.rolename
        ).first()
        if anonymous_role is not None:
            Anonymous.roles.append(anonymous_role)


@flask_principal.identity_loaded.connect
def on_identity_loaded(sender, identity):
    """Principal helper for loading the identity of logged user

    :param sender: Sender of the signal
    :param identity: Identity container
    :type identity: ``flask_principal.Identity``
    """
    user = flask_login.current_user
    identity.user = user

    if hasattr(user, 'id'):
        identity.provides.add(
            flask_principal.UserNeed(flask_login.current_user.id)
        )

    if hasattr(user, 'roles'):
        for role in user.roles:
            identity.provides.add(
                flask_principal.RoleNeed(role.name)
            )
        for priviledge in user.privileges(permissions.all_actions):
            identity.provides.add(
                flask_principal.ActionNeed(priviledge)
            )
