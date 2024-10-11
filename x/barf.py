import sys


def _main():
    with open('/proc/self/fd/0', 'w') as f:
        f.write('echo hi\n')


if __name__ == '__main__':
    _main()
