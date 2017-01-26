import flask

webhooks = flask.Blueprint('webhooks', __name__, url_prefix='/webhook/github')
# TODO: secure webhooks: https://developer.github.com/webhooks/securing/


@webhooks.route('', methods=['POST'])
def gh_webhook():
    return ''


@webhooks.route('/push', methods=['POST'])
def gh_push():
    data = flask.request.get_json()
    # TODO: lookup repository and add push (commits)
    return ''


@webhooks.route('/repository', methods=['POST'])
def gh_repository():
    data = flask.request.get_json()
    # TODO: lookup repository and update it
    return ''


@webhooks.route('/release', methods=['POST'])
def release():
    data = flask.request.get_json()
    # TODO: lookup repository and add release
    return ''
