import logging
from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context
        self.logger = logging.getLogger(type(self).__name__)

    @abstractmethod
    def run(self):
        """Run the specific command implementation"""
