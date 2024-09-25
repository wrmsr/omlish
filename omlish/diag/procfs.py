"""
TODO:
 - dataclasses
"""
import argparse
import logging
import os
import re
import resource
import struct
import sys
import typing as ta

from .. import iterators as it
from .. import lang
from .. import os as oos
from ..formats import json
from .procstats import ProcStats


log = logging.getLogger(__name__)


PidLike = int | str


##


RLIMIT_RESOURCES = {
    getattr(resource, k): k
    for k in dir(resource)
    if k.startswith('RLIMIT_')
}


def parse_size(s: str) -> int:
    if ' ' not in s:
        return int(s)
    us = {'kB': 1024, 'mB': 1024 * 1024}
    v, u = s.split()
    return int(v) * us[u]


class ProcStat(lang.Namespace, lang.Final):
    PID = 0
    COMM = 1
    STATE = 2
    PPID = 3
    PGRP = 4
    SESSION = 5
    TTY_NR = 6
    TPGID = 7
    FLAGS = 8
    MINFLT = 9
    CMINFLT = 10
    MAJFLT = 11
    CMAJFLT = 12
    UTIME = 13
    STIME = 14
    CUTIME = 15
    CSTIME = 16
    PRIORITY = 17
    NICE = 18
    NUM_THREADS = 19
    ITREALVALUE = 20
    STARTTIME = 21
    VSIZE = 22
    RSS = 23
    RSSLIM = 24
    STARTCODE = 25
    ENDCODE = 26
    STARTSTACK = 27
    KSTKESP = 28
    KSTKEIP = 29
    SIGNAL = 30
    BLOCKED = 31
    SIGIGNORE = 32
    SIGCATCH = 33
    WCHAN = 34
    NSWAP = 35
    CNSWAP = 36
    EXIT_SIGNAL = 37
    PROCESSOR = 38
    RT_PRIORITY = 39
    POLICY = 40
    DELAYACCT_BLKIO_TICKS = 41
    GUEST_TIME = 42
    CGUEST_TIME = 43
    START_DATA = 44
    END_DATA = 45
    START_BRK = 46
    ARG_START = 47
    ARG_END = 48
    ENV_START = 49
    ENV_END = 50
    EXIT_CODE = 51


def _check_linux() -> None:
    if sys.platform != 'linux':
        raise OSError


##


def get_process_stats(pid: PidLike = 'self') -> list[str]:
    """http://man7.org/linux/man-pages/man5/proc.5.html -> /proc/[pid]/stat"""

    _check_linux()
    with open(f'/proc/{pid}/stat') as f:
        buf = f.read()
    l, _, r = buf.rpartition(')')
    pid, _, comm = l.partition('(')
    return [pid.strip(), comm, *r.strip().split(' ')]


def get_process_procstats(pid: int | None = None) -> ProcStats:
    st = get_process_stats('self' if pid is None else pid)
    return ProcStats(
        pid=int(st[ProcStat.PID]),

        rss=int(st[ProcStat.RSS]),
    )


##


def get_process_chain(pid: PidLike = 'self') -> list[tuple[int, str]]:
    _check_linux()
    lst = []
    while pid:
        process_stats = get_process_stats(pid)
        lst.append((int(process_stats[ProcStat.PID]), process_stats[ProcStat.COMM]))
        pid = int(process_stats[ProcStat.PPID])
    return lst


def get_process_start_time(pid: PidLike = 'self') -> int:
    """https://stackoverflow.com/questions/2598145/how-to-retrieve-the-process-start-time-or-uptime-in-python"""

    _check_linux()
    hz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    with open('/proc/stat') as f:
        system_stats = f.readlines()
    for line in system_stats:
        if line.startswith('btime'):
            boot_timestamp = int(line.split()[1])
            break
    else:
        raise ValueError
    process_stats = get_process_stats(pid)
    age_from_boot_jiffies = int(process_stats[ProcStat.STARTTIME])
    age_from_boot_timestamp = age_from_boot_jiffies // hz
    return boot_timestamp + age_from_boot_timestamp


def get_process_rss(pid: PidLike = 'self') -> int:
    return int(get_process_stats(pid)[ProcStat.RSS])


def set_process_oom_score_adj(score: str, pid: PidLike = 'self') -> None:
    _check_linux()
    with open(f'/proc/{pid}/oom_score_adj', 'w') as f:
        f.write(str(score))


##


MAP_LINE_RX = re.compile(
    r'^'
    r'(?P<address>[A-Fa-f0-9]+)-(?P<end_address>[A-Fa-f0-9]+)\s+'
    r'(?P<permissions>\S+)\s+'
    r'(?P<offset>[A-Fa-f0-9]+)\s+'
    r'(?P<device>\S+)\s+'
    r'(?P<inode>\d+)\s+'
    r'(?P<path>.*)'
    r'$',
)


def get_process_maps(pid: PidLike = 'self', sharing: bool = False) -> ta.Iterator[dict[str, ta.Any]]:
    """http://man7.org/linux/man-pages/man5/proc.5.html -> /proc/[pid]/maps"""

    _check_linux()
    with open(f'/proc/{pid}/{"smaps" if sharing else "maps"}') as map_file:
        while True:
            line = map_file.readline()
            if not line:
                break
            m = MAP_LINE_RX.match(line)
            if not m:
                raise ValueError(line)
            address = int(m.group('address'), 16)
            end_address = int(m.group('end_address'), 16)
            d = {
                'address': address,
                'end_address': end_address,
                'size': end_address - address,
                'permissions': [x for x in m.group('permissions') if x != '-'],
                'offset': int(m.group('offset'), 16),
                'device': m.group('device'),
                'inode': int(m.group('inode')),
                'path': m.group('path'),
            }
            if sharing:
                s: dict[str, ta.Any] = {}
                while True:
                    line = map_file.readline()
                    k, v = line.split(':')
                    if k.lower() == 'vmflags':
                        break
                    s[k.lower()] = parse_size(v.strip())
                _, v = line.split(':')
                s['vmflags'] = [p for p in [j.strip() for j in v.split(' ')] if p]
                d['sharing'] = s
            yield d


