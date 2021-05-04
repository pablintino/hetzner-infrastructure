import logging
import os

import ansible_runner

from interfaces.ansible.kubespray_manager import build_inventory
from interfaces.terraform.hetzner_provider_mapper import parse_state
from interfaces.terraform.terraform_interface import Terraform

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


# TODO Remove hardcoded var
kubespray_dir = '/home/pablintino/Desktop/kubespray'

main_tf_file = '../terraform/hetzner-k8s-cluster.tf'
config_vars_filename = os.path.join(os.path.dirname(main_tf_file), 'config.json')
var_files = [config_vars_filename] if os.path.isfile(config_vars_filename) else None


tf = Terraform()
res_ok, current_state = tf.show(main_tf_file)
resources = parse_state(current_state)

inventory = build_inventory(resources)


##################### FILES TO PREPARE #######################
# !! Clone kubespray. It's root directory will be known as 'proyect_base'
# proyect_base/env/ssh_key => SSH PK to access remote servers
# proyect_base/inventory/hosts => Ansible inventory file as usual
# proyect_base/inventory/group_vars => All the files inside the original kubespray vars examples. Edit as needed.

r = ansible_runner.run(
    private_data_dir=kubespray_dir,
    playbook='cluster.yml',
    project_dir=kubespray_dir,
    cmdline='-u root -b',
    inventory=inventory
)

print(r)
