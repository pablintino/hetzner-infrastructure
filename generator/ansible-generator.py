import logging
import ansible_runner

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

ansible_settings = {'become': 'true', 'become_user': 'root'}
# TODO Remove hardcoded var
kubespray_dir = '/home/pablintino/Desktop/kubespray'

##################### FILES TO PREPARE #######################
# !! Clone kubespray. It's root directory will be known as 'proyect_base'
# proyect_base/env/ssh_key => SSH Pk to access remote servers
# proyect_base/inventory/hosts => Ansible inventory file as usual
# proyect_base/inventory/group_vars => All the files inside the original kubespray vars examples. Edit as needed.

r = ansible_runner.run(
    private_data_dir=kubespray_dir,
    playbook='cluster.yml',
    project_dir=kubespray_dir,
    settings=ansible_settings
)
