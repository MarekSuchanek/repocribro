import pytest
from sqlalchemy.exc import OperationalError

from repocribro.commands import AssignRoleCommand, DbCreateCommand, \
    RepocheckCommand
from repocribro.models import User


def test_assign_role(filled_db_session):
    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert not user.user_account.has_role('admin')
    assert not user.user_account.has_role('new_role')
    assert len(user.user_account.roles) == 0
    cmd = AssignRoleCommand()
    cmd.run('regular', 'admin')
    assert user.user_account.has_role('admin')
    assert len(user.user_account.roles) == 1
    cmd.run('regular', 'new_role')
    assert user.user_account.has_role('new_role')
    assert len(user.user_account.roles) == 2
    with pytest.raises(SystemExit) as exodus:
        cmd.run('regular', 'admin')
    assert exodus.value.code == 2
    with pytest.raises(SystemExit) as exodus:
        cmd.run('nonexistent', 'admin')
    assert exodus.value.code == 1


def test_create_db(db):
    db.drop_all()
    with pytest.raises(OperationalError) as exodus:
        db.session.query(User).filter_by(login='regular').first()
    assert 'no such table' in str(exodus.value)
    cmd = DbCreateCommand()
    cmd.run()
    db.session.query(User).filter_by(login='regular').first()


def test_repocheck(filled_db_session):
    cmd = RepocheckCommand()
    with pytest.raises(SystemExit) as exodus:
        cmd.run('nonexistent')
    assert exodus.value.code == 1
    # TODO: test updating repo
