from generator.configuration.models import ServerNodeModel, ResourceChange, NodeInterfaceModel, NetworkModel, \
    SubnetModel, GroupedChanges
from jsonpath_ng.ext import parse

from generator.exceptions.exceptions import UnsupportedChangeException

mappers = {}


def __parse_server_nodes(node, address):
    return ServerNodeModel(name=node.get('name'), size=node.get('server_type'), roles=None,
                           public_ip=node.get('ipv4_address'), res_id=node.get('id'), res_addr=address)


def __parse_node_interface(node, address):
    return NodeInterfaceModel(ip=node.get('ip'), mac=node.get('mac_address'), network=node.get('network_id'),
                              res_id=node.get('id'), res_addr=address)


def __parse_network(node, address):
    return NetworkModel(ip_range=node.get('ip_range'), name=node.get('name'), res_id=node.get('id'), res_addr=address)


def __parse_subnet(node, address):
    return SubnetModel(ip_range=node.get('ip_range'), network_id=node.get('network_id'), res_id=node.get('id'),
                       res_addr=address)


def parse_plan(terraform_plan):
    changes = GroupedChanges()
    for res_change in [match.value for match in parse("$.resource_changes[*]").find(terraform_plan)]:
        resource_type = res_change.get('type')
        if resource_type not in mappers:
            print('Not supported type')
        else:
            change_node = res_change.get('change')
            source_res = mappers[resource_type](change_node.get('before'),
                                                res_change.get('address')) if change_node.get('before') else None
            target_res = mappers[resource_type](change_node.get('after'), res_change.get('address')) if change_node.get(
                'after') else None

            if not change_node.get('actions') or len(change_node.get('actions')) != 1:
                raise UnsupportedChangeException(f'{change_type} not supported')

            change_type = change_node.get('actions')[0]
            resource_change = ResourceChange(change_type, resource_type, source=source_res,
                                             target=target_res)
            changes.append_change(resource_change, change_type)

    return changes


mappers['hcloud_server'] = __parse_server_nodes
mappers['hcloud_server_network'] = __parse_node_interface
mappers['hcloud_network'] = __parse_network
mappers['hcloud_network_subnet'] = __parse_subnet
