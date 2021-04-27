import sys
import options
from generator import exec_command

if __name__ == '__main__':
    options = options.Options().parse(sys.argv[1:])
    sys.exit(exec_command(options))
