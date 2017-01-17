import flask

core = flask.Blueprint('core', __name__, url_prefix='/')


@core.route('/')
def index():
    return flask.render_template('core/index.html')
