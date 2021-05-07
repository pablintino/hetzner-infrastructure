import logging
from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):
    def __init__(self, context, requires_ssh=True, context_validators=None):
        self.context = context
        self.logger = logging.getLogger(type(self).__name__)
        self.requires_ssh = requires_ssh
        self.context_validators = [] if not context_validators else context_validators

    @abstractmethod
    def run(self):
        """Run the specific command implementation"""
