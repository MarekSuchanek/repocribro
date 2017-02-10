import flask
import flask_script


class DbCreateCommand(flask_script.Command):
    """Perform procedure create all tables"""

    def run(self):
        """Run the db-create command to create all tables and
        constraints
        """
        db = flask.current_app.container.get('db')
        print('Performing db.create_all()')
        db.create_all()
        print('Database has been created')
