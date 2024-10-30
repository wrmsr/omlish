import sys
import time

import tqdm


def _main() -> None:
    for i in tqdm.tqdm(range(10000)):
        time.sleep(.0001)
        # print(i)

    ##

    def progressbar(iterable, total=None, length=40):
        if total is None:
            total = len(iterable)
        for i, item in enumerate(iterable, start=1):
            done = int(length * i / total)
            bar = f"[{'█' * done}{'.' * (length - done)}] {i}/{total}"
            sys.stdout.write(f'\033[2K\033[G{bar}')  # Clear line and move cursor to start
            sys.stdout.flush()
            yield item
        sys.stdout.write('\n')

    # Example usage
    for i in progressbar(range(10000)):
        time.sleep(0.0001)

    ##

    def progressbar(iterable, total=None, length=40):
        if total is None:
            total = len(iterable)
        start_time = time.time()

        for i, item in enumerate(iterable, start=1):
            elapsed = time.time() - start_time
            iter_per_sec = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / iter_per_sec if iter_per_sec > 0 else 0

            done = int(length * i / total)
            bar = f"[{'█' * done}{'.' * (length - done)}]"
            info = f" {i}/{total} | {iter_per_sec:.2f} it/s | {elapsed:.2f}s elapsed | {remaining:.2f}s left"

            sys.stdout.write(f'\033[2K\033[G{bar}{info}')
            sys.stdout.flush()
            yield item

        sys.stdout.write('\n')

    # Example usage
    for i in progressbar(range(10000)):
        time.sleep(0.0001)


if __name__ == '__main__':
    _main()
