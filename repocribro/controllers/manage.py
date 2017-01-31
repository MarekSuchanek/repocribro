import flask
import flask_login
import flask_sqlalchemy
import injector
import json

from ..extending.helpers import ViewTab, Badge
from ..github import GitHubAPI
from ..models import Repository

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
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def update_profile(db, gh_api):
    # TODO: protect from updating too often
    user_data = gh_api.get_data('/user')
    gh_user = flask_login.current_user.github_user
    gh_user.update_from_dict(user_data)
    db.session.commit()
    return flask.redirect(flask.url_for('manage.dashboard', tab='profile'))


@manage.route('/repos')
@flask_login.login_required
@injector.inject(gh_api=GitHubAPI)
def repositories(gh_api):
    repos_data = gh_api.get_data('/user/repos')
    user = flask_login.current_user.github_user
    active_ids = [repo.github_id for repo in user.repositories]
    return flask.render_template(
        'manage/repos.html',
        repos=[Repository.create_from_dict(d, user) for d in repos_data],
        Repository=Repository, active_ids=active_ids
    )


def has_good_webhook(gh_api, repo):
    if repo.webhook_id is None:
        return False
    # TODO: check if there are right events
    print(repo.webhook_id)
    webhook = gh_api.webhook_get(repo.full_name, repo.webhook_id)
    print(webhook)
    return webhook is None


def update_webhook(gh_api, repo):
    if not has_good_webhook(gh_api, repo):
        repo.webhook_id = None
    if repo.webhook_id is None:
        # Create new webhook
        webhook = gh_api.webhook_create(repo.full_name)
        if webhook is None:
            return False
        repo.webhook_id = webhook['id']
    return True


@manage.route('/repo/<reponame>')
@flask_login.login_required
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def repo_detail(db, reponame):
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)
    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    return flask.render_template('manage/repo.html',
                                 repo=repo, user=user, Repository=Repository)


@manage.route('/repo/<reponame>/update')
@flask_login.login_required
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def repo_update(db, gh_api, reponame):
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)
    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    repo_data = gh_api.get('/repos/' + full_name)
    repo.update_from_dict(repo_data)
    db.session.commit()
    return flask.redirect(
        flask.url_for('manage.repo_detail', reponame=reponame)
    )


@manage.route('/repo/<reponame>/activate', methods=['POST'])
@flask_login.login_required
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def repo_activate(db, gh_api, reponame):
    visibility_type = flask.request.form.get('enable', type=int)
    if visibility_type not in (
        Repository.VISIBILITY_HIDDEN,
        Repository.VISIBILITY_PRIVATE,
        Repository.VISIBILITY_PUBLIC
    ):
        flask.flash('You\'ve requested something weird...', 'error')
        return flask.redirect(flask.url_for('manage.repositories'))

    # TODO: protect from activating too often
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    # TODO: some bug causing that webhook_id is NONE even when is in DB

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
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def repo_deactivate(db, gh_api, reponame):
    user = flask_login.current_user.github_user
    full_name = Repository.make_full_name(user.login, reponame)

    repo = db.session.query(Repository).filter_by(full_name=full_name).first()
    if repo is None:
        flask.abort(404)
    if repo.webhook_id is not None:
        if gh_api.webhook_delete(repo.full_name, repo.webhook_id):
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
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def repo_delete(db, gh_api):
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
@injector.inject(gh_api=GitHubAPI)
def organizations(gh_api):
    flask.abort(501)
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
