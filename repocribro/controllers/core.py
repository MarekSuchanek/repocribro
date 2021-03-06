import flask
import flask_login

from ..models import User, Organization, Repository
from ..security import permissions

#: Core controller blueprint
core = flask.Blueprint('core', __name__, url_prefix='')


@core.route('/')
@permissions.actions.browse.require(403)
def index():
    """Landing page (GET handler)"""
    config = flask.current_app.container.get('config')
    text = config.get('repocribro-core', 'landing_text', fallback=None)
    pic = config.get('repocribro-core', 'landing_picture', fallback=None)
    return flask.render_template(
        'core/index.html', landing_text=text, landing_pic=pic
    )


@core.route('/search/')
@core.route('/search')
@core.route('/search/<query>')
@permissions.actions.search.require(403)
def search(query=''):
    """Search page (GET handler)

    .. todo:: more attrs, limits & pages
    """
    ext_master = flask.current_app.container.get('ext_master')

    tabs = {}
    ext_master.call('view_core_search_tabs',
                    query=query, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)
    return flask.render_template(
        'core/search.html', query=query, tabs=tabs, active_tab=active_tab
    )


@core.route('/user/<login>')
@permissions.actions.browse_user.require(403)
def user_detail(login):
    """User detail (GET handler)

    .. todo:: implement 410 (user deleted/archived/renamed)
    """
    db = flask.current_app.container.get('db')
    ext_master = flask.current_app.container.get('ext_master')

    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        org = db.session.query(Organization).filter(
            Organization.login == login
        ).first()
        if org is None:
            flask.abort(404)
        flask.flash('Oy! You wanted to access user, but it\'s an organization.'
                    'We redirected you but be careful next time!', 'notice')
        return flask.redirect(flask.url_for('core.org_detail', login=login))

    tabs = {}
    ext_master.call('view_core_user_detail_tabs',
                    user=user, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/user.html', user=user, tabs=tabs, active_tab=active_tab
    )


@core.route('/org/<login>')
@permissions.actions.browse_org.require(403)
def org_detail(login):
    """Organization detail (GET handler)

    .. todo:: implement 410 (org deleted/archived/renamed)
    """
    db = flask.current_app.container.get('db')
    ext_master = flask.current_app.container.get('ext_master')

    org = db.session.query(Organization).filter_by(login=login).first()
    if org is None:
        user = db.session.query(User).filter_by(login=login).first()
        if user is None:
            flask.abort(404)
        flask.flash('Oy! You wanted to access organization, but it\'s  auser.'
                    'We redirected you but be careful next time!', 'notice')
        return flask.redirect(flask.url_for('core.user_detail', login=login))
    tabs = {}
    ext_master.call('view_core_org_detail_tabs',
                    org=org, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/org.html', org=org, tabs=tabs, active_tab=active_tab
    )


@core.route('/repo/<login>')
@permissions.actions.browse_repo.require(403)
def repo_redir(login):
    flask.flash('Seriously?! You forget to specify repository name, didn\'t '
                'you? We redirected you but be careful next time!', 'notice')
    return flask.redirect(flask.url_for('core.user_detail', login=login))


def repo_detail_common(db, ext_master, repo, has_secret=False):
    """Repo detail (for GET handlers)

    .. todo:: implement 410 (repo deleted/archived/renamed)
    """
    if repo is None:
        flask.abort(404)
    if not flask_login.current_user.sees_repo(repo, has_secret):
        flask.abort(404)

    tabs = {}
    ext_master.call('view_core_repo_detail_tabs',
                    repo=repo, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/repo.html', repo=repo, tabs=tabs, active_tab=active_tab
    )


@core.route('/repo/<login>/<reponame>')
@permissions.actions.browse_repo.require(403)
def repo_detail(login, reponame):
    """Repo detail (GET handler)"""
    db = flask.current_app.container.get('db')
    ext_master = flask.current_app.container.get('ext_master')

    repo = db.session.query(Repository).filter_by(
        full_name='{}/{}'.format(login, reponame),
    ).first()
    return repo_detail_common(db, ext_master, repo)


@core.route('/hidden-repo/<secret>')
@permissions.actions.browse_repo_hidden.require(403)
def repo_detail_hidden(secret):
    """Hidden repo detail (GET handler)"""
    db = flask.current_app.container.get('db')
    ext_master = flask.current_app.container.get('ext_master')

    repo = db.session.query(Repository).filter_by(secret=secret).first()
    return repo_detail_common(db, ext_master, repo, True)
