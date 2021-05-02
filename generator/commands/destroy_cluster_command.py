import os
import json
import logging

from interfaces.terraform.terraform_interface import Terraform

__logger = logging.getLogger(__name__)


def destroy_cluster_command(context):
    terraform_content = context.terraform_config.package_manager.get_content()

    tf = Terraform()

    if not os.listdir(context.cluster_space.tf_plugins_directory):
        result = tf.providers_mirror(terraform_content, context.cluster_space.tf_plugins_directory)
        if not result:
            __logger.error('Cannot prepare terraform needed plugins')
            return False

    if not tf.init(terraform_content, context.cluster_space.tf_plugins_directory):
        __logger.error('Terraform initialization has failed')
        return False

    tf_vars_file = context.temporal_fs.get_temporal_file(ext='.tfvars.json')
    with open(tf_vars_file, 'w') as file:
        json.dump(context.terraform_config.infra_config, file)

    res = tf.destroy(terraform_content, [tf_vars_file], state_file=context.cluster_space.tf_state_file)
    if res:
        __logger.info('Infrastructure successfully destroyed')
    else:
        __logger.info('Failed to destroy infrastructure')

    return res
