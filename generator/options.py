import argparse
import os.path


class Options:

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kubernetes for Hetzner Cloud generator')
        self.parser.add_argument('--wrk-space', action="store",
                                 default=os.path.expanduser(os.path.expandvars(b"~/.k8sgen")),
                                 help='Sets the generator scratchpad directory')

    def parse(self, args):
        return self.parser.parse_args(args)
