import jinja2


class ViewTab:
    """Tab for the tabbed view at pages"""
    def __init__(self, id, name, priority=100, content='',
                 octicon=None, badge=None):
        self.id = id
        self.name = name
        self.content = jinja2.Markup(content)
        self.priority = priority
        self.octicon = octicon
        self.badge = badge

    def __lt__(self, other):
        return self.priority < other.priority


class Badge:
    """Simple Twitter Bootstrap badge representation"""
    def __init__(self, content):
        self.content = content


class ExtensionView:
    """View object for extensions"""
    def __init__(self, name, category, author,
                 admin_url=None, home_url=None, gh_url=None):
        self.name = name
        self.category = category
        self.author = author
        self.admin_url = admin_url
        self.home_url = home_url
        self.gh_url = gh_url

    @staticmethod
    def from_class(cls):
        """Make view from Extension class"""
        return ExtensionView(
            getattr(cls, 'NAME', 'uknown'),
            getattr(cls, 'CATEGORY', ''),
            getattr(cls, 'AUTHOR', ''),
            getattr(cls, 'ADMIN_URL', None),
            getattr(cls, 'HOME_URL', None),
            getattr(cls, 'GH_URL', None),
        )
