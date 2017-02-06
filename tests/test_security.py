import flask_login
import pytest
from werkzeug.exceptions import Forbidden


from repocribro.security import login, logout, permissions
from repocribro.models import UserAccount, Role


def test_login_logout(app, empty_db_session):
    with app.test_request_context('/'):
        account = UserAccount()
        account.id = 666
        empty_db_session.add(account)
        empty_db_session.commit()
        login(account)
        assert flask_login.current_user.id == 666
        logout()
        assert flask_login.current_user.is_anonymous


def test_permission_admin(app, empty_db_session):
    with app.test_request_context('/'):
        @permissions.admin_role.require(403)
        def test():
            return 200

        with pytest.raises(Forbidden):
            assert test() == 200

        role_admin = Role('admin', '')
        account = UserAccount()
        account.id = 666
        account.roles.append(role_admin)
        empty_db_session.add(role_admin)
        empty_db_session.add(account)
        empty_db_session.commit()
        login(account)
