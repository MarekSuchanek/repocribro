from .repocribro import create_app, get_auth_cfg

app = create_app(get_auth_cfg())
