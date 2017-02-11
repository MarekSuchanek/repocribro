import flask
import flask_login
import flask_migrate

from .extending import Extension
from .extending.helpers import ViewTab, Badge
from .models import Push, Release, Repository
from .github import GitHubAPI


def gh_webhook_push(db, repo, data, delivery_id):
    """Process push webhook msg

    :todo: deal with limit of commits in webhook msg (20)
    """
    push = Push.create_from_dict(data['push'], data['sender'], repo)
    db.session.add(push)
    for commit in push.commits:
        db.session.add(commit)


def gh_webhook_release(db, repo, data, delivery_id):
    """Process release webhook msg"""
    release = Release.create_from_dict(data['release'], data['sender'], repo)
    db.session.add(release)


def gh_webhook_repository(db, repo, data, delivery_id):
    """Process repository webhook msg

    This can be one of "created", "deleted", "publicized", or "privatized".

    :todo: find out where is "updated" action
    """
    action = data['action']
    if action == 'privatized':
        repo.private = True
        repo.visibility_type = Repository.VISIBILITY_PRIVATE
    elif action == 'publicized':
        repo.private = False
        repo.visibility_type = Repository.VISIBILITY_PUBLIC
    elif action == 'deleted':
        # TODO: consider some signalization of not being @GitHub anymore
        repo.webhook_id = None
        repo.visibility_type = Repository.VISIBILITY_PRIVATE


# AWESOME EVENTS ARE DIFFERENT THAN WEBHOOK MSGS!!
def gh_event_push(db, repo, payload, actor):
    """Process GitHub PushEvent (with commits)

    https://developer.github.com/v3/activity/events/types/#pushevent

    :param db: Database to store push data
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :param repo: Repository where push belongs to
    :type repo: ``repocribro.models.Repository``
    :param payload: Data about push and commits
    :type payload: dict
    :param actor: Actor doing the event
    :type actor: dict
    """
    push = Push.create_from_dict(payload, actor, repo)
    db.session.add(push)
    for commit in push.commits:
        db.session.add(commit)


def gh_event_release(db, repo, payload, actor):
    """Process GitHub ReleaseEvent (with commits)

    https://developer.github.com/v3/activity/events/types/#releaseevent

    :param db: Database to store push data
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :param repo: Repository where release belongs to
    :type repo: ``repocribro.models.Repository``
    :param payload: Data about release and action
    :type payload: dict
    :param actor: Actor doing the event
    :type actor: dict
    """
    action = payload['action']
    release = Release.create_from_dict(payload['release'], actor, repo)
    db.session.add(release)


def gh_event_repository(db, repo, payload, actor):
    """Process GitHub RepositoryEvent (with commits)

    https://developer.github.com/v3/activity/events/types/#repositoryevent

    :param db: Database to store repository data
    :type db: ``flask_sqlalchemy.SQLAlchemy``
    :param repo: Repository related to event
    :type repo: ``repocribro.models.Repository``
    :param payload: Data about repository and action
    :type payload: dict
    :param actor: Actor doing the event
    :type actor: dict
    """
    action = payload['action']
    if action == 'privatized':
        repo.private = True
        repo.visibility_type = Repository.VISIBILITY_PRIVATE
    elif action == 'publicized':
        repo.private = False
        repo.visibility_type = Repository.VISIBILITY_PUBLIC
    elif action == 'deleted':
        # TODO: consider some signalization of not being @GitHub anymore
        repo.webhook_id = None
        repo.visibility_type = Repository.VISIBILITY_PRIVATE


def make_githup_api_factory(cfg):
    """Simple factory for making the GitHub API client factory

    :param cfg: Configuration of the application
    :type cfg: ``configparser.ConfigParser``
    :return: GitHub API client factory
    :rtype: ``function``
    """
    def github_api_factory(token=None, session=None):
        return GitHubAPI(
            cfg.get('github', 'client_id'),
            cfg.get('github', 'client_secret'),
            cfg.get('github', 'webhooks_secret'),
            session=session,
            token=token
        )
    return github_api_factory


