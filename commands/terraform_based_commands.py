import os
import json
import utils
import interfaces.terraform.hetzner_provider_mapper

from abc import ABC
from commands.command import Command
from commands.validators.command_validators import KubesprayPatchesValidator
from exceptions.exceptions import UnexpectedTerraformFailureException, CommandConfirmationException
from interfaces.ansible.kubespray_manager import KubesprayManager
from interfaces.terraform import hetzner_provider_mapper
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

            tf_vars = {'ssh_public_key': self.context.ssh_key_manager.get_public_rsa_key_opnessh()}

            plan_file = self.context.temporal_fs.get_temporal_file()
            res, output = self.tf.plan(self.terraform_content, [infra_settings_file], tf_vars, True,
                                       state_file=self.context.cluster_space.tf_state_file, plan_file=plan_file)
            if res:
                # TODO Make some validations
                plan_changes = hetzner_provider_mapper.parse_plan(output)
                if plan_changes.create or plan_changes.destroy or plan_changes.update:
                    res = self.tf.apply(self.terraform_content, [infra_settings_file], tf_vars,
                                        state_file=self.context.cluster_space.tf_state_file, plan_file=plan_file)
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
            if not utils.get_optional_arg(self.context.run_options, 'confirm'):
                raise CommandConfirmationException('Destroy command needs destruction confirmation flag')

            self.prepare_arena()
            infra_settings_file = self.get_dumped_infra_settings()

            tf_vars = {'ssh_public_key': self.context.ssh_key_manager.get_public_rsa_key_opnessh()}
            res = self.tf.destroy(self.terraform_content, [infra_settings_file], tf_vars,
                                  state_file=self.context.cluster_space.tf_state_file)

            if res:
                self.context.cluster_space.destroy_cluster_space()
                self.logger.info('Infrastructure successfully destroyed')
            else:
                self.logger.info('Failed to destroy infrastructure')
        except UnexpectedTerraformFailureException as err:
            self.logger.error(err)
            return False
