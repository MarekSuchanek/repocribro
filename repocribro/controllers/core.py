import flask

core = flask.Blueprint('core', __name__, url_prefix='')


@core.route('/')
def index():
    return flask.render_template('core/index.html')


@core.route('/search')
@core.route('/search/<query>')
def search(query=None):
    # TODO: do query in DB and send results to view
    return flask.render_template('core/search.html')


@core.route('/user/<username>')
def user(username):
    # TODO: get user from DB and send to view or redirect if org
    return flask.render_template('core/user.html', username=username)


@core.route('/org/<username>')
def org(username):
    # TODO: get org from DB and send to view or redirect if user
    return flask.render_template('core/org.html', username=username)


@core.route('/repo/<username>')
def repo_redir(username):
    # TODO: if org then redirect to org instead
    return flask.redirect(flask.url_for('user', username=username))


@core.route('/repo/<username>/<reponame>')
def repo(username, reponame):
    # TODO: get user from DB and send to view or redirect if org
    return flask.render_template('core/repo.html',
                                 username=username,
                                 reponame=reponame)
