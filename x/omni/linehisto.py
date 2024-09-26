"""
TODO:
 - hey cmd line options
 - truncation
 - mean/min/max/median/stddev
 - DELTA mean/min/max/median/stddev
 - HEAT - red rapidly changing blue stale
 - paging
 - find
 - stdin/stdout redir (ttyname(0))
 - graph
 - COLUMNS ARE CLASSES. TRANSFORMS. CONFIGURABLE. PIPELINE. .....

(for l in $(cat attic/scratch/linehisto.py | tr ' ' '\n' | egrep -v "^$") ; do echo $l ; sleep 0.01 ; done) | \
  ./python attic/scratch/linehisto.py
"""
import curses
import datetime
import heapq
import sys


def get_total_milliseconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e3


def with_timer(interval=5000):
    def outer(fn):
        def inner(*args, **kwargs):
            inner.now = datetime.datetime.now()
            if get_total_milliseconds(inner.now - inner.last) < interval:
                return None

            inner.last = inner.now
            return fn(*args, **kwargs)

        inner.start = datetime.datetime.now()
        inner.last = inner.start
        return inner

    return outer


def flip2(seq):
    return ((b, a) for a, b in seq)


def fst(seq):
    return seq[0]


class KeyedHisto:

    def __init__(self, max_entries=None):
        self.entries = {}
        self.total_seen = 0
        self.total_evicted = 0

        self.max_entries = max_entries
        if max_entries is not None:
            self.eviction_len = int(self.max_entries * 2)

        self.num_evicted = 0

    def __len__(self):
        return len(self.entries)

    @property
    def total_tracked(self):
        return self.total_seen - self.total_evicted

    def inc(self, key, n=1):
        if self.max_entries is not None and len(self) >= self.eviction_len:
            self.evict(len(self) - self.max_entries)

        self.total_seen += n

        ct = self.entries.get(key, 0) + n
        self.entries[key] = ct

        return ct

    @property
    def items(self):
        return self.entries.items()

    @property
    def sorted(self):
        items = sorted(flip2(self.items))

        return flip2(items[::-1])

    def evict(self, n=1):
        self.num_evicted += n

        for ct, key in heapq.nsmallest(n, flip2(self.items)):
            self.total_evicted += ct

            del self.entries[key]

    def nlargest(self, n=20):
        entries = heapq.nlargest(n, flip2(self.items))
        return list(flip2(entries))

    def nsmallest(self, n=20):
        entries = heapq.nsmallest(n, flip2(self.items))
        return list(flip2(entries))


def calc_percent(a, b):
    if not a or not b:
        return 0.0
    return ((a * 1e9) // (b * 1e5)) / 100.0


class KeyedHistoRenderer:

    def __init__(self, histo, max_lines=None):
        self.histo = histo
        self.max_lines = max_lines

    @property
    def entries_to_render(self):
        if self.max_lines is None:
            return list(self.histo.sorted)

        nlines = min(self.max_lines, len(self.histo))

        return self.histo.nlargest(nlines)

    def render_header(self, count_width):
        header = 'count : % sen : % tkd : line'

        if count_width > 5:
            header = (' ' * (count_width - 5)) + header

        return header

    def render_entry(self, entry, count_width):
        line, count = entry

        line_fmt = '%' + str(count_width) + 'd : %5s : %5s : %s'

        percent_seen_str = '%3.2f' % (calc_percent(count, self.histo.total_seen))
        percent_tracked_str = '%3.2f' % (calc_percent(count, self.histo.total_tracked))

        return line_fmt % (count, percent_seen_str, percent_tracked_str, line)

    def render_entries(self, entries, count_width):
        return [self.render_entry(entry, count_width) for entry in entries]

    def render_status(self, entries):
        status = '%d total seen' % (self.histo.total_seen,)

        total_tracked_percent = calc_percent(self.histo.total_tracked, self.histo.total_seen)

        status += ', %d tracked, %d / %.2f %% total tracked' % \
            (len(self.histo), self.histo.total_tracked, total_tracked_percent)

        status += ', %d evicted, %d / %.2f %% total evicted' % \
            (self.histo.num_evicted, self.histo.total_evicted, 100.0 - total_tracked_percent)

        duplicate_evictions = self.histo.total_evicted - self.histo.num_evicted

        status += ', %d / %.2f %% duplicate evictions' % \
            (duplicate_evictions, calc_percent(duplicate_evictions, self.histo.total_evicted))

        # tracked % + duplicate evicted %
        status += ', %.2f %% correct' % (calc_percent(self.histo.total_tracked - duplicate_evictions, self.histo.total_seen))  # noqa

        return status

    def render(self, entries=None):
        if entries is None:
            entries = self.entries_to_render

        max_count = entries[0][1] if entries else 0
        count_width = len(str(max_count))

        status_line = self.render_status(entries)
        header_line = self.render_header(count_width)
        entry_lines = self.render_entries(entries, count_width)

        return status_line, header_line, entry_lines

    def render_to_str(self):
        status_line, header_line, entry_lines = self.render()

        return '\n'.join([status_line, '', header_line] + entry_lines) + '\n'


class CursesKeyedHistoRenderer(KeyedHistoRenderer):
    color_normal = 0
    color_green = 1
    color_yellow = 2
    color_red = 3

    def __init__(self, window, histo, redraw_interval=100):
        self.window = window
        self.redraw_interval = redraw_interval

        h, w = self.window.getmaxyx()
        max_lines = h - 3

        self.max_line_len = w - 30

        super().__init__(histo, max_lines)

        self.timed_redraw = with_timer(redraw_interval)(self.draw)

        self.last_drawn_entries = []

        curses.init_pair(self.color_green, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.color_yellow, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.color_red, curses.COLOR_RED, curses.COLOR_BLACK)

    def get_entry_color(self, cur_pos, last_pos):
        if last_pos is None:
            return self.color_green
        elif last_pos > cur_pos:
            return self.color_yellow
        elif last_pos < cur_pos:
            return self.color_red
        else:
            return self.color_normal

    def get_entry_colors(self, entries):
        last_pos_map = dict(flip2(enumerate(map(fst, self.last_drawn_entries))))

        return [
            self.get_entry_color(i, last_pos_map.get(key))
            for i, key in enumerate(map(fst, entries))
        ]

    def draw(self):
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


def main():
    screen = curses.initscr()
    curses.start_color()
    curses.curs_set(0)

    histo = KeyedHisto(max_entries=10000)
    renderer = CursesKeyedHistoRenderer(screen, histo, redraw_interval=250)

    try:
        while True:
            line = sys.stdin.readline()
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

    except (IOError, KeyboardInterrupt):
        pass

    finally:
        curses.endwin()

        try:
            sys.stdout.write(KeyedHistoRenderer(histo).render_to_str())

        except Exception as ex:
            sys.stderr.write(repr(ex) + '\n')


if __name__ == '__main__':
    main()
