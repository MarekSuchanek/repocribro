import flask
import requests
import json

user = flask.Blueprint('user', __name__, url_prefix='/user')

GITHUB_API = 'https://api.github.com'


@user.route('/dashboard')
def dashboard():
    # TODO: require logged user (decorator?)
    response = requests.get(
        GITHUB_API + '/user',
        params={'access_token': flask.session['github_token']}
    )
    return flask.render_template(
        'user/dashboard.html',
        token=flask.session['github_token'],
        scopes=flask.session['github_scope'],
        user_json=json.dumps(
            response.json(),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )


@user.route('/repos')
def repositories():
    # TODO: require logged user (decorator?)
    response = requests.get(
        GITHUB_API + '/user/repos',
        params={
            'access_token': flask.session['github_token']
        }
    )
    return flask.render_template(
        'user/repos.html',
        repos_json=json.dumps(
            response.json(),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )


@user.route('/orgs')
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