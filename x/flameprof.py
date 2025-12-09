# MIT License
#
# Copyright (c) 2017 Anton Bobrov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR
#
# https://github.com/baverman/flameprof/blob/df94267b78028b88234a64c21d88d046217ba72e/flameprof.py
r"""
TODO:
 - hover / mouseover effect like flamegraph.pl

====

flameprof --format=log prof.pstats | flamegraph.pl > prof.svg && open prof.svg

flameprof --format=svg prof.pstats > prof.svg && open prof.svg
"""
import argparse
import collections
import contextlib
import hashlib
import os.path
import pstats
import struct
import sys
import time
import xml.sax.saxutils


##


DEFAULT_WIDTH = 1200
DEFAULT_ROW_HEIGHT = 24
DEFAULT_FONT_SIZE = 12
DEFAULT_THRESHOLD = 0.1
DEFAULT_FORMAT = 'svg'
DEFAULT_LOG_MULT = 1000000


def bstr(data):
    if type(data) is str:
        data = data.encode('utf-8')
    return data


def ustr(data):
    if type(data) is bytes:
        data = data.decode('latin1')
    return data


def get_profiler(cpu):
    from cProfile import Profile

    if cpu:
        return Profile(time.process_time)
    else:
        return Profile()


@contextlib.contextmanager
def profile(filename, cpu=False):
    p = get_profiler(cpu)
    p.enable()
    try:
        yield
    finally:
        p.disable()
        p.dump_stats(filename)


def get_out(out, default=None):
    out = out or default
    if out:
        return open(out, 'w')
    else:
        return sys.stdout


def gen_colors(s, e, size):
    for i in range(size):
        yield (
            s[0] + (e[0] - s[0]) * i // size,
            s[1] + (e[1] - s[1]) * i // size,
            s[2] + (e[2] - s[2]) * i // size,
        )


COLORS = list(gen_colors((255, 240, 141), (255, 65, 34), 7))
C_COLORS = list(gen_colors((44, 255, 210), (113, 194, 0), 5))
E_COLORS = list(gen_colors((230, 230, 255), (150, 150, 255), 5))
D_COLORS = list(gen_colors((190, 190, 190), (240, 240, 240), 7))


INT_STRUCT = struct.Struct('!L')


def name_hash(name):
    v, = INT_STRUCT.unpack(hashlib.sha1(bstr(name)).digest()[:4])
    return v / (0xffffffff + 1.0)


def calc_callers(stats):
    roots = []
    funcs = {}
    calls = {}

    for func, (cc, nc, tt, ct, clist) in stats.items():
        funcs[func] = {
            'calls': [],
            'called': [],
            'stat': (cc, nc, tt, ct),
        }

        if not clist:
            roots.append(func)
            calls[('root', func)] = funcs[func]['stat']

    for func, (_, _, _, _, clist) in stats.items():
        for cfunc, t in clist.items():
            assert (cfunc, func) not in calls
            funcs[cfunc]['calls'].append(func)
            funcs[func]['called'].append(cfunc)
            calls[(cfunc, func)] = t

    total = sum(funcs[r]['stat'][3] for r in roots)
    ttotal = sum(funcs[r]['stat'][2] for r in funcs)

    if not (0.8 < total / ttotal < 1.2):
        print(
            f'Warning: flameprof can\'t find proper roots, root cumtime is {total} but sum tottime is {ttotal}',
            file=sys.stderr,
        )

    # Try to find suitable root
    newroot = max(
        (r for r in funcs if r not in roots),
        key=lambda r: funcs[r]['stat'][3],
    )

    nstat = funcs[newroot]['stat']
    ntotal = total + nstat[3]

    if 0.8 < ntotal / ttotal < 1.2:
        roots.append(newroot)
        calls[('root', newroot)] = nstat
        total = ntotal
    else:
        total = ttotal

    funcs['root'] = {
        'calls': roots,
        'called': [],
        'stat': (1, 1, 0, total),
    }

    return funcs, calls


def prepare(funcs, calls, threshold=0.0001):
    blocks = []
    bblocks = []
    block_counts = collections.Counter()

    def _counts(parent, visited, level=0):
        for child in funcs[parent]['calls']:
            k = parent, child
            block_counts[k] += 1
            if block_counts[k] < 2:
                if k not in visited:
                    _counts(child, visited | {k}, level+1)

    def _calc(
            parent,
            timings,
            level,
            origin,
            visited,
            trace=(),
            pccnt=1,
            pblock=None,
    ):
        childs = funcs[parent]['calls']
        _, _, ptt, ptc = timings
        fchilds = sorted(
            (
                (f, funcs[f], calls[(parent, f)], max(block_counts[(parent, f)], pccnt))
                for f in childs
            ),
            key=lambda r: r[0],
        )

        gchilds = [r for r in fchilds if r[3] == 1]
        bchilds = [r for r in fchilds if r[3] > 1]

        if bchilds:
            gctc = sum(r[2][3] for r in gchilds)
            bctc = sum(r[2][3] for r in bchilds)
            rest = ptc - ptt - gctc
            if bctc > 0:
                factor = rest / bctc
            else:
                factor = 1

            bchilds = [
                (
                    f,
                    ff,
                    (round(cc * factor), round(nc * factor), tt * factor, tc * factor),
                    ccnt,
                )
                for (
                    f,
                    ff,
                    (cc, nc, tt, tc),
                    ccnt
                ) in bchilds
            ]

        for child, _, (cc, nc, tt, tc), ccnt in gchilds + bchilds:
            if tc / maxw > threshold:
                ckey = parent, child
                ctrace = trace + (child,)

                block = {
                    'trace': ctrace,
                    'color': (pccnt == 1 and ccnt > 1),
                    'level': level,
                    'name': child[2],
                    'hash_name': f'{child[0]}:{child[1]}:{child[2]}',
                    'full_name': f'{child[0]}:{child[1]}:{child[2]} {tc / maxw:.2%} ({cc} {nc} {tt} {tc})',
                    'w': tc,
                    'ww': tt,
                    'x': origin,
                }
                blocks.append(block)

                if ckey not in visited:
                    _calc(
                        child,
                        (cc, nc, tt, tc),
                        level + 1,
                        origin,
                        visited | {ckey},
                        ctrace,
                        ccnt,
                        block,
                    )

            elif pblock:
                pblock['ww'] += tc

            origin += tc

    def _calc_back(
            names,
            level,
            to,
            origin,
            visited,
            pw,
    ):
        if to and names:
            factor = pw / sum(calls[(r, to)][3] for r in names)
        else:
            factor = 1

        for name in sorted(names):
            func = funcs[name]
            if to:
                cc, nc, tt, tc = calls[(name, to)]
                ttt = tc * factor
            else:
                cc, nc, tt, tc = func['stat']
                ttt = tt * factor

            if ttt / maxw > threshold:
                block = {
                    'color': 2 if level > 0 else not func['calls'],
                    'level': level,
                    'name': name[2],
                    'hash_name': f'{name[0]}:{name[1]}:{name[2]}',
                    'full_name': f'{name[0]}:{name[1]}:{name[2]} {tt / maxw:.2%} ({cc} {nc} {tt} {tc})',
                    'w': ttt,
                    'x': origin,
                }
                bblocks.append(block)

                key = name, to
                if key not in visited:
                    _calc_back(
                        func['called'],
                        level+1,
                        name,
                        origin,
                        visited | {key},
                        ttt,
                    )

            origin += ttt

    maxw = funcs['root']['stat'][3] * 1.0

    _counts('root', set())

    _calc(
        'root',
        (1, 1, maxw, maxw),
        0,
        0,
        set(),
    )

    _calc_back(
        (f for f in funcs if f != 'root'),
        0,
        None,
        0,
        set(),
        0,
    )

    return blocks, bblocks, maxw


def render_svg_section(
        blocks,
        maxw,
        colors,
        h=24,
        fsize=12,
        width=1200,
        top=0,
        invert=False,
):
    maxlevel = max(r['level'] for r in blocks)
    height = (maxlevel + 1) * h
    content = []

    for b in blocks:
        x = b['x'] * width / maxw
        tx = h / 6

        if invert:
            y = top + height - (maxlevel - b['level']) * h - h
        else:
            y = top + height - b['level'] * h - h

        ty = h / 2
        w = max(1, b['w'] * width / maxw - 1)
        bcolors = colors[b['color']]
        fill = bcolors[int(len(bcolors) * name_hash(b['hash_name']))]

        content.append(ELEM.format(
            w=w,
            x=x,
            y=y,
            tx=tx,
            ty=ty,
            name=xml.sax.saxutils.escape(b['name']),
            full_name=xml.sax.saxutils.escape(b['full_name']),
            fsize=fsize,
            h=h-1,
            fill=fill,
        ))

    return content, top + height


def render_svg(
        blocks,
        bblocks,
        maxw,
        h=24,
        fsize=12,
        width=1200,
):
    if blocks:
        s1, h1 = render_svg_section(
            blocks,
            maxw,
            [COLORS, C_COLORS],
            h=h,
            fsize=fsize,
            width=width,
            top=0,
        )
        h1 += h

    else:
        s1, h1 = [], 0

    s2, h2 = render_svg_section(
        bblocks,
        maxw,
        [COLORS, E_COLORS, D_COLORS],
        h=h,
        fsize=fsize,
        width=width,
        top=h1,
        invert=True,
    )

    return SVG.format(
        '\n'.join(s1 + s2),
        width=width,
        height=h2,
    )


def render_fg(blocks, multiplier, out):
    for b in blocks:
        trace = []
        for t in b['trace']:
            trace.append('{}:{}:{}'.format(*t))

        print(';'.join(trace), round(b['ww'] * multiplier), file=out)


SVG = '''\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg
    version="1.1"
    width="{width}"
    height="{height}"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
>
<style type="text/css">
    .func_g:hover {{ stroke:black; stroke-width:0.5; cursor:pointer; }}
</style>
{}
</svg>'''

ELEM = '''\
<svg class="func_g" x="{x}" y="{y}" width="{w}" height="{h}"><g>
    <title>{full_name}</title>
    <rect height="100%" width="100%" fill="rgb{fill}" rx="2" ry="2" />
    <text alignment-baseline="central" x="{tx}" y="{ty}" font-size="{fsize}px" fill="rgb(0,0,0)">{name}</text>
</g></svg>'''


def render(
        stats,
        out,
        fmt=DEFAULT_FORMAT,
        threshold=DEFAULT_THRESHOLD / 100,
        width=DEFAULT_WIDTH,
        row_height=DEFAULT_ROW_HEIGHT,
        fsize=DEFAULT_FONT_SIZE,
        log_mult=DEFAULT_LOG_MULT,
):
    funcs, calls = calc_callers(stats)
    blocks, bblocks, maxw = prepare(funcs, calls, threshold=threshold)

    if fmt == 'svg':
        print(
            render_svg(
                blocks,
                bblocks,
                maxw,
                h=row_height,
                fsize=fsize,
                width=width,
            ),
            file=out,
        )
    elif fmt == 'log':
        render_fg(blocks, log_mult, out)

    out.flush()


def get_arg_parser():
    import textwrap

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Make flamegraph from cProfile stats.

            Using existing profile:

                flameprof -o /tmp/profile.svg /path/to/file-with-cprofile.stats

            Profile script:

                flameprof -o /tmp/profile.svg -r myscript.py [-- script_arg1, script_arg2, ...]

            Profile python module:

                flameprof -o /tmp/profile.svg -m some.module [-- mod_arg1, mod_arg2, ...]

            Profile pytest:

                py.test -p flameprof  # by default svg will be put in /tmp/pytest-prof.svg

                # other options can be set via --flameprof-opts

            Profile WSGI:

                FLAMEPROF="mypkg.mymod:application" uwsgi --http=:5000 -w flameprof:wsgi

            Out files will be placed in /tmp by default. Profile WSGI with custom filename format:

                FLAMEPROF="--wsgi-format='{method}.{url}.{ts}.{duration}ms' mypkg.mymod:application" uwsgi --http=:5000 -w flameprof:wsgi
        '''),
    )

    parser.add_argument(
        'stats',
        help='file with cProfile stats or command to run or wsgi entry',
    )
    parser.add_argument(
        '--width',
        type=int,
        help='image width, default is %(default)s',
        default=DEFAULT_WIDTH,
    )
    parser.add_argument(
        '--row-height',
        type=int,
        help='row height, default is %(default)s',
        default=DEFAULT_ROW_HEIGHT,
    )
    parser.add_argument(
        '--font-size',
        type=int,
        help='font size, default is %(default)s',
        default=DEFAULT_FONT_SIZE,
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=DEFAULT_THRESHOLD,
        help='limit functions relative cumulative time in percents, default is %(default)s%%',
    )
    parser.add_argument(
        '--format',
        choices=['svg', 'log'],
        default=DEFAULT_FORMAT,
        help='output format, default is %(default)s. `log` is suitable as input for flamegraph.pl',
    )
    parser.add_argument(
        '--log-mult',
        type=int,
        default=DEFAULT_LOG_MULT,
        help='multiply score value for log format, default is %(default)s',
    )
    parser.add_argument(
        '-r',
        '--run',
        action='store_true',
        help='run python script',
    )
    parser.add_argument(
        '-m',
        '--run-module',
        action='store_true',
        help='run python module',
    )
    parser.add_argument(
        '--cpu',
        action='store_true',
        help='count cpu time only (without io wait)',
    )
    parser.add_argument(
        '-o',
        '--out',
        help='filename with output, default is stdout',
    )
    parser.add_argument(
        '--wsgi-out-dir',
        default='/tmp',
        help='directory where svg will be places in wsgi mode, default is %(default)s',
    )
    parser.add_argument(
        '--wsgi-format',
        default='{method}.{url}',
        help='file name template in wsgi mode, default is %(default)s. Possible vars are method, url, ts or duration',
    )
    parser.add_argument(
        '--pstat',
        action='store_true',
        help='Also save profile output into *.pstat file',
    )

    return parser


def _main() -> None:
    parser = get_arg_parser()
    args, rest = parser.parse_known_args()

    if args.run or args.run_module:
        if args.run:
            with open(args.stats, mode='rb') as f:
                code = compile(f.read(), '__main__', 'exec', dont_inherit=True)
            fname = args.stats

        elif args.run_module:
            import runpy
            mod_name, mod_spec, code = runpy._get_module_details(args.stats)  # noqa
            fname = mod_spec.origin

        else:
            raise RuntimeError

        s = get_profiler(args.cpu)

        globs = {
            '__file__': fname,
            '__name__': '__main__',
            '__package__': None,
        }

        sys.argv[:] = [fname] + rest

        sys.path.insert(0, os.path.dirname(args.stats))

        try:
            s.runctx(code, globs)
        except SystemExit:
            pass

        s.create_stats()

    else:
        s = pstats.Stats(args.stats)

    if args.out and args.pstat:
        filename = os.path.splitext(args.out)[0] + '.pstat'
        s.dump_stats(filename)

    render(
        s.stats,
        get_out(args.out),
        args.format,
        args.threshold / 100,
        args.width,
        args.row_height,
        args.font_size,
        args.log_mult,
    )


if __name__ == '__main__':
    _main()
