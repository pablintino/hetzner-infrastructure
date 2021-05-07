import argparse


class Options:
    COMMAND_CREATE = 'create'
    COMMAND_DESTROY = 'destroy'

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kubernetes for Hetzner Cloud generator', prog='k8sgen')
        subparsers = self.parser.add_subparsers(help='sub-command help', dest='command')

        # create the parser for the "command_a" command
        parser_a = subparsers.add_parser(Options.COMMAND_CREATE, help='Creates a new cluster')
        parser_a.add_argument('--rsa-private-key', dest='pk_rsa_key', type=str, help='Private SSH RSA key')
        parser_a.add_argument('--rsa-key', dest='pub_rsa_key', type=str, help='Public SSH RSA key')
        parser_a.add_argument('--rsa-passphrase', dest='pk_passphrase', type=str, help='Private SSH RSA key Passphrase')
        parser_a.add_argument('--remote-user', dest='remote_user', type=str,
                              help='User to be used to connect to to remote')

        parser_b = subparsers.add_parser(Options.COMMAND_DESTROY, help='Destroy the cluster')

    def parse(self, args):
        return self.parser.parse_args(args)
