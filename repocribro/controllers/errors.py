import flask

#: Errors controller blueprint
errors = flask.Blueprint('errors', __name__)


@errors.app_errorhandler(403)
def err_forbidden(error):
    """Error handler for HTTP 403 - Unauthorized"""
    return flask.render_template('error/403.html'), 403


@errors.app_errorhandler(404)
def err_not_found(error):
    """Error handler for HTTP 403 - Not Found"""
    return flask.render_template('error/404.html'), 404


@errors.app_errorhandler(410)
def err_gone(error):
    """Error handler for HTTP 410 - Gone"""
    return flask.render_template('error/410.html'), 410


@errors.app_errorhandler(500)
def err_internal(error):
    """Error handler for HTTP 500 - Internal Server Error"""
    return flask.render_template('error/500.html'), 500


@errors.app_errorhandler(501)
def err_internal(error):
    """Error handler for HTTP 501 - Not Implemented"""
    return flask.render_template('error/501.html'), 501
