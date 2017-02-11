import flask

from ..models import Repository

webhooks = flask.Blueprint('webhooks', __name__, url_prefix='/webhook/github')


@webhooks.route('', methods=['POST'])
def gh_webhook():
    """Point for GitHub webhook msgs (POST handler)"""
    db = flask.current_app.container.get('db')
    ext_master = flask.current_app.container.get('ext_master')
    gh_api = flask.current_app.container.get('gh_api')

    hooks_list = ext_master.call('get_gh_webhook_processors', default={})
    hooks = {}
    for ext_hooks in hooks_list:
        for hook_event in ext_hooks:
            if hook_event not in hooks:
                hooks[hook_event] = []
            hooks[hook_event].extend(ext_hooks[hook_event])

    headers = flask.request.headers
    agent = headers.get('User-Agent', '')
    signature = headers.get('X-Hub-Signature', '')
    delivery_id = headers.get('X-GitHub-Delivery', '')
    event = headers.get('X-GitHub-Event', '')
    data = flask.request.get_json()

    if not agent.startswith('GitHub-Hookshot/'):
        flask.abort(404)
    if data is None or 'repository' not in data:
        flask.abort(404)
    if not gh_api.webhook_verify_signature(flask.request.data, signature):
        flask.abort(404)

    repo = db.session.query(Repository).filter_by(
        github_id=data['repository']['id']
    ).first()
    if repo is None:
        flask.abort(404)

    for event_processor in hooks.get(event, []):
        event_processor(db=db, repo=repo, data=data, delivery_id=delivery_id)

    repo.events_updated()
    db.session.commit()
    return ''
