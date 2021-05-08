import os
import json
import interfaces.terraform.hetzner_provider_mapper


from abc import ABC
from commands.command import Command
from commands.validators.command_validators import KubesprayPatchesValidator
from exceptions.exceptions import UnexpectedTerraformFailureException
from interfaces.ansible.kubespray_manager import KubesprayManager
from interfaces.terraform.terraform_interface import Terraform


class TerraformBaseCommand(Command, ABC):

    def __init__(self, context):
        super().__init__(context, context_validators=[KubesprayPatchesValidator])
        self.terraform_content = None
        self.tf = Terraform()

    def prepare_arena(self):
        self.terraform_content = self.context.terraform_config.package_manager.get_content()
        if not os.listdir(self.context.cluster_space.tf_plugins_directory):
            if not self.tf.providers_mirror(self.terraform_content, self.context.cluster_space.tf_plugins_directory):
                raise UnexpectedTerraformFailureException('Cannot prepare terraform needed plugins')

        if not self.tf.init(self.terraform_content, self.context.cluster_space.tf_plugins_directory):
            raise UnexpectedTerraformFailureException('Terraform infrastructure initialization has failed')

    def get_dumped_infra_settings(self):
        tf_vars_file = self.context.temporal_fs.get_temporal_file(ext='.tfvars.json')
        with open(tf_vars_file, 'w') as file:
            json.dump(self.context.terraform_config.infra_config, file)
        return tf_vars_file

    def get_state_resources(self):
        res_ok, current_state = self.tf.show(self.terraform_content,
                                             input_file=self.context.cluster_space.tf_state_file)
        if not res_ok:
            raise UnexpectedTerraformFailureException('Cannot obtain current terraform state')
        return interfaces.terraform.hetzner_provider_mapper.parse_state(current_state)


class CreateClusterCommand(TerraformBaseCommand):

    def __init__(self, context):
        super().__init__(context)

    def run(self):
        try:
            self.prepare_arena()
            infra_settings_file = self.get_dumped_infra_settings()
            res, output = self.tf.plan(self.terraform_content, [infra_settings_file], True,
                                       state_file=self.context.cluster_space.tf_state_file)
            if res:
                # TODO Make some validations
                # plan_changes = hetzner_provider_mapper.parse_plan(output)
                # TODO Call apply with the planned state instead of recalculate all
                res = self.tf.apply(self.terraform_content, [infra_settings_file],
                                    state_file=self.context.cluster_space.tf_state_file)
                if res:
                    self.logger.info('Infrastructure successfully created')
                    spray = KubesprayManager(self.context, self.get_state_resources())
                    spray.create_cluster()

                else:
                    self.logger.info('Failed to create infrastructure')

        except UnexpectedTerraformFailureException as err:
            self.logger.error(err)
            # TODO Raise to end with a proper exit code


class DestroyClusterCommand(TerraformBaseCommand):

    def __init__(self, context):
        super().__init__(context)

    def run(self):

        try:
            self.prepare_arena()
            infra_settings_file = self.get_dumped_infra_settings()
            res = self.tf.destroy(self.terraform_content, [infra_settings_file],
                                  state_file=self.context.cluster_space.tf_state_file)
            if res:
                self.logger.info('Infrastructure successfully destroyed')
            else:
                self.logger.info('Failed to destroy infrastructure')
        except UnexpectedTerraformFailureException as err:
            self.logger.error(err)
            return False
