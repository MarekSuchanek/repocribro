import flask
import flask_login
import json

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
def update_profile():
    """Update user info from GitHub (GET handler)

    :todo: protect from updating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    user_data = gh_api.get_data('/user')
    gh_user = flask_login.current_user.github_user
    gh_user.update_from_dict(user_data)
    db.session.commit()
    return flask.redirect(flask.url_for('manage.dashboard', tab='profile'))


@manage.route('/repos')
@flask_login.login_required
def repositories():
    """List user repositories from GitHub (GET handler)"""
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    repos_data = gh_api.get_data('/user/repos')
    user = flask_login.current_user.github_user
    active_ids = [repo.github_id for repo in user.repositories]
    return flask.render_template(
        'manage/repos.html', repos=repos_data,
        Repository=Repository, active_ids=active_ids
    )


def has_good_webhook(gh_api, repo):
    """Check webhook at GitHub for repo

    :param gh_api: GitHub API client for communication
    :type gh_api: ``repocribro.github.GitHubAPI``
    :param repo: Repository which webhook should be checked
    :type repo: ``repocribro.models.Repository``
    :return: If webhook is already in good shape
    :rtype: bool

    :todo: move somewhere else, check registered events
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

    :todo: move somewhere else
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


@manage.route('/repo/<reponame>')
@flask_login.login_required
def repo_detail(reponame):
    """Repository detail (GET handler)"""
    db = flask.current_app.container.get('db')

    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)
    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    return flask.render_template('manage/repo.html',
                                 repo=repo, user=user, Repository=Repository)


@manage.route('/repo/<reponame>/update')
@flask_login.login_required
def repo_update(reponame):
    """Update repo info from GitHub (GET handler)

    :todo: protect from updating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)
    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    repo_data = gh_api.get_data('/repos/' + full_name)
    repo.update_from_dict(repo_data)
    db.session.commit()
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repo/<reponame>/activate', methods=['POST'])
@flask_login.login_required
def repo_activate(reponame):
    """Activate repo in app from GitHub (POST handler)

    :todo: protect from activating too often
    """
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    visibility_type = flask.request.form.get('enable', type=int)
    if visibility_type not in (
        Repository.VISIBILITY_HIDDEN,
        Repository.VISIBILITY_PRIVATE,
        Repository.VISIBILITY_PUBLIC
    ):
        flask.flash('You\'ve requested something weird...', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = db.session.query(Repository).filter_by(full_name=full_name).first()

    response = gh_api.get('/repos/' + full_name)
    if response.status_code != 200:
        flask.flash('GitHub didn\'t give us data about that repository',
                    'error')
        return flask.redirect(flask.url_for('manage.repositories'))
    gh_repo = response.json()

    if repo is None:
        repo = Repository.create_from_dict(gh_repo, user)
        db.session.add(repo)
    else:
        repo.update_from_dict(gh_repo)
    if not update_webhook(gh_api, repo):
        flask.flash('We were unable to create webhook for that repository',
                    'warning')
    repo.visibility_type = visibility_type
    if repo.is_hidden:
        repo.generate_secret()
    db.session.commit()
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repo/<reponame>/deactivate', methods=['POST'])
@flask_login.login_required
def repo_deactivate(reponame):
    """Deactivate repo in app from GitHub (POST handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    if repo.webhook_id is not None:
        if gh_api.webhook_delete(repo.full_name, repo.webhook_id):
            flask.flash('Webhook was deactivated', 'success')
        else:
            flask.flash('GitHub couldn\'t delete the webhook', 'warning')
        repo.webhook_id = None
        db.session.commit()
    else:
        flask.flash('There is no registered the webhook', 'info')
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repos/delete', methods=['POST'])
@flask_login.login_required
def repo_delete():
    """Delete repo (in app) from GitHub (POST handler)"""
    db = flask.current_app.container.get('db')
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    reponame = flask.request.form.get('reponame')
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    if repo.webhook_id is not None:
        gh_api.webhook_delete(repo.full_name, repo.webhook_id)
    db.session.delete(repo)
    db.session.commit()
    flask.flash('Repository {} has been deleted within app.'.format(full_name),
                'success')
    return flask.redirect(flask.url_for('manage.repositories'))


@manage.route('/orgs')
@flask_login.login_required
def organizations():
    """List user organizations from GitHub (GET handler)"""
    flask.abort(501)
    gh_api = flask.current_app.container.get(
        'gh_api', token=flask.session['github_token']
    )

    orgs_data = gh_api.get_data('/user/orgs')
    return flask.render_template(
        'manage/orgs.html',
        orgs_json=json.dumps(
            orgs_data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )
