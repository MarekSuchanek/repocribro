from .common import common_filters
from .models import model_filters


def register_filters_from_dict(app, filters_dict):
    for name, func in filters_dict.items():
        app.jinja_env.filters[name] = func


def register_filters(app):
    register_filters_from_dict(app, common_filters)
    register_filters_from_dict(app, model_filters)
