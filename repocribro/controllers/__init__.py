from .admin import admin
from .auth import auth
from .core import core
from .errors import errors
from .manage import manage
from .webhooks import webhooks

all_blueprints = [
    admin, auth, core, errors, manage, webhooks
]

__all__ = [
    'all_blueprints',
    'admin', 'auth', 'core', 'errors', 'manage', 'webhooks'
]
