import flask
import jinja2


def repo_visibility(repo):
    """Convert repo to its visibility attribute as string

    :param repo: Repository to show its visibility as string
    :type repo: ``repocribro.models.Repository``
    :return: Text representation of repo visibility
    :rtype: str
    """
    if repo.is_public:
        return 'Public'
    if repo.is_hidden:
        return 'Hidden'
    if repo.is_private:
        return 'Private'


def repo_link(repo, show_secret=False):
    """Convert repo to link to the detail page of that repo

    :param repo: Repository to show its link
    :type repo: ``repocribro.models.Repository``
    :param show_secret: If secret links should be returned
    :type show_secret: bool
    :return: HTML code with link to repository detail page
    :rtype: ``jinja2.Markup``
    """
    url = None
    if repo.is_public:
        url = flask.url_for('core.repo_detail',
                            login=repo.owner_login, reponame=repo.name)
    elif repo.is_hidden and show_secret:
        url = flask.url_for('core.repo_detail_hidden', secret=repo.secret)
    elif repo.is_private and show_secret:
        url = flask.url_for('core.repo_detail',
                            login=repo.owner_login, reponame=repo.name)
    if url is None:
        return 'Top secret'
    return jinja2.Markup('<a href="{0}">{0}</a>'.format(url))


def gh_user_link(user):
    """Convert user/org to its GitHub URL

    :param repo: User to show its GitHub URL
    :type repo: ``repocribro.models.RepositoryOwner``
    :return: HTML code with hyperlink to GitHub user/org page
    :rtype: ``jinja2.Markup``
    """
    return jinja2.Markup(
        '<a href="https://github.com/{0}" target="_blank">{0}</a>'.format(
            user.login
        )
    )


def gh_push_url(push):
    """Convert push to compare GitHub URL

    :param push: Push to be converted
    :type push: ``repocribro.models.Push``
    :return: URL to GitHub compare page
    :rtype: str
    """
    before = push.before[:10]
    after = push.after[:10]
    return 'https://github.com/{0}/compare/{1}...{2}'.format(
        push.repository.full_name, before, after
    )


def gh_repo_link(repo):
    """Convert repo to its GitHub URL

    :param repo: Repository to show its GitHub URL
    :type repo: ``repocribro.models.Repository``
    :return: HTML code with hyperlink to GitHub repo page
    :rtype: ``jinja2.Markup``
    """
    return jinja2.Markup(
        '<a href="https://github.com/{0}" target="_blank">{0}</a>'.format(
            repo.full_name
        )
    )


def gh_repo_visibility(repo):
    """Convert repo to its GitHub visibility attribute as string

    :param repo: Repository to show its GitHub visibility as string
    :type repo: ``repocribro.models.Repository``
    :return: Text representation of repo GitHub visibility
    :rtype: str
    """
    return 'Private' if repo.private else 'Public'


#: Container with all model filters with their names in views
model_filters = {
    'repo_visibility': repo_visibility,
    'repo_link': repo_link,
    'gh_user_link': gh_user_link,
    'gh_repo_link': gh_repo_link,
    'gh_push_url': gh_push_url,
    'gh_repo_visibility': gh_repo_visibility
}
