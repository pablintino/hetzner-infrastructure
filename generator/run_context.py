import os
import json
import logging

import validators

from exceptions.exceptions import ConfigurationException
from package_manager import PackageManager


class KubesprayConfiguration:

    def __init__(self, config_dict):

        if 'kubespray' in config_dict:
            self.source_url = config_dict['kubespray'].get('source-url')
            if not validators.url(self.source_url):
                raise ConfigurationException('Kubespray source-url is not a valid URL')

            self.remote_user = config_dict['kubespray'].get('remote-user')
            self.version = config_dict['kubespray'].get('version')
            self.patches_dir = config_dict['kubespray'].get('patches-dir')
        else:
            raise ConfigurationException('Not Kubespray configuration found in generator configuration')


class RunContext:
    __logger = logging.getLogger(__name__)

    def __init__(self, options):
        self.run_options = options
        self.json_path = self.__get_config_path()
        configuration = self.__parse_configuration()
        self.kubespray_config = KubesprayConfiguration(configuration)
        self.package_manager = PackageManager(self)
        self.package_manager.prepare_content()

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
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
                raise ConfigurationException('Cannot load generator configuration')
        else:
            raise ConfigurationException('No json configuration file present')

    def destroy(self):
        self.package_manager.clean()

