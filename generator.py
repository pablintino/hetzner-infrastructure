import os
import logging
from commands.terraform_based_commands import CreateClusterCommand, DestroyClusterCommand
from exceptions.exceptions import ConfigurationException, SSHKeysException
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


def prepare_requirements(command, context):
    if command.requires_ssh:
        context.load_ssh()

    for validator in command.context_validators:
        validator(context).validate()


def exec_command(options):
    try:
        run_context = RunContext(options)
        run_context.configure()
        if options.command in command_registry:
            command_instance = command_registry[options.command](run_context)
            prepare_requirements(command_instance, run_context)
            command_instance.run()
        else:
            logger.error('Unrecognised command')
            return os.EX_USAGE

    except (ConfigurationException, SSHKeysException) as ex:
        logger.error(ex)
        return os.EX_USAGE
    finally:
        run_context.destroy()


__register_command(Options.COMMAND_CREATE, CreateClusterCommand)
__register_command(Options.COMMAND_DESTROY, DestroyClusterCommand)
