import flask
import flask_login

from ..models import Repository, Organization

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


def get_repo_if_admin(db, full_name):
    """Retrieve repository from db and return if
     current user is admin (owner or member)

    :param db: database connection where are repos stored
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :param full_name: full name of desired repository
    :type full_name: str
    :return: repository if found, None otherwise
    :rtype: ``repocribro.models.Repository`` or None
    """
    user = flask_login.current_user.github_user
    repo = db.session.query(Repository).filter_by(
        full_name=full_name
    ).first()
    if repo is None:
        return None
    if repo.owner == user or user in repo.members:
        return repo
    return None


@manage.route('/repository/<path:full_name>')
@flask_login.login_required
def repository_detail(full_name):
    """Repository detail (GET handler)"""
    db = flask.current_app.container.get('db')
    repo = get_repo_if_admin(db, full_name)
    if repo is None:
        flask.abort(404)

    return flask.render_template(
        'manage/repo.html', repo=repo, Repository=Repository
    )


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
    return webhook.is_ok


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

    gh_repo = gh_api.get('/repos/' + full_name)
    if not gh_repo.is_ok:
        flask.flash('Repository not found at GitHub', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))
    if not gh_repo.data['permissions']['admin']:
        flask.flash('You are not admin of that repository', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    user = flask_login.current_user.github_user
    repo = db.session.query(Repository).filter_by(
        full_name=full_name
    ).first()
    is_personal_repo = gh_repo.data['owner']['id'] == user.github_id

    if repo is None:
        if is_personal_repo:
            repo = Repository.create_from_dict(gh_repo.data, user)
        else:
            org_login = gh_repo.data['owner']['login']
            org = db.session.query(Organization).filter_by(
                login=org_login
            ).first()
            if org is None:
                gh_org = gh_api.get('/orgs/'+org_login)
                org = Organization.create_from_dict(gh_org.data)
            repo = Repository.create_from_dict(gh_repo.data, org)
            repo.members.append(user)
            db.session.add(org)
        db.session.add(repo)
    else:
        if not is_personal_repo and user not in repo.members:
            repo.members.append(user)

        gh_repo_langs = gh_api.get('/repos/' + full_name + '/languages')
        repo.update_from_dict(gh_repo.data)
        if not gh_repo_langs.is_ok:
            repo.update_languages(gh_repo_langs.data)

    if not update_webhook(gh_api, repo):
        flask.flash('We were unable to create webhook for that repository. '
                    'There is maybe some old one, please remove it and try '
                    'this procedure again.',
                    'warning')
    repo.visibility_type = visibility_type
    if repo.is_hidden:
        repo.generate_secret()
    db.session.commit()

    return flask.redirect(
        flask.url_for('manage.repository_detail', full_name=repo.full_name)
    )


@manage.route('/repository/deactivate', methods=['POST'])
@flask_login.login_required
def repository_deactivate():
    """Deactivate repo in app from GitHub (POST handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    repo = get_repo_if_admin(db, full_name)
    if repo is None:
        flask.abort(404)

    if repo.webhook_id is not None:
        if gh_api.webhook_delete(repo.full_name, repo.webhook_id):
            flask.flash('Webhook has been deactivated',
                        'success')
        else:
            flask.flash('GitHub couldn\'t delete the webhook. Please do it '
                        'manually within GitHub web application.',
                        'warning')
        repo.webhook_id = None
        db.session.commit()
    else:
        flask.flash('There is no registered the webhook within app', 'info')

    return flask.redirect(
        flask.url_for('manage.repository_detail', full_name=repo.full_name)
    )


@manage.route('/repository/delete', methods=['POST'])
@flask_login.login_required
def repository_delete():
    """Delete repo (in app) from GitHub (POST handler)

    .. todo:: consider deleting org repository if there are more members
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    repo = get_repo_if_admin(db, full_name)
    if repo is None:
        flask.abort(404)

    if repo.webhook_id is not None:
        if gh_api.webhook_delete(repo.full_name, repo.webhook_id):
            flask.flash('Webhook has been deactivated',
                        'success')
        else:
            flask.flash('GitHub couldn\'t delete the webhook. Please do it '
                        'manually within GitHub web application.',
                        'warning')
        repo.webhook_id = None
        db.session.commit()

    db.session.delete(repo)
    db.session.commit()
    flask.flash('Repository {} has been deleted within app.'.format(full_name),
                'success')

    return flask.redirect(flask.url_for('manage.repositories'))


@manage.route('/repository/update', methods=['POST'])
@flask_login.login_required
def repository_update():
    """Update repo info from GitHub (POST handler)

    .. todo:: protect from updating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    full_name = flask.request.form.get('full_name')
    repo = get_repo_if_admin(db, full_name)
    if repo is None:
        flask.abort(404)

    gh_repo = gh_api.get('/repos/' + full_name)
    gh_repo_langs = gh_api.get('/repos/' + full_name + '/languages')
    if gh_repo.is_ok and gh_repo_langs.is_ok:
        repo.update_from_dict(gh_repo.data)
        repo.update_languages(gh_repo_langs.data)
        db.session.commit()
    else:
        flask.flash('GitHub doesn\'t know about this repository. '
                    'Try it later or remove repository from app.',
                    'error')

    return flask.redirect(
        flask.url_for('manage.repository_detail', full_name=repo.full_name)
    )


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
    """Update organization

    .. :todo: update org profile
    """
    ORG_REPOS_URL = '/orgs/{}/repos?type=member'
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )
    db = flask.current_app.container.get('db')
    org = db.session.query(Organization).filter_by(login=login).first()
    if org is None:
        flask.abort(404)

    gh_repos = gh_api.get(ORG_REPOS_URL.format(login))
    if gh_repos.is_ok and len(gh_repos.data) > 0:
        gh_org = gh_api.get('/orgs/'+login)
        if gh_org.is_ok:
            org.update_from_dict(gh_org.data)
            db.session.commit()
        else:
            flask.flash('GitHub doesn\'t know about this organization.',
                        'error')
    else:
        flask.flash('You cannot update organizations where you are not '
                    'a member of single repository.',
                    'error')

    return flask.redirect(
        flask.url_for('manage.organizations')
    )


@manage.route('/organization/<login>/delete')
@flask_login.login_required
def organization_delete(login):
    """Delete organization (if no repositories)

    .. :todo: delete org profile
    """
    return flask.abort(501)
