import os
import requests
import ntpath
from exceptions.exceptions import PackageManagerExpcetion


class PackageManager:
    SUPPORTED_EXTENSIONS = ['zip', 'tar.gz']

    def __init__(self, context):
        self.context = context
        self.k8s_folder = os.path.join(os.path.expanduser('~'), '.k8sgen')
        self.content_folder = os.path.join(self.k8s_folder, 'content')

        if not os.path.exists(self.k8s_folder):
            os.mkdir(self.files_folder)
        if not os.path.exists(self.content_folder):
            os.mkdir(self.content_folder)

    def prepare_content(self):
        if not self.__check_if_content_present():
            # TODO Manage errors
            req_result = requests.get(self.context.kubespray_config.source_url)
            extension = PackageManager.__calculate_extension(req_result)

            # TODO Hardcoded name is duplicated
            with open(os.path.join(self.content_folder,
                                   f'kubespray-source-{self.context.kubespray_config.version}.{extension}'), 'wb') as f:
                f.write(req_result.content)

    def __check_if_content_present(self):
        files = [ntpath.basename(f) for f in os.listdir(self.content_folder) if
                 os.path.isfile(os.path.join(self.content_folder, f))]

        # TODO Hardcoded name is duplicated
        possible_files = [f'kubespray-source-{self.context.kubespray_config.version}.{extension}' for
                          extension in PackageManager.SUPPORTED_EXTENSIONS]

        return len(list(set(files) & set(possible_files))) == 1

    @staticmethod
    def __calculate_extension(request_result):
        mime_type = request_result.headers['content-type']
        if mime_type == 'application/zip':
            return 'zip'
        elif mime_type == 'application/x-gtar' or mime_type == 'application/x-tgz' or mime_type == 'application/tar+gzip':
            return 'tar.gz'

        raise PackageManagerExpcetion(f'File extension is unsupported {mime_type}')

    def clean(self):
        pass
