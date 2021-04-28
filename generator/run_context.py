import os
import json
import logging

from exceptions.exceptions import ConfigurationException
from package_manager import PackageManager


class KubesprayConfiguration:

    def __init__(self, config_dict, packages):
        if 'kubespray' in config_dict:
            self.remote_user = config_dict['kubespray'].get('remote-user')
            self.patches_dir = config_dict['kubespray'].get('patches-dir')
            self.package_name = config_dict['kubespray'].get('package')
            self.package_manager = packages[self.package_name] if self.package_name in packages else None
            if not self.package_manager:
                raise ConfigurationException('Kubespray configuration has an invalid package association')

        else:
            raise ConfigurationException('Not Kubespray configuration found in generator configuration')


class RunContext:
    __logger = logging.getLogger(__name__)

    def __init__(self, options):
        self.run_options = options
        self.packages = {}
        self.kubespray_config = None
        self.json_path = None

    def configure(self):
        self.json_path = self.__get_config_path()
        configuration = self.__parse_configuration()

        # Parse and process declared packages
        self.__prepare_packages(configuration)
        self.kubespray_config = KubesprayConfiguration(configuration, self.packages)

    def __prepare_packages(self, configuration):
        packages_config_node = configuration.get('packages')
        if packages_config_node:
            for package_name, package_node in packages_config_node.items():
                if package_name not in self.packages:
                    package_manager = PackageManager(package_name, package_node)
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
        return user_path if os.path.isfile(user_path) else None

    def __parse_configuration(self):
        if self.json_path:
            try:
                with open(self.json_path, 'r') as json_file:
                    return json.load(json_file)
            except ValueError:
                raise ConfigurationException('Cannot load generator configuration')
        else:
            raise ConfigurationException('No json configuration file present')

    def destroy(self):
        for pm_name, pm in self.packages.items():
            try:
                pm.clean()
            except Exception:
                self.__logger.error(f'Failed to clean {pm_name} resources')
