import flask
import flask_bower
from .core.controllers import core

app = flask.Flask(__name__)
flask_bower.Bower(app)

app.register_blueprint(core)
# TODO: load all parts
# TODO: load all extensions


def start():
    # TODO: improve CLI for start
    # TODO: load config file(s)
    app.config['DEBUG'] = True
    app.run()
