import flask
import flask_login
import json
from ..github import GitHubAPI
from ..models import Repository, db

user = flask.Blueprint('user', __name__, url_prefix='/user')


@user.route('')
@flask_login.login_required
def dashboard():
    tab = flask.request.args.get('tab', default='repos')
    return flask.render_template(
        'user/dashboard.html',
        tab=tab,
        token=GitHubAPI.get_token(),
        scopes=GitHubAPI.get_scope()
    )


@user.route('/profile/update')
def update_profile():
    # TODO: protect from updating too often
    user_data = GitHubAPI.get_data('/user')
    gh_user = flask_login.current_user.github_user
    gh_user.update_from_dict(user_data)
    db.session.commit()
    return flask.redirect(flask.url_for('user.dashboard', tab='profile'))


@user.route('/repos')
@flask_login.login_required
def repositories():
    repos_data = GitHubAPI.get_data('/user/repos')
    user = flask_login.current_user.github_user
    return flask.render_template(
        'user/repos.html',
        repos=[Repository.create_from_dict(d, user) for d in repos_data]
    )


@user.route('/repos/activate', methods=['POST'])
@flask_login.login_required
def repository_activate():
    repo_id = flask.request.form.get('repo_id')
    # TODO retrieve repository
    # TODO check if owner / have access
    # TODO register repository


@user.route('/repos/deactivate', methods=['POST'])
@flask_login.login_required
def repository_deactivate():
    repo_id = flask.request.form.get('repo_id')
    # TODO retrieve repository
    # TODO check if owner / have access
    # TODO unregister repository


@user.route('/orgs')
@flask_login.login_required
def organizations():
    orgs_data = GitHubAPI.get_data('/user/orgs')
    return flask.render_template(
        'user/orgs.html',
        orgs_json=json.dumps(
            orgs_data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )