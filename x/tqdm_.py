import shutil
import sys
import time
import typing as ta

import tqdm


T = ta.TypeVar('T')


def _main() -> None:
    # for i in tqdm.tqdm(range(10000)):
    #     time.sleep(.0001)
    #     # print(i)

    ##

    # def progressbar(iterable, total=None, length=40):
    #     if total is None:
    #         total = len(iterable)
    #     for i, item in enumerate(iterable, start=1):
    #         done = int(length * i / total)
    #         bar = f"[{'█' * done}{'.' * (length - done)}] {i}/{total}"
    #         sys.stdout.write(f'\033[2K\033[G{bar}')  # Clear line and move cursor to start
    #         sys.stdout.flush()
    #         yield item
    #     sys.stdout.write('\n')
    #
    # # Example usage
    # for i in progressbar(range(10000)):
    #     time.sleep(0.0001)

    ##

    def progressbar(
            iterable: ta.Sequence[T],
            *,
            total: int | None = None,
            length: int = 40,
            interval: float = .2,
            no_tty_check: bool = False,
    ) -> ta.Generator[T, None, None]:
        if not no_tty_check and not sys.stdout.isatty():
            yield from iterable
            return

        if total is None:
            total = len(iterable)

        start_time = time.time()
        last_render = 0.

        def render() -> None:
            iter_per_sec = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / iter_per_sec if iter_per_sec > 0 else 0

            done = int(length * i / total)
            bar = f"[{'█' * done}{'.' * (length - done)}]"
            info = f" {i}/{total} | {iter_per_sec:.2f} it/s | {elapsed:.2f}s elapsed | {remaining:.2f}s left"

            sys.stdout.write(f'\033[2K\033[G{bar}{info}')
            sys.stdout.flush()

            nonlocal last_render
            last_render = now

        for i, item in enumerate(iterable, start=1):
            now = time.time()
            elapsed = now - start_time
            if not i or (now - last_render) >= interval:
                render()

            yield item

        render()

        sys.stdout.write('\n')

    # Example usage
    for i in progressbar(range(10000)):
        time.sleep(0.0001)

    ##

    # def progressbar(iterable, total=None, length=None):
    #     if total is None:
    #         total = len(iterable)
    #     if length is None:
    #         term_width = shutil.get_terminal_size((80, 20)).columns
    #         length = term_width - 40  # Reserve space for additional info
    #         length = max(10, length)  # Ensure minimum length
    #
    #     start_time = time.time()
    #
    #     for i, item in enumerate(iterable, start=1):
    #         elapsed = time.time() - start_time
    #         iter_per_sec = i / elapsed if elapsed > 0 else 0
    #         remaining = (total - i) / iter_per_sec if iter_per_sec > 0 else 0
    #
    #         done = int(length * i / total)
    #         bar = f"[{'█' * done}{'.' * (length - done)}]"
    #         info = f"{i}/{total} | {iter_per_sec:.2f} it/s | {elapsed:.2f}s elapsed | {remaining:.2f}s left"
    #
    #         # Align the info to the right of the terminal width
    #         output = f"{bar} {info}".ljust(term_width)
    #
    #         sys.stdout.write(f'\033[2K\033[G{output}')
    #         sys.stdout.flush()
    #         yield item
    #
    #     sys.stdout.write('\n')
    #
    # # Example usage
    # for i in progressbar(range(10000)):
    #     time.sleep(0.0001)

    ##

    # def progressbar(iterable, total=None, length=None):
    #     if total is None:
    #         total = len(iterable)
    #     if length is None:
    #         term_width = shutil.get_terminal_size((80, 20)).columns
    #         length = term_width - 40  # Reserve space for additional info
    #         length = max(10, length)  # Ensure a minimum length
    #
    #     start_time = time.time()
    #
    #     for i, item in enumerate(iterable, start=1):
    #         elapsed = time.time() - start_time
    #         iter_per_sec = i / elapsed if elapsed > 0 else 0
    #         remaining = (total - i) / iter_per_sec if iter_per_sec > 0 else 0
    #
    #         done = int(length * i / total)
    #         bar = f"[{'█' * done}{'.' * (length - done)}]"
    #         info = f"{i}/{total} | {iter_per_sec:.2f} it/s | {elapsed:.2f}s elapsed | {remaining:.2f}s left"
    #
    #         # Create the complete line and right-align the info part
    #         line = f"{bar} {info}".ljust(term_width)
    #
    #         sys.stdout.write(f'\033[2K\033[G{line}')  # Clear line and move to start
    #         sys.stdout.flush()
    #         yield item
    #
    #     sys.stdout.write('\n')
    #
    # # Example usage
    # for i in progressbar(range(10000)):
    #     time.sleep(0.0001)


if __name__ == '__main__':
    _main()
