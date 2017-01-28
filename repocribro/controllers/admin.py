import flask
from ..security import permissions
from ..helpers import ViewTab, Badge
from ..models import UserAccount, Role, Repository


admin = flask.Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('')
@permissions.admin_role.require(404)
def index():
    accounts = UserAccount.query.all()
    roles = Role.query.all()
    repos = Repository.query.all()
    exts = []  # TODO: gather extensions

    tabs = [
        ViewTab(
            'users', 'Users', 0,
            flask.render_template('admin/tabs/users.html', accounts=accounts),
            octicon='person', badge=Badge(len(accounts))
        ),
        ViewTab(
            'roles', 'Roles', 0,
            flask.render_template('admin/tabs/roles.html', roles=roles),
            octicon='briefcase', badge=Badge(len(roles))
        ),
        ViewTab(
            'repos', 'Repositories', 0,
            flask.render_template('admin/tabs/repos.html', repos=repos),
            octicon='repo', badge=Badge(len(repos))
        ),
        ViewTab(
            'exts', 'Extensions', 0,
            flask.render_template('admin/tabs/exts.html', exts=exts),
            octicon='code', badge=Badge(len(exts))
        ),
    ]

    return flask.render_template('admin/index.html',
                                 tabs=tabs, active_tab='users')


@admin.route('/account/<uid>')
@permissions.admin_role.require(404)
def account_detail(uid):
    flask.abort(501)


@admin.route('/repository/<uid>')
@permissions.admin_role.require(404)
def repo_detail(uid):
    flask.abort(501)


@admin.route('/role/<uid>')
@permissions.admin_role.require(404)
def role_detail(uid):
    flask.abort(501)
