import os
import re
import json
import logging

import utils
from exceptions.exceptions import ConfigurationException
from fs.cluster_space import ClusterSpace
from fs.package_manager import PackageManager
from fs.temporal_fs_manager import TemporalFsManager
from ssh_key_manager import SshRsaKeyManager


class GlobalClusterSettings:

    def __init__(self, config_dict):
        try:
            self.cluster_name = config_dict.get('cluster-name', None)
            if not self.cluster_name:
                raise ConfigurationException('Cluster name is null or empty in configuration')
            elif not re.match(r'[\w\-. ]+$', self.cluster_name) or len(self.cluster_name) < 5 or len(
                    self.cluster_name) > 100:
                raise ConfigurationException(
                    'Cluster name is contains invalid chars, is less than 5 characters or exceeds 100')
        except KeyError as key_error:
            raise ConfigurationException(f'Global settings {key_error.args[0]} is null or empty') from key_error


class TerraformConfiguration:

    def __init__(self, config_dict, packages):
        if 'terraform' in config_dict:
            try:
                self.infra_config = config_dict['terraform']['infra-config']
                self.package_name = config_dict['terraform']['package']
                self.package_manager = packages[self.package_name] if self.package_name in packages else None
                if not self.package_manager:
                    raise ConfigurationException('Terraform configuration has an invalid package association')
            except KeyError as key_error:
                raise ConfigurationException(f'Terraform {key_error.args[0]} is null or empty') from key_error
        else:
            raise ConfigurationException('No Terraform configuration found in generator configuration')


class KubesprayConfiguration:

    def __init__(self, config_dict, packages):
        if 'kubespray' in config_dict:
            try:
                self.remote_user = config_dict['kubespray'].get('remote-user')
                self.patches = config_dict['kubespray'].get('patches', [])
                self.package_name = config_dict['kubespray']['package']
                self.package_manager = packages[self.package_name] if self.package_name in packages else None
                if not self.package_manager:
                    raise ConfigurationException('Kubespray configuration has an invalid package association')
            except KeyError as key_error:
                raise ConfigurationException(f'Terraform {key_error.args[0]} is null or empty') from key_error
        else:
            raise ConfigurationException('No Kubespray configuration found in generator configuration')


class RunContext:
    __logger = logging.getLogger(__name__)

    def __init__(self, options):
        self.run_options = options
        self.packages = {}
        self.generator_dir = None
        self.kubespray_config = None
        self.terraform_config = None
        self.json_path = None
        self.global_settings = None
        self.cluster_space = None
        self.temporal_fs = TemporalFsManager()
        self.ssh_key_manager = SshRsaKeyManager(options)

    def configure(self):
        self.generator_dir = self.__get_generator_folder(self.run_options)
        self.json_path = self.__get_config_path(self.generator_dir)
        configuration = self.__parse_configuration()
        self.global_settings = GlobalClusterSettings(configuration)

        # Parse and process declared packages
        self.__prepare_packages(configuration)
        self.kubespray_config = KubesprayConfiguration(configuration, self.packages)
        self.terraform_config = TerraformConfiguration(configuration, self.packages)
        self.cluster_space = ClusterSpace(self.global_settings.cluster_name, self.generator_dir)

        return self

    def load_ssh(self):
        self.ssh_key_manager.load()

    def __prepare_packages(self, configuration):
        packages_config_node = configuration.get('packages')
        if packages_config_node:
            for package_name, package_node in packages_config_node.items():
                if package_name not in self.packages:
                    package_manager = PackageManager(package_name, package_node, self.temporal_fs, self.generator_dir)
                    package_manager.prepare_content()
                    self.packages[package_name] = package_manager
                else:
                    raise ConfigurationException(f'Package {package_name} is duplicated inside configuration')

    @staticmethod
    def __get_config_path(generator_directory):
        current_dir_path = os.path.join(os.getcwd(), 'k8s-config.json')
        if os.path.isfile(current_dir_path):
            return current_dir_path

        user_path = os.path.join(generator_directory, 'k8s-config.json')
        if os.path.isfile(user_path):
            return user_path

        raise ConfigurationException('No json configuration file present')

    @staticmethod
    def __get_generator_folder(run_options):
        generator_dir = utils.get_optional_arg(run_options, 'generator_dir',
                                               os.path.join(os.path.expanduser('~'), '.k8sgen'))
        if not os.path.exists(generator_dir):
            os.makedirs(generator_dir)
        return generator_dir

    def __parse_configuration(self):
        if self.json_path:
            try:
                with open(self.json_path, 'r') as json_file:
                    return json.load(json_file)
            except ValueError:
                raise ConfigurationException('Cannot load generator configuration')

    def destroy(self):
        self.temporal_fs.cleanup()
