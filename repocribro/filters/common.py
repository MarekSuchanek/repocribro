import jinja2


def yes_no(value):
    return 'Yes' if value else 'No'


def email_link(email):
    if email is None:
        return ''
    return jinja2.Markup('<a href="mailto:{0}">{0}</a>'.format(email))


def ext_link(url):
    if url is None:
        return ''
    return jinja2.Markup('<a href="{0}" target="_blank">{0}</a>'.format(url))


def flash_class(category):
    if category == 'error':
        return 'danger'
    return category


common_filters = {
    'yes_no': yes_no,
    'email_link': email_link,
    'ext_link': ext_link,
    'flash_class': flash_class
}
