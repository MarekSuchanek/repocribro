from flask import Flask
from .core.controllers import core

app = Flask(__name__)

app.register_blueprint(core)
# TODO: load all parts
# TODO: load all extensions


def start():
    # TODO: improve CLI for start
    # TODO: load config file(s)
    app.run()
