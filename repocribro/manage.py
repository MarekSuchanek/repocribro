from .repocribro import create_app, get_auth_cfg

app, manager = create_app(get_auth_cfg())
manager.run()