class CoreExtension(Extension):
    #: Name of core extension
    NAME = 'core'
    #: Category of core extension
    CATEGORY = 'basic'
    #: Author of core extension
    AUTHOR = 'Marek Suchánek'
    #: GitHub URL of core extension
    GH_URL = 'https://github.com/MarekSuchanek/repocribro'

    def __init__(self, master, app, db):
        super().__init__(master, app, db)
        self.migrate = flask_migrate.Migrate(self.app, self.db)

    @staticmethod
    def provide_models():
        from .models import all_models
        return all_models

    @staticmethod
    def provide_blueprints():
        from .controllers import all_blueprints
        return all_blueprints

    @staticmethod
    def provide_filters():
        from .filters import all_filters
        return all_filters

    @staticmethod
    def get_gh_webhook_processors():
        """Get all GitHub webhooks processory"""
        return {
            'push': [gh_webhook_push],
            'release': [gh_webhook_release],
            'repository': [gh_webhook_repository],
        }

    @staticmethod
    def get_gh_event_processors():
        """Get all GitHub events processors"""
        return {
            'push': [gh_event_push],
            'release': [gh_event_release],
            'repository': [gh_event_repository],
        }

    def init_business(self):
        """Init business layer (other extensions, what is needed)"""
        from .security import init_login_manager
        login_manager, principals = init_login_manager(self.db)
        login_manager.init_app(self.app)
        principals.init_app(self.app)
        from .api import create_api
        api_manager = create_api(self.app, self.db)

    def init_container(self):
        """Init service DI container of the app"""
        self.app.container.set_factory(
            'gh_api',
            make_githup_api_factory(self.app.container.get('config'))
        )

    def view_core_search_tabs(self, query, tabs_dict):
        """Prepare tabs for search view of core controller

        :param query: Fulltext query for the search
        :type query: str
        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        from .models import User, Organization, Repository
        users = User.fulltext_query(
            query, self.db.session.query(User)
        ).all()
        orgs = Organization.fulltext_query(
            query, self.db.session.query(Organization)
        ).all()
        repos = Repository.fulltext_query(
            query, self.db.session.query(Repository)
        ).all()

        tabs_dict['repositories'] = ViewTab(
            'repositories', 'Repositories', 0,
            flask.render_template('core/search/repos_tab.html', repos=repos),
            octicon='repo', badge=Badge(len(repos))
        )
        tabs_dict['users'] = ViewTab(
            'users', 'Users', 1,
            flask.render_template('core/search/users_tab.html', users=users),
            octicon='person', badge=Badge(len(users))
        )
        tabs_dict['orgs'] = ViewTab(
            'orgs', 'Organizations', 2,
            flask.render_template('core/search/orgs_tab.html', orgs=orgs),
            octicon='organization', badge=Badge(len(orgs))
        )

    def view_core_user_detail_tabs(self, user, tabs_dict):
        """Prepare tabs for user detail view of core controller

        :param user: User which details should be shown
        :type user: ``repocribro.models.User``
        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        tabs_dict['details'] = ViewTab(
            'details', 'Details', 0,
            flask.render_template('core/user/details_tab.html', user=user),
            octicon='person'
        )
        tabs_dict['repositories'] = ViewTab(
            'repositories', 'Repositories', 1,
            flask.render_template(
                'core/repo_owner/repositories_tab.html', owner=user
            ),
            octicon='repo', badge=Badge(len(user.repositories))
        )

    def view_core_org_detail_tabs(self, org, tabs_dict):
        """Prepare tabs for org detail view of core controller

        :param org: Organization which details should be shown
        :type org: ``repocribro.models.Organization``
        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        tabs_dict['details'] = ViewTab(
            'details', 'Details', 0,
            flask.render_template('core/org/details_tab.html', org=org),
            octicon='person'
        )
        tabs_dict['repositories'] = ViewTab(
            'repositories', 'Repositories', 1,
            flask.render_template(
                'core/repo_owner/repositories_tab.html', owner=org
            ),
            octicon='repo', badge=Badge(len(org.repositories))
        )

    def view_core_repo_detail_tabs(self, repo, tabs_dict):
        """Prepare tabs for repo detail view of core controller

        :param repo: Repository which details should be shown
        :type repo: ``repocribro.models.Repository``
        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        tabs_dict['details'] = ViewTab(
            'details', 'Details', 0,
            flask.render_template('core/repo/details_tab.html', repo=repo),
            octicon='repo'
        )
        tabs_dict['releases'] = ViewTab(
            'releases', 'Releases', 1,
            flask.render_template('core/repo/releases_tab.html', repo=repo),
            octicon='tag', badge=Badge(len(repo.releases))
        )
        tabs_dict['updates'] = ViewTab(
            'updates', 'Updates', 2,
            flask.render_template('core/repo/updates_tab.html', repo=repo),
            octicon='git-commit', badge=Badge(len(repo.pushes))
        )

    def view_admin_index_tabs(self, tabs_dict):
        """Prepare tabs for index view of admin controller

        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        from .models import Repository, Role, UserAccount
        accounts = self.db.session.query(UserAccount).all()
        roles = self.db.session.query(Role).all()
        repos = self.db.session.query(Repository).all()
        exts = [e for e in self.master.call('view_admin_extensions', None)
                if e is not None]

        tabs_dict['users'] = ViewTab(
            'users', 'Users', 0,
            flask.render_template('admin/tabs/users.html', accounts=accounts),
            octicon='person', badge=Badge(len(accounts))
        )
        tabs_dict['roles'] = ViewTab(
            'roles', 'Roles', 1,
            flask.render_template('admin/tabs/roles.html', roles=roles),
            octicon='briefcase', badge=Badge(len(roles))
        )
        tabs_dict['repositories'] = ViewTab(
            'repositories', 'Repositories', 2,
            flask.render_template('admin/tabs/repos.html', repos=repos),
            octicon='repo', badge=Badge(len(repos))
        )
        tabs_dict['extensions'] = ViewTab(
            'extensions', 'Extensions', 3,
            flask.render_template('admin/tabs/exts.html', exts=exts),
            octicon='code', badge=Badge(len(exts))
        )

    def view_manage_dashboard_tabs(self, tabs_dict):
        """Prepare tabs for dashboard view of manage controller

        :param tabs_dict: Target dictionary for tabs
        :type tabs_dict: dict of str: ``repocribro.extending.helpers.ViewTab``
        """
        repos = flask_login.current_user.github_user.repositories

        tabs_dict['repositories'] = ViewTab(
            'repositories', 'Repositories', 0,
            flask.render_template(
                'manage/dashboard/repos_tab.html',
                repos=repos
            ),
            octicon='repo', badge=Badge(len(repos))
        )
        tabs_dict['profile'] = ViewTab(
            'profile', 'Profile', 1,
            flask.render_template(
                'manage/dashboard/profile_tab.html',
                user=flask_login.current_user.github_user
            ),
            octicon='person'
        )
        tabs_dict['session'] = ViewTab(
            'session', 'Session', 2,
            flask.render_template(
                'manage/dashboard/session_tab.html',
                token=flask.session['github_token'],
                scopes=flask.session['github_scope']
            ),
            octicon='mark-github'
        )


def make_extension(*args, **kwargs):
    """Alias for instantiating the extension

    Actually not needed, just example that here can be something
    more complex to do before creating the extension.
    """
    return CoreExtension(*args, **kwargs)
