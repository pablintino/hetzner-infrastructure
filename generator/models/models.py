from exceptions.exceptions import UnsupportedChangeException
from utils import try_parseint


class ResourceChange:
    def __init__(self, change_type, resource_type, source=None, target=None):
        if not change_type:
            raise Exception('change_type cannot be null or empty')
        if not resource_type:
            raise Exception('resource_type cannot be null or empty')
        self.type = change_type
        self.resource_type = resource_type
        self.source = source
        self.target = target


class GroupedChanges:
    def __init__(self):
        self.update = []
        self.create = []
        self.destroy = []
        self.noop = []

    def append_change(self, change_model, change_type):
        if change_type == 'no-op':
            self.noop.append(change_model)
        elif change_type == 'create':
            self.create.append(change_model)
        elif change_type == 'destroy':
            self.destroy.append(change_model)
        elif change_type == 'update':
            self.update.append(change_model)
        else:
            raise UnsupportedChangeException(f'{change_type} not supported')


class ResourceModel:
    def __init__(self, res_id=None, res_addr=None):
        int_id = try_parseint(res_id)
        self.id = int_id if int_id else res_id
        self.addr = res_addr


class NodeInterfaceModel(ResourceModel):
    def __init__(self, ip, mac, network, server_id, network_id, res_id=None, res_addr=None):
        super().__init__(res_id, res_addr)
        self.ip = ip
        self.mac = mac
        self.network = network
        self.server_id = server_id
        self.network_id = network_id


class ServerNodeModel(ResourceModel):
    def __init__(self, name, size, roles, public_ip, res_id=None, res_addr=None):
        super().__init__(res_id, res_addr)
        self.name = name
        self.size = size
        self.roles = roles
        self.public_ip = public_ip
        self.network_interfaces = []


class NetworkModel(ResourceModel):
    def __init__(self, name, ip_range, res_id=None, res_addr=None):
        super().__init__(res_id, res_addr)
        self.name = name
        self.ip_range = ip_range


class SubnetModel(ResourceModel):
    def __init__(self, ip_range, network_id, res_id=None, res_addr=None):
        super().__init__(res_id, res_addr)
        self.network_id = network_id
        self.ip_range = ip_range
