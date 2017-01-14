from flask import Blueprint

core = Blueprint('core', __name__, url_prefix='/')


@core.route('/')
def index():
    return "TODO: Landing"
