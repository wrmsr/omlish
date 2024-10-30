import time

import tqdm


def _main() -> None:
    for i in tqdm.tqdm(range(10000)):
        time.sleep(.0001)
        print(i)


if __name__ == '__main__':
    _main()
