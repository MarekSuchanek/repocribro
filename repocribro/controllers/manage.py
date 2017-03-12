import flask
import flask_login

from ..models import Repository

#: Manage controller blueprint
manage = flask.Blueprint('manage', __name__, url_prefix='/manage')


@manage.route('')
@flask_login.login_required
def dashboard():
    """Management zone dashboard (GET handler)"""
    ext_master = flask.current_app.container.get('ext_master')

    tabs = {}
    ext_master.call('view_manage_dashboard_tabs', tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'manage/dashboard.html', tabs=tabs, active_tab=active_tab
    )


@manage.route('/profile/update')
@flask_login.login_required
def profile_update():
    """Update user info from GitHub (GET handler)

    .. todo:: protect from updating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    user_data = gh_api.get('/user').data
    gh_user = flask_login.current_user.github_user
    gh_user.update_from_dict(user_data)
    db.session.commit()
    return flask.redirect(flask.url_for('manage.dashboard', tab='profile'))


@manage.route('/repositories')
@flask_login.login_required
def repositories():
    """List user repositories from GitHub (GET handler)"""
    page = int(flask.request.args.get('page', 0))
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    gh_repos = gh_api.get('/user/repos', page=page)
    user = flask_login.current_user.github_user
    active_ids = [repo.github_id for repo in user.repositories]
    return flask.render_template(
        'manage/repos.html', repos=gh_repos.data,
        actual_page=gh_repos.actual_page, total_pages=gh_repos.total_pages,
        Repository=Repository, active_ids=active_ids
    )


@manage.route('/repository/<path:full_name>')
@flask_login.login_required
def repository_detail(full_name):
    """Repository detail (GET handler)"""
    db = flask.current_app.container.get('db')

    # TODO: check if repo in DB and has permissions

    return flask.abort(501)


def has_good_webhook(gh_api, repo):
    """Check webhook at GitHub for repo

    :param gh_api: GitHub API client for communication
    :type gh_api: ``repocribro.github.GitHubAPI``
    :param repo: Repository which webhook should be checked
    :type repo: ``repocribro.models.Repository``
    :return: If webhook is already in good shape
    :rtype: bool

    .. todo:: move somewhere else, check registered events
    """
    if repo.webhook_id is None:
        return False
    webhook = gh_api.webhook_get(repo.full_name, repo.webhook_id)
    return webhook is None


def update_webhook(gh_api, repo):
    """Update webhook at GitHub for repo if needed

    :param gh_api: GitHub API client for communication
    :type gh_api: ``repocribro.github.GitHubAPI``
    :param repo: Repository which webhook should be updated
    :type repo: ``repocribro.models.Repository``
    :return: If webhook is now in good shape
    :rtype: bool

    .. todo:: move somewhere else
    """
    if not has_good_webhook(gh_api, repo):
        repo.webhook_id = None
    if repo.webhook_id is None:
        # Create new webhook
        webhook = gh_api.webhook_create(
            repo.full_name,
            flask.url_for(gh_api.WEBHOOK_CONTROLLER, _external=True)
        )
        if webhook is None:
            return False
        repo.webhook_id = webhook['id']
    return True


@manage.route('/repository/activate', methods=['POST'])
@flask_login.login_required
def repository_activate():
    """Activate repo in app from GitHub (POST handler)

    .. todo:: protect from activating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    visibility_type = flask.request.form.get('enable', type=int)
    if visibility_type not in (
        Repository.VISIBILITY_HIDDEN,
        Repository.VISIBILITY_PRIVATE,
        Repository.VISIBILITY_PUBLIC
    ):
        flask.flash('You\'ve requested something weird...', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    gh_repo = gh_api.get('/repos/'+full_name)
    if not gh_repo.is_ok:
        flask.flash('Repository not found at GitHub', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))
    if not gh_repo['permissions']['admin']:
        flask.flash('You are not admin of that repository', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    # TODO: check if repo in DB, (if orgrepo add member)
    # TODO: add webhook (register or lookup for existing)
    # TODO: add repo to DB

    return flask.jsonify(gh_repo.data)


@manage.route('/repository/deactivate', methods=['POST'])
@flask_login.login_required
def repository_deactivate():
    """Deactivate repo in app from GitHub (POST handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    # TODO: check if repo in DB and user has permissions
    # TODO: remove webhook

    return flask.abort(501)


@manage.route('/repository/delete', methods=['POST'])
@flask_login.login_required
def repository_delete():
    """Delete repo (in app) from GitHub (POST handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    # TODO: check if repo in DB and user has permissions
    # TODO: remove webhook
    # TODO: remove repo from DB

    return flask.abort(501)


@manage.route('/repository/update')
@flask_login.login_required
def repository_update():
    """Update repo info from GitHub (GET handler)

    .. todo:: protect from updating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    # TODO: check if repo in DB and user has permissions
    # TODO: update repo from GH
    # TODO: check if webhook is valid and fix if needed

    return flask.abort(501)


@manage.route('/organizations')
@flask_login.login_required
def organizations():
    """List user organizations from GitHub (GET handler)"""
    page = int(flask.request.args.get('page', 0))
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    gh_orgs = gh_api.get('/user/orgs', page=page)
    orgs_link = gh_api.app_connections_link

    return flask.render_template(
        'manage/orgs.html', orgs=gh_orgs.data,
        actual_page=gh_orgs.actual_page, total_pages=gh_orgs.total_pages,
        orgs_link=orgs_link,

    )


@manage.route('/organization/<login>')
@flask_login.login_required
def organization(login):
    """List organization repositories for activation

    .. :todo: register organization in repocribro
    .. :todo: own profile page of organization
    """
    ORG_REPOS_URL = '/orgs/{}/repos?type=member'
    page = int(flask.request.args.get('page', 0))
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    gh_repos = gh_api.get(ORG_REPOS_URL.format(login), page=page)
    user = flask_login.current_user.github_user
    active_ids = [repo.github_id for repo in user.repositories]
    return flask.render_template(
        'manage/repos.html', repos=gh_repos.data,
        actual_page=gh_repos.actual_page, total_pages=gh_repos.total_pages,
        Repository=Repository, active_ids=active_ids,
        repos_type=login+' (organization)'
    )


@manage.route('/organization/<login>/update')
@flask_login.login_required
def organization_update(login):
    """List organization repositories for activation

    .. :todo: update org profile
    """
    return flask.abort(501)
