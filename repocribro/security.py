import flask
import flask_login
import flask_principal

login_manager = flask_login.LoginManager()
principals = flask_principal.Principal()

admin_permission = flask_principal.Permission(
    flask_principal.RoleNeed('admin')
)

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
