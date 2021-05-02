import os
import logging

import commands.create_cluster_command
import commands.destroy_cluster_command
from exceptions.exceptions import ConfigurationException
from options import Options
from run_context import RunContext

logger = logging.getLogger(__name__)

command_registry = {}


def __register_command(command_name, command):
    if not command_name or not command:
        raise ValueError('command_name nor command can be null')

    if command_name in command_registry:
        raise ValueError('command already registered')

    command_registry[command_name] = command


def exec_command(options):
    try:
        run_context = RunContext(options)
        run_context.configure()
        if options.command in command_registry:
            return command_registry[options.command](run_context)
        else:
            logger.error('Unrecognised command')
            return os.EX_USAGE

    except ConfigurationException as ex:
        logger.error(ex)
        return os.EX_USAGE
    finally:
        run_context.destroy()


__register_command(Options.COMMAND_CREATE, commands.create_cluster_command.create_cluster_command)
__register_command(Options.COMMAND_DESTROY, commands.destroy_cluster_command.destroy_cluster_command)
