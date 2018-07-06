import datetime
import pytest
from sqlalchemy.exc import OperationalError

from repocribro.commands.assign_role import _assign_role
from repocribro.commands.check_config import _check_config
from repocribro.commands.db_create import _db_create
from repocribro.commands.repocheck import _repocheck
from repocribro.models import User, Repository


def test_assign_role(filled_db_session):
    user = filled_db_session.query(User).filter_by(login='regular').first()
    assert not user.user_account.has_role('admin')
    assert not user.user_account.has_role('new_role')
    assert len(user.user_account.roles) == 0

    _assign_role('regular', 'admin')
    assert user.user_account.has_role('admin')
    assert len(user.user_account.roles) == 1
    _assign_role('regular', 'new_role')
    assert user.user_account.has_role('new_role')
    assert len(user.user_account.roles) == 2
    with pytest.raises(SystemExit) as exodus:
        _assign_role('regular', 'admin')
    assert exodus.value.code == 2
    with pytest.raises(SystemExit) as exodus:
        _assign_role('nonexistent', 'admin')
    assert exodus.value.code == 1


def test_create_db(db):
    db.drop_all()
    with pytest.raises(OperationalError) as exodus:
        db.session.query(User).filter_by(login='regular').first()
    assert 'no such table' in str(exodus.value)
    _db_create()
    db.session.query(User).filter_by(login='regular').first()


def test_repocheck_invalid(filled_db_session, app_client):
    app_client.get('/test/fake-github')

    with pytest.raises(SystemExit) as exodus:
        _repocheck('nonexistent')
    assert exodus.value.code == 1

    repo = Repository(105, None, 'regular/repo4', 'repo4', 'Python', '', '',
                      '', False, None, None, Repository.VISIBILITY_PUBLIC)
    filled_db_session.add(repo)
    filled_db_session.commit()

    with pytest.raises(SystemExit) as exodus:
        _repocheck('regular/repo4')
    assert exodus.value.code == 3


def test_repocheck_push_single(filled_db_session, app_client):
    app_client.get('/test/fake-github')

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2020', '%d-%m-%Y')
    _repocheck('regular/repo1')
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2010', '%d-%m-%Y')
    _repocheck('regular/repo1')
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 2
    assert len(repo1.releases) == 2


def test_repocheck_push_all(filled_db_session, app_client):
    app_client.get('/test/fake-github')

    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2020', '%d-%m-%Y')
    _repocheck()
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 1
    assert len(repo1.releases) == 1
    repo1.last_event = datetime.datetime.strptime('1-1-2010', '%d-%m-%Y')
    _repocheck()
    repo1 = filled_db_session.query(Repository).filter_by(
        full_name='regular/repo1'
    ).first()
    assert len(repo1.pushes) == 2
    assert len(repo1.releases) == 2


def test_check_config(capsys):
    _check_config('triple')
    out, err = capsys.readouterr()
    assert 'flask server_name repocribro.test' in out.lower()
    assert 'github client_secret some_client_secret' in out.lower()
