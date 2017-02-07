import jinja2


def yes_no(value):
    """Convert boolen value to text representation

    :param value: Truth value to be converted
    :type value: bool
    :return: Yes or No text
    :rtype: str
    """
    return 'Yes' if value else 'No'


def email_link(email):
    """Convert email string to HTML link

    :param email: Email address
    :type email: str
    :return: HTML code with hyperlink mailto
    :rtype: ``jinja2.Markup``
    """
    if email is None:
        return ''
    return jinja2.Markup('<a href="mailto:{0}">{0}</a>'.format(email))


def ext_link(url):
    """Convert URL string to HTML link

    :param email: URL
    :type email: str
    :return: HTML code with hyperlink
    :rtype: ``jinja2.Markup``
    """
    if url is None:
        return ''
    return jinja2.Markup('<a href="{0}" target="_blank">{0}</a>'.format(url))


def flash_class(category):
    """Convert flash message category to CSS class
    for Twitter Bootstrap alert

    :param category: Category of flash message
    :type category: str
    :return: CSS class for category
    :rtype: str
    """
    if category == 'error':
        return 'danger'
    return category


#: Container with all common filters with their names in views
common_filters = {
    'yes_no': yes_no,
    'email_link': email_link,
    'ext_link': ext_link,
    'flash_class': flash_class
}
