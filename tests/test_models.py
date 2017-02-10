from repocribro.models import *


def test_user_account(empty_db_session):
    # clean DB for this testfile
    user_account = UserAccount()

    empty_db_session.add(user_account)
    empty_db_session.commit()

    assert user_account.id > 0
    assert empty_db_session.query(UserAccount).first() == user_account
    assert str(user_account.id) in repr(user_account)
    assert 'UserAccount' in repr(user_account)


def test_user(session, github_data_loader):
    user_data = github_data_loader('user')
    user_account = session.query(UserAccount).first()
    user = User.create_from_dict(user_data, user_account)

    session.add(user)
    session.commit()

    assert user.id > 0
    assert session.query(User).first() == user
    assert str(user.id) in repr(user)
    assert 'User' in repr(user)

    user2 = User(111, 'some', '', '', None, '', '', None,
                 None, None, None)
    user2.update_from_dict(user_data)
    assert user2.login == 'octocat'
    assert user2.location == 'San Francisco'


def test_org(session, github_data_loader):
    org_data = github_data_loader('org')
    org = Organization.create_from_dict(org_data)

    session.add(org)
    session.commit()

    assert org.id > 0
    assert session.query(Organization).first() == org
    assert str(org.id) in repr(org)
    assert 'Organization' in repr(org)


def test_org_repo(session, github_data_loader):
    repo_data = github_data_loader('repo')
    org = session.query(Organization).first()
    assert len(org.repositories) == 0
    repo = Repository.create_from_dict(repo_data, org)
    assert len(org.repositories) == 1

    session.add(repo)
    session.commit()

    assert repo.id > 0
    assert repo.owner.id == org.id
    assert session.query(Repository).first() == repo
    session.delete(repo)
    session.commit()
    assert len(org.repositories) == 0


def test_user_repo(session, github_data_loader):
    repo_data = github_data_loader('repo')
    user = session.query(User).first()
    assert len(user.repositories) == 0
    repo = Repository.create_from_dict(repo_data, user)
    assert len(user.repositories) == 1

    session.add(repo)
    session.commit()

    assert repo.id > 0
    assert repo.owner.id == user.id
    assert session.query(Repository).first() == repo


def test_repo(github_data_loader):
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    repo.id = 10
    assert '10' in repr(repo)
    assert 'Repository' in repr(repo)
    assert Repository.make_full_name('some', 'repo') == repo.full_name

    assert repo.is_private
    repo.visibility_type = Repository.VISIBILITY_PUBLIC
    assert repo.is_public
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert repo.is_hidden
    repo.generate_secret()
    secret1 = repo.secret

    repo_data = github_data_loader('repo')
    repo.update_from_dict(repo_data)
    assert repo.full_name == 'octocat/Hello-World'
    assert repo.owner_login == 'octocat'
    repo.generate_secret()
    secret2 = repo.secret
    assert secret1 != secret2


def test_repo_release(session, github_data_loader):
    release_data = github_data_loader('release')
    sender_data = github_data_loader('sender')
    repo = session.query(Repository).first()
    assert len(repo.releases) == 0
    release = Release.create_from_dict(release_data, sender_data, repo)
    assert len(repo.releases) == 1

    session.add(release)
    session.commit()

    assert release.id > 0
    assert release.repository.id == repo.id
    assert session.query(Release).first() == release
    assert str(release.id) in repr(release)
    assert 'Release' in repr(release)


def test_repo_push(session, github_data_loader):
    push_data = github_data_loader('push')
    sender_data = github_data_loader('sender')
    repo = session.query(Repository).first()
    assert len(repo.pushes) == 0
    push = Push.create_from_dict(push_data, sender_data, repo)
    assert len(repo.pushes) == 1

    session.add(push)
    session.commit()

    assert push.id > 0
    assert push.repository.id == repo.id
    assert len(push.commits) == 1
    assert session.query(Push).first() == push
    assert str(push.id) in repr(push)
    assert 'Push' in repr(push)
    assert str(push.commits[0].id) in repr(push.commits[0])
    assert 'Commit' in repr(push.commits[0])
    before = datetime.datetime.now()
    repo.events_updated()
    act = datetime.datetime.now()
    delta = act - before
    assert (datetime.datetime.now() - repo.last_event) < delta


def test_role_mixin():
    roleA = Role('admin', 'Admin of this great app')
    roleB = Role('admin', 'Administrator of the app')
    roleC = Role('admininistrator', 'Admin of this great app')
    assert roleA == roleB
    assert roleB == roleA
    assert hash(roleA) == hash(roleB)
    assert roleA != roleC
    assert hash(roleA) != hash(roleC)
    assert roleB != roleC
    assert hash(roleB) != hash(roleC)
    roleA.id = 10
    assert '10' in repr(roleA)
    assert 'Role' in repr(roleA)


def test_anonymous():
    anonym = Anonymous()
    assert not anonym.has_role('admin')
    assert not anonym.has_role('user')
    assert not anonym.is_active
    assert not anonym.is_authenticated
    assert anonym.rolenames == []
    assert anonym.is_anonymous
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    assert not anonym.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert not anonym.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_PUBLIC
    assert anonym.sees_repo(repo)
    assert not anonym.owns_repo(repo)


def test_user_mixin():
    account = UserAccount()
    account.active = True
    assert account.is_active
    assert not account.has_role('admin')
    assert not account.has_role('user')

    assert account.login == '<unknown>'
    someone_user = User(711, 'someone', '', '', None, '', '', None,
                        None, None, account)
    assert account.login == 'someone'

    some_user = User(111, 'some', '', '', None, '', '', None,
                     None, None, None)
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, some_user, Repository.VISIBILITY_PRIVATE)
    assert not account.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert not account.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_PUBLIC
    assert account.sees_repo(repo)

    role = Role('admin', '')
    account.roles.append(role)
    assert account.has_role('admin')
    assert account.rolenames == ['admin']
    repo.visibility_type = Repository.VISIBILITY_PRIVATE
    assert account.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert account.sees_repo(repo)
    account.roles.remove(role)
    assert not account.has_role('admin')

    repo.owner = someone_user
    assert account.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_PRIVATE
    assert account.sees_repo(repo)
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert account.sees_repo(repo)
