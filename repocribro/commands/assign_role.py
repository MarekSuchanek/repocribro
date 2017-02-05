import flask_script


class AssignRoleCommand(flask_script.Command):
    """Assign role to user"""

    option_list = (
        flask_script.Option('--login', '-l', dest='login'),
        flask_script.Option('--role', '-r', dest='role_name'),
    )

    def run(self, login, role_name):
        from ..database import db
        from ..models import Role, User
        user = db.session.query(User).filter_by(login=login).first()
        if user is None:
            print('User {} not found'.format(login))
            exit(1)
        elif user.user_account.has_role(role_name):
            print('User {} already has role {}'.format(login, role_name))
            exit(2)
        role = db.session.query(Role).filter_by(name=role_name).first()
        if role is None:
            print('Role {} not in DB... adding'.format(role_name))
            role = Role(role_name, '')
            db.session.add(role)
        user.user_account.roles.append(role)
        db.session.commit()
        print('Role {} added to {}'.format(role_name, login))
