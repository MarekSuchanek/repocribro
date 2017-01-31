import flask
import flask_sqlalchemy
import injector
import sqlalchemy

from ..extending.helpers import ViewTab, Badge
from ..models import UserAccount, User, Role, Repository
from ..extending import ExtensionsMaster
from ..security import permissions

admin = flask.Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('')
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 ext_master=ExtensionsMaster)
def index(db, ext_master):
    accounts = db.session.query(UserAccount).query.all()
    roles = db.session.query(Role.query).all()
    repos = db.session.query(Repository).query.all()
    exts = ext_master.call('view_admin_extensions', None)

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


@admin.route('/account/<login>')
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def account_detail(db, login):
    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        flask.abort(404)
    return flask.render_template('admin/account.html', user=user)


@admin.route('/account/<login>/ban', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def account_ban(db, login):
    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        flask.abort(404)
    ban = flask.request.form.get('active') == '0'
    unban = flask.request.form.get('active') == '1'
    if user.user_account.active and ban:
        user.user_account.active = False
        db.session.commmit()
        flask.flash('User account {} has been disabled.'.format(login),
                    'success')
    elif not user.user_account.active and unban:
        user.user_account.active = True
        db.session.commmit()
        flask.flash('User account {} has been enabled.'.format(login),
                    'success')
    else:
        flask.flash('Nope, no action has been performed', 'info')
    return flask.redirect(
        flask.url_for('admin.account_detail', login=login)
    )


@admin.route('/account/<login>/delete', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def account_delete(db, login):
    user = db.session.query(User).filter_by(login=login).first()
    if user is None:
        flask.abort(404)
    db.session.delete(user.user_account)
    db.session.commit()
    flask.flash('User account {} with the all related data'
                ' has been deleted'.format(login), 'success')
    return flask.redirect(
        flask.url_for('admin.index', tab='users')
    )


@admin.route('/repository/<login>/<reponame>')
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def repo_detail(db, login, reponame):
    repo = db.session.query(Repository).filter_by(
        full_name=Repository.make_full_name(login, reponame)
    ).first()
    if repo is None:
        flask.abort(404)
    return flask.render_template(
        'admin/repo.html',
        repo=repo, Repository=Repository
    )


@admin.route('/repository/<login>/<reponame>/visibility', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def repo_visibility(db, login, reponame):
    repo = db.session.query(Repository).filter_by(
        full_name=Repository.make_full_name(login, reponame)
    ).first()
    if repo is None:
        flask.abort(404)
    visibility_type = flask.request.form.get('enable', type=int)
    if visibility_type not in (
            Repository.VISIBILITY_HIDDEN,
            Repository.VISIBILITY_PRIVATE,
            Repository.VISIBILITY_PUBLIC
    ):
        flask.flash('You\'ve requested something weird...', 'error')
        return flask.redirect(
            flask.url_for('admin.repo_detail', login=login, reponame=reponame)
        )

    repo.visibility_type = visibility_type
    if repo.visibility_type == Repository.VISIBILITY_HIDDEN:
        repo.generate_secret()
    db.session.commit()
    flask.flash('The visibility of repository {}  has been '
                'updated'.format(repo.full_name), 'success')
    return flask.redirect(
        flask.url_for('admin.repo_detail', login=login, reponame=reponame)
    )


@admin.route('/repository/<login>/<reponame>/delete', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def repo_delete(db, login, reponame):
    repo = db.session.query(Repository).filter_by(
        full_name=Repository.make_full_name(login, reponame)
    ).first()
    if repo is None:
        flask.abort(404)
    db.session.delete(repo)
    db.session.commit()
    flask.flash('Repository {} with the all related data has '
                'been deleted'.format(repo.full_name), 'success')
    return flask.redirect(flask.url_for('admin.index', tab='repos'))


@admin.route('/role/<name>')
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_detail(db, name):
    role = db.session.query(Role).filter_by(name=name).first()
    if role is None:
        flask.abort(404)
    return flask.render_template('admin/role.html', role=role)


@admin.route('/role/<name>/edit', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_edit(db, name):
    role = db.session.query(Role).filter_by(name=name).first()
    if role is None:
        flask.abort(404)
    name = flask.request.form.get('name', '')
    desc = flask.request.form.get('description', None)
    if name == '':
        flask.flash('Couldn\'t make that role...', 'warning')
        return flask.redirect(flask.url_for('admin.index', tab='roles'))
    try:
        role.name = name
        role.description = desc
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        flask.flash('Couldn\'t make that role... {}'.format(str(e)),
                    'warning')
        return flask.redirect(flask.url_for('admin.index', tab='roles'))
    flask.flash('Role {} has been edited'.format(name), 'success')
    return flask.redirect(flask.url_for('admin.role_detail', name=role.name))


@admin.route('/role/<name>/delete', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_delete(db, name):
    role = db.session.query(Role).filter_by(name=name).first()
    if role is None:
        flask.abort(404)
    db.session.delete(role)
    db.session.commit()
    flask.flash('Role {} with the all related data has '
                'been deleted'.format(name), 'success')
    return flask.redirect(flask.url_for('admin.index', tab='roles'))


@admin.route('/roles/create', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_create(db):
    name = flask.request.form.get('name', '')
    desc = flask.request.form.get('description', None)
    if name == '':
        flask.flash('Couldn\'t make that role...', 'warning')
        return flask.redirect(flask.url_for('admin.index', tab='roles'))
    try:
        role = Role(name, desc)
        db.session.add(role)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        flask.flash('Couldn\'t make that role... {}'.format(str(e)),
                    'warning')
        return flask.redirect(flask.url_for('admin.index', tab='roles'))
    return flask.redirect(flask.url_for('admin.role_detail', name=role.name))


@admin.route('/role/<name>/add', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_assignment_add(db, name):
    login = flask.request.form.get('login', '')
    user = db.session.query(User).filter_by(login=login).first()
    role = db.session.query(Role).filter_by(name=name).first()
    if user is None or role is None:
        flask.abort(404)
    account = user.user_account
    if account in role.user_accounts:
        flask.flash('User {} already has role {}'.format(login, name),
                    'error')
    else:
        role.user_accounts.append(account)
        db.session.commit()
        flask.flash('Role {} assigned to user {}'.format(name, login),
                    'success')
    return flask.redirect(flask.url_for('admin.role_detail', name=name))


@admin.route('/role/<name>/remove', methods=['POST'])
@permissions.admin_role.require(404)
@injector.inject(db=flask_sqlalchemy.SQLAlchemy)
def role_assignment_remove(db, name):
    login = flask.request.form.get('login', '')
    user = db.session.query(User).filter_by(login=login).first()
    role = db.session.query(Role).filter_by(name=name).first()
    if user is None or role is None:
        flask.abort(404)
    account = user.user_account
    if account not in role.user_accounts:
        flask.flash('User {} doesn\'t have role {}'.format(login, name),
                    'error')
    else:
        role.user_accounts.remove(account)
        db.session.commit()
        flask.flash('Role {} removed from user {}'.format(name, login),
                    'success')
    return flask.redirect(flask.url_for('admin.role_detail', name=name))
