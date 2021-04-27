from interfaces.ansible.kubespray_manager import update_config_files


def test_override_patches():
    inventory_path = '/home/pablintino/Desktop/kubespray/inventory/mycluster/group_vars'
    patches_dir = '/home/pablintino/Sources/k8s/config/kubespray-config'
    update_config_files(inventory_path, patches_dir)
    print('test')