import logging

__logger = logging.getLogger(__name__)


def create_cluster_command(context):
    __logger.info('Call logger')
    temporal_content = context.terraform_config.package_manager.get_content()
    __logger.info(temporal_content)
