import flask

user = flask.Blueprint('user', __name__, url_prefix='/user')


@user.route('/dashboard')
def dashboard():
    # TODO: require logged user (decorator?)
    return flask.render_template('user/dashboard.html',
                                 token=flask.session['github_token'],
                                 scopes=flask.session['github_scope']
                                 )
