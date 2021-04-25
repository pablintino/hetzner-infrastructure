import sys
import options


if __name__ == '__main__':
    options = options.Options().parse(sys.argv[1:])
    print(options)
