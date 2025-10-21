import argparse


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('profile')
    args, argv = parser.parse_known_args()

    print(f'{args=} {argv=}')


if __name__ == '__main__':
    _main()
