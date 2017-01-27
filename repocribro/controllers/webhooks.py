import flask
from ..github import GitHubAPI
from ..models import Repository, db

webhooks = flask.Blueprint('webhooks', __name__, url_prefix='/webhook/github')

# TODO: move webhooks logic somewhere else


def gh_webhook_push(repo, data, deliver_id):
    # TODO: lookup repository and add push (commits)
    return ''


def gh_webhook_release(repo, data, deliver_id):
    # TODO: lookup repository and add release
    return ''


def gh_webhook_repository(repo, data, deliver_id):
    # TODO: lookup repository and update it
    return ''


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
