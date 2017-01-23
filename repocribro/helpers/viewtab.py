import jinja2


class ViewTab:

    def __init__(self, id, name, priority=100, content=''):
        self.id = id
        self.name = name
        self.content = jinja2.Markup(content)
        self.priority = priority
