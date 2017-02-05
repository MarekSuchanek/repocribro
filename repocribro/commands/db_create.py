import flask_script


class DbCreateCommand(flask_script.Command):
    """Perform basic create all tables"""

    def run(self):
        from ..database import db
        print('Performing db.create_all()')
        db.create_all()
        print('Database has been created')
