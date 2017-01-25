import flask
from ..security import permissions

admin = flask.Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('')
@permissions.admin_role.require(404)
def index():
    return flask.render_template('admin/index.html')

