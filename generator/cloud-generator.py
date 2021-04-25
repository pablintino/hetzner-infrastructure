import os
import logging
from generator.terraform.terraform_interface import Terraform
from generator.terraform.hetzner_provider_mapper import parse_plan, parse_state

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

main_tf_file = '../terraform/hetzner-k8s-cluster.tf'
config_vars_filename = os.path.join(os.path.dirname(main_tf_file), 'config.tfvars')
var_files = [config_vars_filename] if os.path.isfile(config_vars_filename) else None


tf = Terraform()
res, json_out = tf.plan(main_tf_file, vars_files=var_files, json_out=True)
if res:
    plan_model = parse_plan(json_out)
    if plan_model.create or plan_model.update or plan_model.destroy:
        if tf.apply(main_tf_file, vars_files=var_files):
            res_ok, current_state = tf.show(main_tf_file)
            resources = parse_state(current_state)

            print('test')

        else:
            logger.error('An error occurred while applying infrastructure changes.')
    else:
        logger.info('No changes to infrastructure detected. Nothing tot do.')
