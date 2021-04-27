import argparse
import os.path


class Options:

    COMMAND_CREATE = 'create'

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kubernetes for Hetzner Cloud generator', prog='k8sgen')
        self.parser.add_argument('--foo', action='store_true', help='foo help')
        subparsers = self.parser.add_subparsers(help='sub-command help', dest='command')

        # create the parser for the "command_a" command
        parser_a = subparsers.add_parser(Options.COMMAND_CREATE, help='Creates a new cluster')
        parser_a.add_argument('bar', type=int, help='bar help')

    def parse(self, args):
        return self.parser.parse_args(args)
