import datetime
import jinja2
import pytest

from repocribro.filters.common import *
from repocribro.filters.models import *
from repocribro.models import Repository, User, Organization, Push


def test_yes_no():
    assert yes_no(True) == 'Yes'
    assert yes_no(False) == 'No'
    assert yes_no(None) == 'No'


def test_email_link():
    result = email_link('test@testing.com')
    assert 'test@testing.com' in result
    assert 'href="mailto:test@testing.com"' in result
    assert isinstance(result, jinja2.Markup)
    assert email_link(None) == ''


def test_ext_link():
    result = ext_link('https://github.com')
    assert 'https://github.com' in result
    assert 'href="https://github.com"' in result
    assert 'target="_blank"' in result
    assert isinstance(result, jinja2.Markup)
    assert ext_link(None) == ''


# @see http://getbootstrap.com/components/#alerts
@pytest.mark.parametrize(
    ['category', 'css_class'],
    [
        ('error', 'danger'),
        ('warning', 'warning'),
        ('info', 'info'),
        ('success', 'success'),
    ]
)
def test_flash_class(category, css_class):
    assert flash_class(category) == css_class


def test_repo_visibility():
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    assert repo_visibility(repo) == 'Private'
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    assert repo_visibility(repo) == 'Hidden'
    repo.visibility_type = Repository.VISIBILITY_PUBLIC
    assert repo_visibility(repo) == 'Public'


def test_repo_link():
    repo = Repository(777, None, 'some/project', 'project', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PUBLIC)
    result = repo_link(repo, False)
    assert 'a href="' in result
    assert isinstance(result, jinja2.Markup)
    result = repo_link(repo, True)
    assert 'a href="' in result
    assert isinstance(result, jinja2.Markup)
    repo.visibility_type = Repository.VISIBILITY_HIDDEN
    repo.generate_secret()
    result = repo_link(repo, False)
    assert 'a href="' not in result
    result = repo_link(repo, True)
    assert 'a href="' in result
    assert repo.secret in result
    assert repo.name not in result
    assert repo.owner_login not in result
    assert isinstance(result, jinja2.Markup)
    repo.visibility_type = Repository.VISIBILITY_PRIVATE
    result = repo_link(repo, False)
    assert 'a href="' not in result
    result = repo_link(repo, True)
    assert 'a href="' in result
    assert isinstance(result, jinja2.Markup)


def test_gh_user_link():
    user = User(111, 'some', '', '', None, '', '', None, None, None, None)
    result = gh_user_link(user)
    assert user.login in result
    assert 'https://github.com' in result
    assert isinstance(result, jinja2.Markup)
    org = Organization(111, 'some', '', '', None, '', '', None, None)
    result = gh_user_link(org)
    assert org.login in result
    assert 'https://github.com' in result
    assert isinstance(result, jinja2.Markup)


def test_gh_repo_link():
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    result = gh_repo_link(repo)
    assert repo.full_name in result
    assert 'https://github.com' in result
    assert isinstance(result, jinja2.Markup)


def test_gh_push_url():
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    push = Push(484, 'refs/heads/changes', 'abc', 'def', 1, 1,
                datetime.datetime.now(), 'sender_login', 'sender_id', repo)
    result = gh_push_url(push)
    assert push.repository.full_name in result
    assert 'https://github.com' in result
    assert 'compare' in result


def test_gh_repo_visibility():
    repo = Repository(777, None, 'some/repo', 'repo', 'C++', '', '',
                      False, None, None, Repository.VISIBILITY_PRIVATE)
    assert gh_repo_visibility(repo) == 'Public'
    repo.private = True
    assert gh_repo_visibility(repo) == 'Private'
