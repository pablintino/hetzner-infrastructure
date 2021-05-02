import os
import git
import shutil
import logging
import requests
import validators
import giturlparse

from fs import file_utils
from exceptions.exceptions import PackageManagerException, ConfigurationException
from utils import common_start


class PackageManager:
    SUPPORTED_EXTENSIONS = ['zip', 'tar.gz', 'tar']

    __logger = logging.getLogger(__name__)

    def __init__(self, package_name, package_metadata, temporal_fs_manager):

        if not package_name:
            raise ValueError('package_name cannot be null or empty')
        if not package_metadata:
            raise ValueError('package_metadata cannot be null or empty')

        self.temporal_fs_manager = temporal_fs_manager
        self.package_name = package_name
        k8s_folder = file_utils.get_generator_user_path()
        self.content_folder = os.path.join(k8s_folder, 'content')
        self.package_content_path = None

        self.source_url = package_metadata.get('source-url')
        if not validators.url(self.source_url) and not giturlparse.parse(self.source_url).valid:
            raise ConfigurationException(f'{self.package_name} source-url is not a valid URL')
        self.package_version = package_metadata.get('version')
        if not self.package_version:
            raise ConfigurationException(f'{self.package_name} version is empty')

        if not os.path.exists(k8s_folder):
            os.mkdir(self.files_folder)
        if not os.path.exists(self.content_folder):
            os.mkdir(self.content_folder)

    def __build_file_content_folder_path(self, extension):
        return os.path.join(
            self.content_folder, f'{self.package_name}-{self.package_version}.{extension}')

    def __prepare_git_content(self):
        # TODO Manage errors
        target_clone_dir = self.temporal_fs_manager.get_temporal_directory()
        self.package_content_path = self.__build_file_content_folder_path('zip')

        git.Repo.clone_from(self.source_url, target_clone_dir, env=dict(GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa"))
        shutil.make_archive(os.path.splitext(self.package_content_path)[0], 'zip', target_clone_dir)

    def __prepare_http_content(self):
        # TODO Manage errors
        req_result = requests.get(self.source_url)
        extension = PackageManager.__calculate_extension(req_result)
        self.package_content_path = self.__build_file_content_folder_path(extension)
        with open(self.package_content_path, 'wb') as file:
            file.write(req_result.content)

    def prepare_content(self):
        self.package_content_path = self.__check_if_content_present()
        if not self.package_content_path:
            if self.source_url.startswith('git') and self.source_url.endswith('git'):
                self.__prepare_git_content()
            else:
                self.__prepare_http_content()

    def get_content(self):
        if self.package_content_path:
            target_dir = self.temporal_fs_manager.get_temporal_directory()
            try:
                shutil.unpack_archive(self.package_content_path, target_dir)
                target_paths = os.listdir(target_dir)
                common_path = next((file for file in target_paths if common_start(target_paths)), None)
                # If compressed file contains a root folder just remove it and copy content to the temporal root
                if common_path and all(filename.startswith(common_path) for filename in target_paths):
                    file_utils.move_content_to_parent(os.path.join(target_dir, common_path))

            except (ValueError, RuntimeError):
                raise PackageManagerException(f'Cannot extract content from source file {self.package_content_path}')
            return target_dir

        return None

    def __check_if_content_present(self):
        files = [os.path.join(self.content_folder, f) for f in os.listdir(self.content_folder) if
                 os.path.isfile(os.path.join(self.content_folder, f))]

        matched_extension = next((ext for ext in PackageManager.SUPPORTED_EXTENSIONS if self.source_url.endswith(ext)),
                                 None) if not giturlparse.parse(self.source_url).valid else 'zip'
        if matched_extension:
            possible_files = [self.__build_file_content_folder_path(matched_extension)]
        else:
            possible_files = [self.__build_file_content_folder_path(extension) for extension in
                              PackageManager.SUPPORTED_EXTENSIONS]

        matching_files = list(set(files) & set(possible_files))
        if matching_files and len(matching_files) > 1:
            raise PackageManagerException(f'Package {self.package_name} content seems to be duplicated')

        return matching_files[0] if matching_files else None

    @staticmethod
    def __calculate_extension(request_result):
        mime_type = request_result.headers['content-type']
        if mime_type == 'application/zip':
            return 'zip'
        elif mime_type == 'application/x-gtar' or mime_type == 'application/x-tgz' or \
                mime_type == 'application/tar+gzip' or mime_type == 'application/x-gzip':
            return 'tar.gz'
        elif mime_type == 'application/x-tar':
            return 'tar'

        raise PackageManagerException(f'File extension is unsupported {mime_type}')
