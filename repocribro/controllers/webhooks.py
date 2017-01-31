import flask
import flask_sqlalchemy
import functools
import injector

from ..github import GitHubAPI
from ..models import Repository, Push, Release

webhooks = flask.Blueprint('webhooks', __name__, url_prefix='/webhook/github')

# TODO: move webhooks logic somewhere else


# Decorator for checking data fields
def webhook_data_requires(*fields):
    def check_data_requires(func):
        @functools.wraps(func)
        def webhook_processor(repo, data, delivery_id):
            for field in fields:
                if field not in data:
                    flask.abort(400)
            return func(repo, data, delivery_id)
    return check_data_requires


@webhook_data_requires('push', 'sender')
def gh_webhook_push(db, repo, data, delivery_id):
    # TODO: deal with limit of commits in webhook msg (20)
    push = Push.create_from_dict(data['push'], data['sender'], repo)
    db.session.add(push)
    for commit in push.commits:
        db.session.add(commit)


@webhook_data_requires('release', 'sender')
def gh_webhook_release(db, repo, data, delivery_id):
    release = Release.create_from_dict(data['release'], data['sender'], repo)
    db.session.add(release)


@webhook_data_requires('action', 'repository')
def gh_webhook_repository(db, repo, data, delivery_id):
    # This can be one of "created", "deleted", "publicized", or "privatized".
    # TODO: find out where is "updated" action
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


# TODO: extensible registered hooks
hooks = {
    'push': [gh_webhook_push],
    'release': [gh_webhook_release],
    'repository': [gh_webhook_repository],
}


@webhooks.route('', methods=['POST'])
@injector.inject(db=flask_sqlalchemy.SQLAlchemy,
                 gh_api=GitHubAPI)
def gh_webhook(db, gh_api):
    headers = flask.request.headers
    agent = headers.get('User-Agent', '')
    signature = headers.get('X-Hub-Signature', '')
    delivery_id = headers.get('X-GitHub-Delivery', '')
    event = headers.get('X-GitHub-Event', '')
    data = flask.request.get_json()

    if not agent.startswith('GitHub-Hookshot/'):
        return flask.abort(404)
    if data is None or 'repository' not in data:
        return flask.abort(400)
    if not gh_api.webhook_verify_signature(data, signature):
        return flask.abort(404)

    repo = db.session.query(Repository).get_or_404(data['repository']['id'])

    for event_processor in hooks.get(event, []):
        event_processor(db=db, repo=repo, data=data, deliver_id=delivery_id)

    db.session.commit()
    return ''
