import os

from fs import file_utils


class ClusterSpace:

    CLUSTERS_DIR_PREFIX = 'clusters'

    def __init__(self, cluster_name):
        self.cluster_files_directory = file_utils.get_create_if_not_exists(
            os.path.join(*[file_utils.get_generator_user_path(), ClusterSpace.CLUSTERS_DIR_PREFIX, cluster_name]))
        self.tf_directory = file_utils.get_create_if_not_exists(os.path.join(self.cluster_files_directory, 'terraform'))
