import flask
import flask_bower
from .core.controllers import core

app = flask.Flask(__name__)
flask_bower.Bower(app)

app.register_blueprint(core)
# TODO: load all parts
# TODO: load all extensions


@app.errorhandler(403)
def not_found(error):
    return flask.render_template('error/403.html'), 403


@app.errorhandler(404)
def not_found(error):
    return flask.render_template('error/404.html'), 404


@app.errorhandler(410)
def not_found(error):
    return flask.render_template('error/410.html'), 410


@app.errorhandler(500)
def not_found(error):
    return flask.render_template('error/500.html'), 500


def start():
    # TODO: improve CLI for start
    # TODO: load config file(s)
    app.config['DEBUG'] = True
    app.run()
