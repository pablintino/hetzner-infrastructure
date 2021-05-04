import os
import re
import json
import logging
import commands.validators
from exceptions.exceptions import ConfigurationException
from fs.cluster_space import ClusterSpace
from fs.package_manager import PackageManager
from fs.temporal_fs_manager import TemporalFsManager


class GlobalClusterSettings:

    def __init__(self, config_dict):
        # TODO Replace this key retrieval code as is repetitive. Make something more reusable and clean
        self.cluster_name = config_dict.get('cluster-name', None)
        if not self.cluster_name:
            raise ConfigurationException('Cluster name is null or empty in configuration')
        elif not re.match(r'[\w\-. ]+$', self.cluster_name) or len(self.cluster_name) < 5 or len(
                self.cluster_name) > 100:
            raise ConfigurationException(
                'Cluster name is contains invalid chars, is less than 5 characters or exceeds 100')


class TerraformConfiguration:

    def __init__(self, config_dict, packages):
        if 'terraform' in config_dict:
            self.infra_config = config_dict['terraform'].get('infra-config', None)
            if not self.infra_config:
                raise ConfigurationException('Terraform configuration has no infrastructure configuration')

            # TODO Replace this key retrieval code as is repetitive. Make something more reusable and clean
            self.package_name = config_dict['terraform'].get('package', None)
            self.package_manager = packages[self.package_name] if self.package_name in packages else None
            if not self.package_manager:
                raise ConfigurationException('Terraform configuration has an invalid package association')

        else:
            raise ConfigurationException('No Terraform configuration found in generator configuration')


class KubesprayConfiguration:

    def __init__(self, config_dict, packages):
        if 'kubespray' in config_dict:
            # TODO Replace this key retrieval code as is repetitive. Make something more reusable and clean
            self.remote_user = config_dict['kubespray'].get('remote-user')
            self.patches = config_dict['kubespray'].get('patches')
            self.package_name = config_dict['kubespray'].get('package')
            self.package_manager = packages[self.package_name] if self.package_name in packages else None
            if not self.package_manager:
                raise ConfigurationException('Kubespray configuration has an invalid package association')

        else:
            raise ConfigurationException('No Kubespray configuration found in generator configuration')


class RunContext:
    __logger = logging.getLogger(__name__)

    def __init__(self, options):
        self.run_options = options
        self.packages = {}
        self.kubespray_config = None
        self.terraform_config = None
        self.json_path = None
        self.global_settings = None
        self.cluster_space = None
        self.temporal_fs = TemporalFsManager()

    def configure(self):
        self.json_path = self.__get_config_path()
        configuration = self.__parse_configuration()
        self.global_settings = GlobalClusterSettings(configuration)

        # Parse and process declared packages
        self.__prepare_packages(configuration)
        self.kubespray_config = KubesprayConfiguration(configuration, self.packages)
        self.terraform_config = TerraformConfiguration(configuration, self.packages)
        self.cluster_space = ClusterSpace(self.global_settings.cluster_name)

        return self

    def validate(self):
        for validator in commands.validators.context_validators:
            validator(self)
        return self

    def __prepare_packages(self, configuration):
        packages_config_node = configuration.get('packages')
        if packages_config_node:
            for package_name, package_node in packages_config_node.items():
                if package_name not in self.packages:
                    package_manager = PackageManager(package_name, package_node, self.temporal_fs)
                    package_manager.prepare_content()
                    self.packages[package_name] = package_manager
                else:
                    raise ConfigurationException(f'Package {package_name} is duplicated inside configuration')

    @staticmethod
    def __get_config_path():
        current_dir_path = os.path.join(os.getcwd(), 'k8s-config.json')
        if os.path.isfile(current_dir_path):
            return current_dir_path

        user_path = os.path.join(os.path.join(os.path.expanduser('~'), '.k8sgen'), 'k8s-config.json')
        if os.path.isfile(user_path):
            return user_path

        raise ConfigurationException('No json configuration file present')

    def __parse_configuration(self):
        if self.json_path:
            try:
                with open(self.json_path, 'r') as json_file:
                    return json.load(json_file)
            except ValueError:
                raise ConfigurationException('Cannot load generator configuration')

    def destroy(self):
        self.temporal_fs.cleanup()
