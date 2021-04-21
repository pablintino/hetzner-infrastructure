import json

from generator.configuration.models import NodeModel, ConfigurationModel
from generator.exceptions.exceptions import ConfigurationValidationException


def __validate_nullability(json_node, field):
    prop = json_node.get(field)
    if not prop:
        raise ConfigurationValidationException(f'Node {field} cannot be null or empty')
    return prop


def __parse_nodes_configuration(nodes_section):
    nodes_dict = {}
    for json_node in nodes_section:
        node_name = __validate_nullability(json_node, 'name')
        node_roles = __validate_nullability(json_node, 'roles')
        node_size = __validate_nullability(json_node, 'size')
        node = NodeModel(name=node_name, roles=node_roles, size=node_size)
        nodes_dict[node.name] = node
    return nodes_dict


def parse_configuration(file_path):
    with open(file_path, 'r') as file:
        json_config = json.load(file)
        config_model = ConfigurationModel()
        config_model.nodes = __parse_nodes_configuration(json_config.get('nodes'))
        return config_model
