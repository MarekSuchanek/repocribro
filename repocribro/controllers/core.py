import flask
import flask_login
import flask_sqlalchemy
import injector

from ..extending import ExtensionsMaster
from ..models import User, Organization, Repository

core = flask.Blueprint('core', __name__, url_prefix='')


@core.route('/')
def index():
    return flask.render_template('core/index.html')


@core.route('/search/')
@core.route('/search')
@core.route('/search/<query>')
@injector.inject(ext_master=ExtensionsMaster)
def search(ext_master, query=''):
    # TODO: more attrs, limits & pages
    tabs = {}
    active_tab = ''
    if query != '':
        ext_master.call('view_core_search_tabs',
                        query=query, tabs_dict=tabs)
        tabs = sorted(tabs.values())
        active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/search.html', query=query, tabs=tabs, active_tab=active_tab
    )


@core.route('/user/<login>')
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 ext_master=ExtensionsMaster)
def user_detail(db, ext_master, login):
    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        is_org = db.session.query(Organization).filter(
            Organization.login == login
        ).exists()
        if is_org:
            # TODO: implement 410 (user deleted/archived)
            # TODO: user renaming
            flask.abort(404)
        flask.flash('Oy! You wanted to access user, but it\'s an organization.'
                    'We redirected you but be careful next time!', 'notice')
        return flask.redirect(flask.url_for('core.org', login=login))

    tabs = {}
    ext_master.call('view_core_user_detail_tabs',
                    user=user, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/user.html', user=user, tabs=tabs, active_tab=active_tab
    )


@core.route('/org/<login>')
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 ext_master=ExtensionsMaster)
def org_detail(db, ext_master, login):
    org = db.session.query(User).filter_by(login=login).first()
    if org is None:
        is_user = db.session.query(User).filter_by(login=login).exists()
        if is_user:
            # TODO: implement 410 (org deleted/archived)
            # TODO: org renaming
            flask.abort(404)
        flask.flash('Oy! You wanted to access organization, but it\'s  auser.'
                    'We redirected you but be careful next time!', 'notice')

    tabs = {}
    ext_master.call('view_core_org_detail_tabs',
                    org=org, tabs_dict=tabs)
    tabs = sorted(tabs.values())
    active_tab = flask.request.args.get('tab', tabs[0].id)

    return flask.render_template(
        'core/org.html', org=org, tabs=tabs, active_tab=active_tab
    )


@core.route('/repo/<login>')
def repo_redir(login):
    flask.flash('Seriously?! You forget to specify repository name, didn\'t '
                'you? We redirected you but be careful next time!', 'notice')
    print('WTF')
    return flask.redirect(flask.url_for('core.user_detail', login=login))


def repo_detail_common(db, ext_master, repo):
    if repo is None:
        # TODO: implement 410 (repo deleted/archived)
        # TODO: repository renaming
        flask.abort(404)
    if not flask_login.current_user.sees_repo(repo):
        # TODO: 404 or 410 (if were public in the past)?
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
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 ext_master=ExtensionsMaster)
def repo_detail(db, ext_master, login, reponame):
    repo = db.session.query(Repository).filter_by(
        full_name='{}/{}'.format(login, reponame),
    ).first()
    return repo_detail_common(db, ext_master, repo)


@core.route('/hidden-repo/<secret>')
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 ext_master=ExtensionsMaster)
def repo_detail_hidden(db, ext_master, secret):
    repo = db.session.query(Repository).filter_by(secret=secret).first()
    return repo_detail_common(db, ext_master, repo)
