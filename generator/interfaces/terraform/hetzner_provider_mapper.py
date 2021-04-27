from generator.models.models import ServerNodeModel, ResourceChange, NodeInterfaceModel, NetworkModel, \
    SubnetModel, GroupedChanges
from jsonpath_ng.ext import parse

from generator.exceptions.exceptions import UnsupportedChangeException
from utils import remove_prefix

mappers = {}


def __parse_server_nodes(node, address):
    server = ServerNodeModel(name=node.get('name'), size=node.get('server_type'), roles=None,
                             public_ip=node.get('ipv4_address'), res_id=node.get('id'), res_addr=address)
    server.roles = [remove_prefix(k, 'k8sgen.rol.') for k, v in node.get('labels').items() if
                    k.startswith('k8sgen.rol.')]
    return server


def __parse_node_interface(node, address):
    return NodeInterfaceModel(ip=node.get('ip'), mac=node.get('mac_address'), network=node.get('network_id'),
                              server_id=node.get('server_id'), network_id=node.get('network_id'),
                              res_id=node.get('id'), res_addr=address)


def __parse_network(node, address):
    return NetworkModel(ip_range=node.get('ip_range'), name=node.get('name'), res_id=node.get('id'), res_addr=address)


def __parse_subnet(node, address):
    return SubnetModel(ip_range=node.get('ip_range'), network_id=node.get('network_id'), res_id=node.get('id'),
                       res_addr=address)


def __map_network_ifs_servers(resource_list):
    server_map = {serv.id: serv for serv in resource_list if isinstance(serv, ServerNodeModel)}
    for if_res in [resource for resource in resource_list if isinstance(resource, NodeInterfaceModel)]:
        if if_res.server_id and if_res.server_id in server_map:
            server_map[if_res.server_id].network_interfaces.append(if_res)


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


def parse_state(terraform_state):
    if terraform_state is None:
        raise TypeError('terraform_state cannot be null')

    resources = []
    for resource_node in [match.value for match in parse("$.values.root_module.resources[*]").find(terraform_state)]:
        resource_type = resource_node.get('type')
        if resource_type not in mappers:
            print('Not supported type')
        else:
            resources.append(mappers[resource_type](resource_node.get('values'), resource_node.get('address')))

    __map_network_ifs_servers(resources)

    return resources


mappers['hcloud_server'] = __parse_server_nodes
mappers['hcloud_server_network'] = __parse_node_interface
mappers['hcloud_network'] = __parse_network
mappers['hcloud_network_subnet'] = __parse_subnet
