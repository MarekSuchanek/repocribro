from repocribro.models import User, UserAccount, Organization, \
    Repository, Release, Push


def test_user_account(session):
    user_account = UserAccount()

    session.add(user_account)
    session.commit()

    assert user_account.id > 0
    assert session.query(UserAccount).first() == user_account


def test_user(session, github_data_loader):
    user_data = github_data_loader('user')
    user_account = session.query(UserAccount).first()
    user = User.create_from_dict(user_data, user_account)

    session.add(user)
    session.commit()

    assert user.id > 0
    assert session.query(User).first() == user


def test_org(session, github_data_loader):
    org_data = github_data_loader('org')
    org = Organization.create_from_dict(org_data)

    session.add(org)
    session.commit()

    assert org.id > 0
    assert session.query(Organization).first() == org


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
