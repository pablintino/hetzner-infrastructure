import sys
import options
import logging
from generator import exec_command

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    options = options.Options().parse(sys.argv[1:])
    sys.exit(exec_command(options))
