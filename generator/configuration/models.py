
class ConfigurationModel:
    def __init__(self):
        self.nodes = []


class NodeModel:

    def __init__(self, name, size, roles):
        self.name = name
        self.size = size
        self.roles = roles
        self.ip = None
