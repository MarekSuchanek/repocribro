import flask
import flask_login
import requests
import json
from ..models import Repository

user = flask.Blueprint('user', __name__, url_prefix='/user')

GITHUB_API = 'https://api.github.com'


@user.route('')
@flask_login.login_required
def dashboard():
    response = requests.get(
        GITHUB_API + '/user',
        params={'access_token': flask.session['github_token']}
    )
    return flask.render_template(
        'user/dashboard.html',
        token=flask.session['github_token'],
        scopes=flask.session['github_scope'],
        user=flask_login.current_user,
        user_json=json.dumps(
            response.json(),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )


@user.route('/profile/update')
def update_profile():
    # TODO: update profile from github
    return flask.redirect(flask.url_for('dashboard'))


@user.route('/repos')
@flask_login.login_required
def repositories():
    response = requests.get(
        GITHUB_API + '/user/repos',
        params={
            'access_token': flask.session['github_token']
        }
    )
    user = flask_login.current_user.github_user
    return flask.render_template(
        'user/repos.html',
        repos=[Repository.create_from_dict(d, user) for d in response.json()]
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
    # TODO: require logged user (decorator?)
    response = requests.get(
        GITHUB_API + '/user/orgs',
        params={'access_token': flask.session['github_token']}
    )
    return flask.render_template(
        'user/orgs.html',
        retval=response.status_code,
        orgs_json=json.dumps(
            response.json(),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )