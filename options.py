import argparse


class Options:
    COMMAND_CREATE = 'create'
    COMMAND_DESTROY = 'destroy'

    @staticmethod
    def __add_common_ssh_options(parser):
        parser.add_argument('--rsa-private-key', dest='pk_rsa_key', type=str, help='Private SSH RSA key')
        parser.add_argument('--rsa-key', dest='pub_rsa_key', type=str, help='Public SSH RSA key')
        parser.add_argument('--rsa-passphrase', dest='pk_passphrase', type=str, help='Private SSH RSA key Passphrase')
        parser.add_argument('--remote-user', dest='remote_user', type=str,
                            help='User to be used to connect to to remote')

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kubernetes for Hetzner Cloud generator', prog='k8sgen')
        self.parser.add_argument('--generator-dir', dest='generator_dir', type=str,
                                 help='Generator state/packages directory')

        subparsers = self.parser.add_subparsers(help='sub-command help', dest='command')

        # create the parser for the "command_a" command
        create_cluster_parser = subparsers.add_parser(Options.COMMAND_CREATE, help='Creates a new cluster')
        self.__add_common_ssh_options(create_cluster_parser)

        destroy_cluster_parser = subparsers.add_parser(Options.COMMAND_DESTROY, help='Destroys the cluster')
        self.__add_common_ssh_options(destroy_cluster_parser)
        destroy_cluster_parser.add_argument('--confirm', type=bool, nargs='?', const=True, default=False,
                                            help='Destroy command confirmation flag')

    def parse(self, args):
        return self.parser.parse_args(args)
