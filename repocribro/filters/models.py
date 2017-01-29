import flask
import jinja2


def repo_visibility(repo):
    if repo.is_public:
        return 'Public'
    if repo.is_hidden:
        return 'Hidden'
    if repo.is_private:
        return 'Private'


def repo_link(repo, show_secret=False):
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
    return jinja2.Markup(
        '<a href="https://github.com/{0}" target="_blank">{0}</a>'.format(
            user.login
        )
    )


def gh_repo_link(repo):
    return jinja2.Markup(
        '<a href="https://github.com/{0}" target="_blank">{0}</a>'.format(
            repo.full_name
        )
    )


def gh_repo_visibility(repo):
    return 'Private' if repo.private else 'Public'


model_filters = {
    'repo_visibility': repo_visibility,
    'repo_link': repo_link,
    'gh_user_link': gh_user_link,
    'gh_repo_link': gh_repo_link,
    'gh_repo_visibility': gh_repo_visibility
}
