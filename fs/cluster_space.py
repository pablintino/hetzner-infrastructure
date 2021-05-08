import os
import shutil

from fs import file_utils


class ClusterSpace:
    CLUSTERS_DIR_PREFIX = 'clusters'

    def __init__(self, cluster_name):
        self.cluster_files_directory = file_utils.get_create_dir_if_not_exists(
            os.path.join(*[file_utils.get_generator_user_path(), ClusterSpace.CLUSTERS_DIR_PREFIX, cluster_name]))
        self.kubectl_file = os.path.join(self.cluster_files_directory, 'admin.conf')
        self.tf_directory = file_utils.get_create_dir_if_not_exists(
            os.path.join(self.cluster_files_directory, 'terraform'))
        self.tf_plugins_directory = file_utils.get_create_dir_if_not_exists(os.path.join(self.tf_directory, 'plugins'))
        self.tf_state_file = os.path.join(self.tf_directory, 'terraform.tfstate')

    def destroy_cluster_space(self):
        shutil.rmtree(self.cluster_files_directory)