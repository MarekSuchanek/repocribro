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

