import datetime
import pytest
from sqlalchemy.exc import OperationalError

from repocribro.commands import AssignRoleCommand, DbCreateCommand, \
    RepocheckCommand
from repocribro.models import User, Repository


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


def test_repocheck_invalid(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    cmd = RepocheckCommand()

    with pytest.raises(SystemExit) as exodus:
        cmd.run('nonexistent')
    assert exodus.value.code == 1

    repo = Repository(105, None, 'regular/repo4', 'repo4', 'Python', '',
                      '', False, None, None, Repository.VISIBILITY_PUBLIC)
    filled_db_session.add(repo)
    filled_db_session.commit()

    cmd = RepocheckCommand()
    with pytest.raises(SystemExit) as exodus:
        cmd.run('regular/repo4')
    assert exodus.value.code == 3


def test_repocheck_push_single(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    cmd = RepocheckCommand()

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2020', '%d-%m-%Y')
    cmd.run('regular/repo1')
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2010', '%d-%m-%Y')
    cmd.run('regular/repo1')
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 2
    assert len(repo1.releases) == 2


def test_repocheck_push_all(filled_db_session, app_client):
    app_client.get('/test/fake-github')
    cmd = RepocheckCommand()

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2020', '%d-%m-%Y')
    cmd.run()
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2010', '%d-%m-%Y')
    cmd.run()
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 2
    assert len(repo1.releases) == 2
