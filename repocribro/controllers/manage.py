import flask
import flask_login
import json
from ..github import GitHubAPI
from ..models import Repository, db
from ..helpers import ViewTab, Badge

manage = flask.Blueprint('manage', __name__, url_prefix='/manage')


@manage.route('')
@flask_login.login_required
def dashboard():
    repos = flask_login.current_user.github_user.repositories

    tabs = [
        ViewTab(
            'repositories', 'Repositories', 0,
            flask.render_template(
                'manage/dashboard/repos_tab.html',
                repos=repos
            ),
            octicon='repo', badge=Badge(len(repos))
        ),
        ViewTab(
            'profile', 'Profile', 1,
            flask.render_template(
                'manage/dashboard/profile_tab.html',
                user=flask_login.current_user.github_user
            ),
            octicon='person'
        ),
        ViewTab(
            'session', 'Session', 2,
            flask.render_template(
                'manage/dashboard/session_tab.html',
                token=GitHubAPI.get_token(),
                scopes=GitHubAPI.get_scope()
            ),
            octicon='mark-github'
        ),
    ]

    return flask.render_template(
        'manage/dashboard.html',
        tabs=tabs,
        active_tab=flask.request.args.get('tab', 'repositories')
    )


@manage.route('/profile/update')
def update_profile():
    # TODO: protect from updating too often
    user_data = GitHubAPI.get_data('/user')
    gh_user = flask_login.current_user.github_user
    gh_user.update_from_dict(user_data)
    db.session.commit()
    return flask.redirect(flask.url_for('user.dashboard', tab='profile'))


@manage.route('/repos')
@flask_login.login_required
def repositories():
    repos_data = GitHubAPI.get_data('/user/repos')
    user = flask_login.current_user.github_user
    return flask.render_template(
        'manage/repos.html',
        repos=[Repository.create_from_dict(d, user) for d in repos_data],
        Repository=Repository
    )


@manage.route('/repo/<reponame>')
@flask_login.login_required
def repo_detail(reponame):
    flask.abort(501)


def update_webhook(repo):
    if repo.webhook_id is not None:
        # Check if actual webhook is still there
        # TODO: check if there are right events
        webhook = GitHubAPI.webhook_get(repo.full_name, repo.webhook_id)
        if webhook is None:
            repo.webhook_id = None
    if repo.webhook_id is None:
        # Create new webhook
        webhook = GitHubAPI.webhook_create(repo.full_name)
        if webhook is None:
            return False
        repo.webhook_id = webhook['id']
    return True


@manage.route('/repos/activate', methods=['POST'])
@flask_login.login_required
def repo_activate():
    visibility_type = flask.request.form.get('enable', type=int)
    if visibility_type not in (
        Repository.VISIBILITY_HIDDEN,
        Repository.VISIBILITY_PRIVATE,
        Repository.VISIBILITY_PUBLIC
    ):
        flask.flash('You\'ve requested something weird...', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    # TODO: protect from activating too often
    reponame = flask.request.form.get('reponame')
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = Repository.query.filter_by(full_name=full_name).first()

    response = GitHubAPI.get('/repos/' + full_name)
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
    if not update_webhook(repo):
        flask.flash('We were unable to create webhook for that repository',
                    'warning')
    repo.visibility_type = visibility_type
    if repo.visibility_type == Repository.VISIBILITY_HIDDEN:
        repo.generate_secret()
    db.session.commit()
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repos/deactivate', methods=['POST'])
@flask_login.login_required
def repo_deactivate():
    reponame = flask.request.form.get('reponame')
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = Repository.query.filter_by(full_name=full_name).first()
    if repo.webhook_id is not None:
        if GitHubAPI.webhook_delete(repo.full_name, repo.webhook_id):
            flask.flash('Webhook was deactivated', 'success')
            repo.webhook_id = None
            db.session.commit()
        else:
            flask.flash('GitHub couldn\'t delete the webhook', 'warning')
    else:
        flask.flash('There is no registered the webhook', 'info')
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repos/delete', methods=['POST'])
@flask_login.login_required
def repo_delete():
    reponame = flask.request.form.get('reponame')
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = Repository.query.filter_by(full_name=full_name).first()
    if repo.webhook_id is not None:
        GitHubAPI.webhook_delete(repo.full_name, repo.webhook_id)
    db.session.delete(repo)
    db.session.commit()
    flask.flash('Repository {} has been deleted within app.'.format(full_name)
                , 'success')
    return flask.redirect(flask.url_for('manage.repositories'))


@manage.route('/orgs')
@flask_login.login_required
def organizations():
    flask.abort(501)
    orgs_data = GitHubAPI.get_data('/user/orgs')
    return flask.render_template(
        'manage/orgs.html',
        orgs_json=json.dumps(
            orgs_data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )
