import flask
from ..github import GitHubAPI
from ..models import Repository, Push, Release, db

webhooks = flask.Blueprint('webhooks', __name__, url_prefix='/webhook/github')

# TODO: move webhooks logic somewhere else


def gh_webhook_push(repo, data, deliver_id):
    if 'push' not in data or 'sender' not in data:
        flask.abort(400)

    # TODO: deal with limit of commits in webhook msg (20)
    push = Push.create_from_dict(data['push'], data['sender'], repo)
    db.session.add(push)
    for commit in push.commits:
        db.session.add(commit)


def gh_webhook_release(repo, data, deliver_id):
    if 'release' not in data or 'sender' not in data:
        flask.abort(400)

    release = Release.create_from_dict(data['release'], data['sender'], repo)
    db.session.add(release)


def gh_webhook_repository(repo, data, deliver_id):
    if 'action' not in data or 'reopsitory' not in data:
        flask.abort(400)

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
def gh_webhook():
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
    if not GitHubAPI.webhook_verify_signature(data, signature):
        return flask.abort(404)

    repo = Repository.query.get_or_404(data['repository']['id'])

    for event_processor in hooks.get(event, []):
        event_processor(repo=repo, data=data, deliver_id=delivery_id)

    db.session.commit()
    return ''
