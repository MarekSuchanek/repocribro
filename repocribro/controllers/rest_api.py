import flask

from ..models import User, Repository, Release, \
                     Organization, Push, Commit


#: REST API controller blueprint
rest_api = flask.Blueprint('api', __name__, url_prefix='/api')

#: DEFAULT PAGE SIZE
PAGE_SIZE = 20


@rest_api.route('/search/<query>')
def search(query):
    """Search searchable objects by query"""
    flask.abort(501)
    return flask.jsonify({})


@rest_api.route('/user/<login>')
def get_user(login):
    """GET User by login"""
    db = flask.current_app.container.get('db')
    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        flask.abort(404)
    return flask.jsonify(user.to_dict())


@rest_api.route('/org/<login>')
def get_org(login):
    """GET Organization by login"""
    db = flask.current_app.container.get('db')
    org = db.session.query(Organization).filter_by(login=login).first()
    if org is None:
        flask.abort(404)
    return flask.jsonify(org.to_dict())


@rest_api.route('/repo/<int:repo_id>')
def get_repo(repo_id):
    """GET Repository (public) by ID"""
    db = flask.current_app.container.get('db')
    repo = db.session.query(Repository).get(repo_id)
    if repo is None or not repo.is_public:
        flask.abort(404)
    return flask.jsonify(repo.to_dict())


@rest_api.route('/repo/<login>/<reponame>')
def get_repo_by_name(login, reponame):
    """GET Repository (public) by owner login and repo name"""
    db = flask.current_app.container.get('db')
    repo = db.session.query(Repository).filter_by(
        fullname=Repository.make_full_name(login, reponame)
    ).first()
    if repo is None or not repo.is_public:
        flask.abort(404)
    return flask.jsonify(repo.to_dict())


@rest_api.route('/push/<int:push_id>')
def get_push(push_id):
    """GET Push (of public repo) by ID"""
    db = flask.current_app.container.get('db')
    push = db.session.query(Push).get(push_id)
    if push is None or not push.repository.is_public:
        flask.abort(404)
    return flask.jsonify(push.to_dict())


@rest_api.route('/commit/<int:commit_id>')
def get_commit(commit_id):
    """GET Commit (of public repo) by ID"""
    db = flask.current_app.container.get('db')
    commit = db.session.query(Commit).get(commit_id)
    if commit is None or not commit.push.repository.is_public:
        flask.abort(404)
    return flask.jsonify(commit.to_dict())


@rest_api.route('/release/<int:release_id>')
def get_release(release_id):
    """GET Release (of public repo) by ID"""
    db = flask.current_app.container.get('db')
    release = db.session.query(Release).get(release_id)
    if release is None or not release.repository.is_public:
        flask.abort(404)
    return flask.jsonify(release.to_dict())
