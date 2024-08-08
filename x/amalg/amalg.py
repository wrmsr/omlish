import os.path


def _main() -> None:
    root_dir = os.path.dirname(__file__)
    with open(os.path.join(root_dir, 'demo/demo.py')) as f:
        src = f.read()
    print(src)


if __name__ == '__main__':
    _main()
