import flask_restless

from .models import User, Organization, Repository, Push, Commit, Release


def create_api(app, db):
    # TODO: allow get by login (user/org) and full_name (repo)
    api_manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
    api_manager.create_api(
        User, methods=['GET'], collection_name='user'
    )
    api_manager.create_api(
        Organization, methods=['GET'], collection_name='org'
    )
    api_manager.create_api(
        Repository, methods=['GET'], collection_name='repo'
    )
    api_manager.create_api(
        Push, methods=['GET'], collection_name='push'
    )
    api_manager.create_api(
        Commit, methods=['GET'], collection_name='commit'
    )
    api_manager.create_api(
        Release, methods=['GET'], collection_name='release'
    )
    return api_manager