##


PAGEMAP_KEYS = (
    'address',
    'pfn',
    'swap_type',
    'swap_offset',
    'pte_soft_dirty',
    'file_page_or_shared_anon',
    'page_swapped',
    'page_present',
)


def get_process_range_pagemaps(start: int, end: int, pid: PidLike = 'self') -> ta.Iterable[dict[str, int]]:
    """https://www.kernel.org/doc/Documentation/vm/pagemap.txt"""

    _check_linux()
    offset = (start // oos.PAGE_SIZE) * 8
    npages = ((end - start) // oos.PAGE_SIZE)
    size = npages * 8
    with open(f'/proc/{pid}/pagemap', 'rb') as pagemap_file:
        pagemap_file.seek(offset)
        pagemap_buf = pagemap_file.read(size)
    if not pagemap_buf:
        return
    _struct_unpack = struct.unpack
    for pagenum in range(npages):
        [packed] = _struct_unpack('Q', pagemap_buf[pagenum * 8:(pagenum + 1) * 8])
        yield {
            'address': start + (pagenum * oos.PAGE_SIZE),
            'pfn': (packed & ((1 << (54 + 1)) - 1)),
            'swap_type': (packed & ((1 << (4 + 1)) - 1)),
            'swap_offset': (packed & ((1 << (54 + 1)) - 1)) >> 5,
            'pte_soft_dirty': ((packed >> 55) & 1) > 0,
            'file_page_or_shared_anon': ((packed >> 61) & 1) > 0,
            'page_swapped': ((packed >> 62) & 1) > 0,
            'page_present': ((packed >> 63) & 1) > 0,
        }


def get_process_pagemaps(pid: PidLike = 'self') -> ta.Iterable[dict[str, int]]:
    _check_linux()
    for m in get_process_maps(pid):
        yield from get_process_range_pagemaps(m['address'], m['end_address'], pid)


##


def _dump_cmd(args: ta.Any) -> None:
    total = 0
    dirty_total = 0
    for m in get_process_maps(args.pid, sharing=True):
        total += m['sharing']['rss']
        sys.stdout.write(json.dumps({'map': m}))
        sys.stdout.write('\n')
        for pm in get_process_range_pagemaps(m['address'], m['end_address'], args.pid):
            if pm['pte_soft_dirty']:
                dirty_total += oos.PAGE_SIZE
            sys.stdout.write(json.dumps({'page': tuple(pm[k] for k in PAGEMAP_KEYS)}))
            sys.stdout.write('\n')
    dct = {
        'total': total,
        'dirty_total': dirty_total,
    }
    sys.stdout.write(json.dumps(dct))
    sys.stdout.write('\n')


def _cmp_cmd(args: ta.Any) -> None:
    if len(args.pids) == 1:
        [rpid] = args.pids
        lpid = get_process_chain(rpid)[1][0]
    elif len(args.pids) == 2:
        lpid, rpid = args.pids
    else:
        raise TypeError('Invalid arguments')

    def g(pid: int) -> ta.Iterator[dict[str, int]]:
        for m in get_process_maps(pid, sharing=True):
            yield from get_process_range_pagemaps(m['address'], m['end_address'], pid)

    lpms, rpms = (g(pid) for pid in (lpid, rpid))

    l_pages = 0
    r_pages = 0
    c_pages = 0
    for _, ps in it.merge_on(lambda pm: pm['address'], lpms, rpms):
        l, r = it.expand_indexed_pairs(ps, None, width=2)
        if l is not None and r is None:
            l_pages += 1
        elif l is None and r is not None:
            r_pages += 1
        elif l['pfn'] != r['pfn']:  # type: ignore
            c_pages += 1
        else:
            continue
        if not args.quiet:
            sys.stdout.write(json.dumps([l, r]))
            sys.stdout.write('\n')
    l_pages += c_pages
    r_pages += c_pages
    dct = {
        'l_pages': l_pages,
        'l_bytes': l_pages * oos.PAGE_SIZE,
        'r_pages': r_pages,
        'r_bytes': r_pages * oos.PAGE_SIZE,
        'c_pages': c_pages,
        'c_bytes': c_pages * oos.PAGE_SIZE,
    }
    sys.stdout.write(json.dumps(dct))
    sys.stdout.write('\n')


def _main() -> None:
    _check_linux()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-q', '--quiet', action='store_true')
    arg_subparsers = arg_parser.add_subparsers()

    dump_arg_parser = arg_subparsers.add_parser('dump')
    dump_arg_parser.add_argument('pid', type=int)
    dump_arg_parser.set_defaults(func=_dump_cmd)

    cmp_arg_parser = arg_subparsers.add_parser('cmp')
    cmp_arg_parser.add_argument('pids', type=int, nargs='*')
    cmp_arg_parser.set_defaults(func=_cmp_cmd)

    args = arg_parser.parse_args()
    if not hasattr(args, 'func'):
        arg_parser.print_help()
    else:
        args.func(args)


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'procfs',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    _main()
