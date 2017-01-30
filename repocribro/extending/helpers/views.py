import jinja2


class ViewTab:

    def __init__(self, id, name, priority=100, content='',
                 octicon=None, badge=None):
        self.id = id
        self.name = name
        self.content = jinja2.Markup(content)
        self.priority = priority
        self.octicon = octicon
        self.badge = badge


class Badge:

    def __init__(self, content):
        self.content = content


class ExtensionView:
    def __init__(self, name, category, author,
                 admin_url=None, home_url=None, gh_url=None):
        self.name = name
        self.category = category
        self.author = author
        self.admin_url = admin_url
        self.home_url = home_url
        self.gh_url = gh_url
