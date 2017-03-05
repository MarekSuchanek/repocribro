from .admin import admin
from .auth import auth
from .core import core
from .errors import errors
from .manage import manage
from .rest_api import rest_api
from .webhooks import webhooks

all_blueprints = [
    admin, auth, core, errors, manage, rest_api, webhooks
]

__all__ = [
    'all_blueprints',
    'admin', 'auth', 'core', 'errors', 'manage', 'rest_api', 'webhooks'
]
