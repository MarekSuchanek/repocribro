import flask
import flask_bower
import flask_migrate

from .extending import Extension
from .extending.helpers import ViewTab, Badge


class CoreExtension(Extension):
    NAME = 'core'
    CATEGORY = 'basic'
    AUTHOR = 'Marek Suchánek'
    GH_URL = 'https://github.com/MarekSuchanek/repocribro'

    def __init__(self, app, db, *args, **kwargs):
        super().__init__(app, db)
        self.bower = flask_bower.Bower(self.app)
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

    def init_business(self, *args, **kwargs):
        from .security import init_login_manager
        login_manager, principals = init_login_manager(self.db)
        login_manager.init_app(self.app)
        principals.init_app(self.app)

    def init_post_injector(self, *args, **kwargs):
        # flask_restless is not compatible with flask_injector!
        from .api import create_api
        api_manager = create_api(self.app, self.db)

    def view_core_search_tabs(self, *args, **kwargs):
        query = kwargs.get('query', '')
        tabs_dict = kwargs.get('tabs_dict')

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

    def view_core_user_detail_tabs(self, *args, **kwargs):
        user = kwargs.get('user')
        tabs_dict = kwargs.get('tabs_dict')

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

    def view_core_org_detail_tabs(self, *args, **kwargs):
        org = kwargs.get('org')
        tabs_dict = kwargs.get('tabs_dict')

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

    def view_core_repo_detail_tabs(self, *args, **kwargs):
        repo = kwargs.get('repo')
        tabs_dict = kwargs.get('tabs_dict')

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


def make_extension(*args, **kwargs):
    return CoreExtension(*args, **kwargs)
