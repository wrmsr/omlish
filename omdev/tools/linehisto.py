"""
TODO:
 - cmd line options
 - truncation
 - mean/min/max/median/stddev
 - delta mean/min/max/median/stddev
 - heat - red rapidly changing blue stale
 - paging
 - find
 - stdin/stdout redir (ttyname(0))
 - graph
"""
import curses
import heapq
import operator
import sys
import time
import typing as ta

from ..cli import CliModule


##


def with_timer(interval=5.):
    def outer(fn):
        start = time.time()
        last = start

        def inner(*args, **kwargs):
            nonlocal last

            now = time.time()
            if (now - last) < interval:
                return None

            last = now
            return fn(*args, **kwargs)

        return inner

    return outer


def calc_percent(a: float, b: float) -> float:
    if not a or not b:
        return 0.
    return ((a * 1e9) // (b * 1e5)) / 100.


##


class KeyedHisto:
    def __init__(
            self,
            *,
            max_entries: int | None = None,
    ) -> None:
        super().__init__()

        self.entries: dict[str, int] = {}
        self.total_seen = 0
        self.total_evicted = 0

        self.max_entries = max_entries
        if max_entries is not None:
            self.eviction_len = int(max_entries * 2)

        self.num_evicted = 0

    def __len__(self) -> int:
        return len(self.entries)

    @property
    def total_tracked(self) -> int:
        return self.total_seen - self.total_evicted

    def inc(self, key: str, n: int = 1) -> int:
        if self.max_entries is not None and len(self) >= self.eviction_len:
            self.evict(len(self) - self.max_entries)

        self.total_seen += n

        ct = self.entries.get(key, 0) + n
        self.entries[key] = ct

        return ct

    @property
    def items(self) -> ta.Iterable[tuple[str, int]]:
        return self.entries.items()

    @property
    def sorted(self) -> list[tuple[str, int]]:
        items = sorted(self.items, key=operator.itemgetter(1))
        return items[::-1]

    def evict(self, n: int = 1) -> None:
        self.num_evicted += n

        for key, ct in heapq.nsmallest(n, self.items, key=operator.itemgetter(1)):
            self.total_evicted += ct

            del self.entries[key]

    def nlargest(self, n: int = 20) -> list[tuple[str, int]]:
        return heapq.nlargest(n, self.items, key=operator.itemgetter(1))

    def nsmallest(self, n: int = 20) -> list[tuple[str, int]]:
        return heapq.nsmallest(n, self.items, key=operator.itemgetter(1))


class KeyedHistoRenderer:
    def __init__(
            self,
            histo: KeyedHisto,
            *,
            max_lines: int | None = None,
    ) -> None:
        super().__init__()

        self.histo = histo
        self.max_lines = max_lines

    @property
    def entries_to_render(self) -> list[tuple[str, int]]:
        if self.max_lines is None:
            return list(self.histo.sorted)

        nlines = min(self.max_lines, len(self.histo))

        return self.histo.nlargest(nlines)

    def render_header(self, count_width: int) -> str:
        header = 'count : % sen : % tkd : line'

        if count_width > 5:
            header = (' ' * (count_width - 5)) + header

        return header

    def render_entry(self, entry: tuple[str, int], count_width: int) -> str:
        line, count = entry

        line_fmt = '%' + str(count_width) + 'd : %5s : %5s : %s'

        percent_seen_str = f'{calc_percent(count, self.histo.total_seen):3.2f}'
        percent_tracked_str = f'{calc_percent(count, self.histo.total_tracked):3.2f}'

        return line_fmt % (count, percent_seen_str, percent_tracked_str, line)

    def render_entries(self, entries: ta.Iterable[tuple[str, int]], count_width: int) -> list[str]:
        return [self.render_entry(entry, count_width) for entry in entries]

    def render_status(self) -> str:
        parts = [f'{self.histo.total_seen} total seen']

        total_tracked_percent = calc_percent(self.histo.total_tracked, self.histo.total_seen)
        parts.extend([
            f'{len(self.histo)} tracked',
            f'{self.histo.total_tracked} / {total_tracked_percent:.2f} % total tracked',
        ])

        parts.extend([
            f'{self.histo.num_evicted} evicted',
            f'{self.histo.total_evicted} / {100.0 - total_tracked_percent:.2f} % total evicted',
        ])

        duplicate_evictions = self.histo.total_evicted - self.histo.num_evicted
        parts.append(
            f'{duplicate_evictions} / {calc_percent(duplicate_evictions, self.histo.total_evicted):.2f} '
            f'% duplicate evictions',
        )

        # tracked % + duplicate evicted %
        parts.append(
            f'{calc_percent(self.histo.total_tracked - duplicate_evictions, self.histo.total_seen):.2f} % correct',
        )

        return ', '.join(parts)

    class Rendered(ta.NamedTuple):
        status_line: str
        header_line: str
        entry_lines: list[str]

    def render(self, entries: ta.Sequence[tuple[str, int]] | None = None) -> Rendered:
        if entries is None:
            entries = self.entries_to_render

        max_count = entries[0][1] if entries else 0
        count_width = len(str(max_count))

        status_line = self.render_status()
        header_line = self.render_header(count_width)
        entry_lines = self.render_entries(entries, count_width)

        return self.Rendered(
            status_line,
            header_line,
            entry_lines,
        )

    def render_to_str(self) -> str:
        status_line, header_line, entry_lines = self.render()

        return '\n'.join([status_line, '', header_line, *entry_lines, ''])


class CursesKeyedHistoRenderer(KeyedHistoRenderer):
    color_normal = 0
    color_green = 1
    color_yellow = 2
    color_red = 3

    def __init__(
            self,
            window,
            histo: KeyedHisto,
            *,
            redraw_interval: float = .1,
    ) -> None:
        self.window = window
        self.redraw_interval = redraw_interval

        h, w = self.window.getmaxyx()
        max_lines = h - 3

        self.max_line_len = w - 30

        super().__init__(
            histo,
            max_lines=max_lines,
        )

        self.timed_redraw = with_timer(redraw_interval)(self.draw)

        self.last_drawn_entries: list[tuple[str, int]] = []

        curses.init_pair(self.color_green, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.color_yellow, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.color_red, curses.COLOR_RED, curses.COLOR_BLACK)

    def get_entry_color(
            self,
            cur_pos: int,
            last_pos: int | None,
    ) -> int:
        if last_pos is None:
            return self.color_green
        elif last_pos > cur_pos:
            return self.color_yellow
        elif last_pos < cur_pos:
            return self.color_red
        else:
            return self.color_normal

    def get_entry_colors(self, entries: ta.Iterable[tuple[str, int]]) -> list[int]:
        last_pos_map = {s: i for i, (s, _) in enumerate(self.last_drawn_entries)}

        return [
            self.get_entry_color(i, last_pos_map.get(key))
            for i, (key, _) in enumerate(entries)
        ]

    def draw(self) -> None:
        entries = self.entries_to_render

        status_line, header_line, entry_lines = self.render(entries)
        entry_colors = self.get_entry_colors(entries)

        self.last_drawn_entries = entries

        self.window.clear()
        self.window.addstr(0, 0, status_line)
        self.window.addstr(2, 0, header_line)

        for i, (line, color) in enumerate(zip(entry_lines, entry_colors)):
            self.window.addstr(i + 3, 0, line[:120], curses.color_pair(color))

        self.window.refresh()


def main() -> None:
    screen = curses.initscr()
    curses.start_color()
    curses.curs_set(0)

    histo = KeyedHisto(max_entries=10_000)
    renderer = CursesKeyedHistoRenderer(screen, histo)

    try:
        while True:
            try:
                line = sys.stdin.readline()
            except UnicodeDecodeError:
                # FIXME
                continue

            if not line:
                break

            if len(line) > renderer.max_line_len:
                line = line[renderer.max_line_len:]

            line = line.strip()

            if not line:
                continue

            histo.inc(line)
            renderer.timed_redraw()

            # screen.nodelay(1)
            # ch = screen.getch()
            # if ch != curses.ERR:
            #     histo.inc(ch, 100)

    except (OSError, KeyboardInterrupt):
        pass

    finally:
        curses.endwin()

        sys.stdout.write(KeyedHistoRenderer(histo).render_to_str())


# @omlish-manifest
_CLI_MODULE = CliModule('linehisto', __name__)


if __name__ == '__main__':
    main()
