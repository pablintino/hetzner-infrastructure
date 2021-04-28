import os
import shutil
import zipfile
import logging
import tempfile
import requests
import validators

from exceptions.exceptions import PackageManagerException, ConfigurationException
from utils import common_start


class PackageManager:
    SUPPORTED_EXTENSIONS = ['zip', 'tar.gz']

    __logger = logging.getLogger(__name__)

    def __init__(self, package_name, package_metadata):
        self.temporal_dirs = []
        if not package_name:
            raise ValueError('package_name cannot be null or empty')
        if not package_metadata:
            raise ValueError('package_metadata cannot be null or empty')

        self.package_name = package_name
        self.k8s_folder = os.path.join(os.path.expanduser('~'), '.k8sgen')
        self.content_folder = os.path.join(self.k8s_folder, 'content')

        self.source_url = package_metadata.get('source-url')
        if not validators.url(self.source_url):
            raise ConfigurationException(f'{self.package_name} source-url is not a valid URL')
        self.package_version = package_metadata.get('version')
        if not self.package_version:
            raise ConfigurationException(f'{self.package_name} version is empty')

        if not os.path.exists(self.k8s_folder):
            os.mkdir(self.files_folder)
        if not os.path.exists(self.content_folder):
            os.mkdir(self.content_folder)

        self.package_content_path = None

    def prepare_content(self):
        self.package_content_path = self.__check_if_content_present()
        if not self.package_content_path:
            # TODO Manage errors
            req_result = requests.get(self.source_url)
            extension = PackageManager.__calculate_extension(req_result)

            # TODO Hardcoded name is duplicated
            self.package_content_path = os.path.join(self.content_folder,
                                                     f'{self.package_name}-{self.package_version}.{extension}')

            with open(self.package_content_path, 'wb') as file:
                file.write(req_result.content)

    def __check_if_content_present(self):
        files = [os.path.join(self.content_folder, f) for f in os.listdir(self.content_folder) if
                 os.path.isfile(os.path.join(self.content_folder, f))]

        # TODO Hardcoded name is duplicated
        possible_files = [os.path.join(self.content_folder, f'{self.package_name}-{self.package_version}.{extension}')
                          for
                          extension in PackageManager.SUPPORTED_EXTENSIONS]
        matching_files = list(set(files) & set(possible_files))
        if matching_files and len(matching_files) > 1:
            raise PackageManagerException(f'Package {self.package_name} content seems to be duplicated')

        return matching_files[0] if matching_files else None

    @staticmethod
    def __calculate_extension(request_result):
        mime_type = request_result.headers['content-type']
        if mime_type == 'application/zip':
            return 'zip'
        elif mime_type == 'application/x-gtar' or mime_type == 'application/x-tgz' or mime_type == 'application/tar+gzip':
            return 'tar.gz'

        raise PackageManagerException(f'File extension is unsupported {mime_type}')

    def get_content(self):
        if self.package_content_path:
            target_dir = tempfile.TemporaryDirectory()
            try:
                with zipfile.ZipFile(self.package_content_path, 'r') as zip_ref:
                    common_path = next(file.filename for file in zip_ref.filelist if
                                       common_start([file.filename for file in zip_ref.filelist]))
                    zip_ref.extractall(target_dir.name)
                    # If ZIP contains a root folder just remove it and copy content to the temporal root
                    if all(file_info.filename.startswith(common_path) for file_info in zip_ref.filelist):
                        for filename in os.listdir(os.path.join(target_dir.name, common_path)):
                            shutil.move(os.path.join(target_dir.name, common_path, filename),
                                        os.path.join(target_dir.name, filename))
                        os.rmdir(os.path.join(target_dir.name, common_path))

            except (ValueError, RuntimeError) as err:
                raise PackageManagerException(f'Cannot extract content from source file {self.package_content_path}')
            finally:
                self.temporal_dirs.append(target_dir)
            return target_dir.name

        return None

    def clean(self):
        for temp_dir in self.temporal_dirs:
            temp_dir.cleanup()
