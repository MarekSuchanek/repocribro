from flask_script import Command


class DbCreateCommand(Command):
    """Perform basic create all tables"""

    # TODO: think about clear, drop_all, dump, ..
    def run(self):
        from ..database import db
        print('Performing db.create_all()')
        db.create_all()
        print('Database has been created')
