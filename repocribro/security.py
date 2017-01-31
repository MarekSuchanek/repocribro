import flask
import flask_login
import flask_principal

from .models import UserAccount, Anonymous


def init_login_manager(db):
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
    # TODO: load roles & their names from somewhere else
    admin_role = flask_principal.Permission(
        flask_principal.RoleNeed('admin')
    )

permissions = Permissions()


def login(user_account):
    flask_login.login_user(user_account)
    flask_principal.identity_changed.send(
        flask_principal.current_app._get_current_object(),
        identity=flask_principal.Identity(user_account.id)
    )


def logout():
    flask_login.logout_user()
    clear_session('identity.name', 'identity.auth_type')
    flask_principal.identity_changed.send(
        flask.current_app._get_current_object(),
        identity=flask_principal.AnonymousIdentity()
    )


def clear_session(*args):
    for key in args:
        flask.session.pop(key, None)


@flask_principal.identity_loaded.connect
def on_identity_loaded(sender, identity):
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
