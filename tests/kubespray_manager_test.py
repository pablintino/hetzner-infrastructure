import generator.ansible.kubespray_manager
from generator.models.models import ServerNodeModel, NodeInterfaceModel


def __create_dummy_server_list():
    servers = [
        ServerNodeModel(name='node1', size='size1', roles=['kube_control_plane', 'etcd'], public_ip='10.10.10.1',
                        res_id='res_id1', res_addr='res_addr1'),
        ServerNodeModel(name='node2', size='size2', roles=['kube_control_plane', 'etcd'], public_ip='10.10.10.2',
                        res_id='res_id2', res_addr='res_addr2'),
        ServerNodeModel(name='node3', size='size3', roles=['kube_control_plane', 'kube-node'], public_ip='10.10.10.3',
                        res_id='res_id3', res_addr='res_addr3'),
    ]

    servers[0].network_interfaces.append(
        NodeInterfaceModel(ip='192.168.1.1', mac='84:c6:39:bc:23:a7', network=1, res_id='res_id1',
                           res_addr='res_addr1'))
    servers[1].network_interfaces.append(
        NodeInterfaceModel(ip='192.168.1.2', mac='84:c7:39:bc:23:a7', network=1, res_id='res_id2',
                           res_addr='res_addr2'))
    servers[2].network_interfaces.append(
        NodeInterfaceModel(ip='192.168.1.3', mac='84:c8:39:bc:23:a7', network=1, res_id='res_id3',
                           res_addr='res_addr3'))

    return servers


def test_basic_exmaple():
    server_list = __create_dummy_server_list()
    inventory = generator.ansible.kubespray_manager.build_inventory(server_list)
    assert inventory is not None
    assert 'all' in inventory
    assert len(inventory) == 1
    assert 'hosts' in inventory['all']
    assert len(inventory['all']['hosts']) == 3
    assert 'children' in inventory['all']
    assert len(inventory['all']['children']) == 5
    assert 'node1' in inventory['all']['hosts']
    assert '10.10.10.1' == inventory['all']['hosts']['node1']['ansible_host']
    assert '10.10.10.2' == inventory['all']['hosts']['node2']['ansible_host']
    assert '10.10.10.3' == inventory['all']['hosts']['node3']['ansible_host']
    assert '192.168.1.1' == inventory['all']['hosts']['node1']['ip']
    assert '192.168.1.2' == inventory['all']['hosts']['node2']['ip']
    assert '192.168.1.3' == inventory['all']['hosts']['node3']['ip']
    assert 'node2' in inventory['all']['hosts']
    assert 'node3' in inventory['all']['hosts']
    assert 'node1' in inventory['all']['children']['kube_control_plane']['hosts']
    assert 'node2' in inventory['all']['children']['kube_control_plane']['hosts']
    assert 'node3' in inventory['all']['children']['kube_control_plane']['hosts']
    assert 'node1' in inventory['all']['children']['etcd']['hosts']
    assert 'node2' in inventory['all']['children']['etcd']['hosts']
