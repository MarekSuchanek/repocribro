import flask
import functools


def webhook_data_requires(*fields):
    """Decorator for checking *data* fields

    :param fields: Required fields
    :type fields: list of str
    :return: Decorated function
    :rtype: function

    :raises: HTTPException(404)
    """
    def check_data_requires(func):
        @functools.wraps(func)
        def webhook_processor(repo, data, delivery_id):
            for field in fields:
                if field not in data:
                    flask.abort(400)
            return func(repo, data, delivery_id)
    return check_data_requires
