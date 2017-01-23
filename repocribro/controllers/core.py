import flask
from ..models import User, Organization, Repository

core = flask.Blueprint('core', __name__, url_prefix='')


@core.route('/')
def index():
    return flask.render_template('core/index.html')


@core.route('/search')
@core.route('/search/<query>')
def search(query=None):
    # TODO: do query in DB and send results to view
    return flask.render_template('core/search.html')


@core.route('/user/<login>')
def user_detail(login):
    user = User.query.filter_by(login=login).first()
    if user is None:
        is_org = Organization.query.filter(
            Organization.login == login
        ).exists()
        if is_org:
            # TODO: implement 410 (user deleted/archived)
            # TODO: user renaming
            flask.abort(404)
        flask.flash('Oy! You wanted to access user, but it\'s an organization.'
                    'We redirected you but be careful next time!', 'notice')
        return flask.redirect(flask.url_for('core.org', login=login))
    # TODO: gather & prepare tabs & pass to template
    return flask.render_template('core/user.html', user=user)


@core.route('/org/<login>')
def org_detail(login):
    org = Organization.query.filter_by(login=login).first()
    if org is None:
        is_user = User.query.filter_by(login=login).exists()
        if is_user:
            # TODO: implement 410 (org deleted/archived)
            # TODO: org renaming
            flask.abort(404)
        flask.flash('Oy! You wanted to access organization, but it\'s  auser.'
                    'We redirected you but be careful next time!', 'notice')
    # TODO: gather & prepare tabs & pass to template
    return flask.render_template('core/org.html', login=login)


@core.route('/repo/<login>')
def repo_redir(login):
    flask.flash('Seriously?! You forget to specify repository name, didn\'t '
                'you? We redirected you but be careful next time!', 'notice')
    return flask.redirect(flask.url_for('user', login=login))


@core.route('/repo/<login>/<reponame>')
def repo_detail(login, reponame):
    repo = Repository.query.filter_by(
        full_name='{}/{}'.format(login, reponame),
    ).first()
    if not repo.is_public():
        # TODO: 404 or 410 (if were public in the past)?
        flask.abort(404)
    if repo is None:
        # TODO: implement 410 (repo deleted/archived)
        # TODO: repository renaming
        flask.abort(404)
    # TODO: gather & prepare tabs & pass to template
    return flask.render_template('core/repo.html', repo=repo)
