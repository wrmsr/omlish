import os.path


def _main():
    base_dir = os.path.dirname(__file__)

    for p, ds, fs in os.walk(base_dir):
        for f in fs:
            if f != '.pkgdata':
                continue
            rp = os.path.relpath(p, base_dir)
            with open(os.path.join(p, f)) as fo:
                src = fo.read()
            for l in src.splitlines():
                if not (l := l.strip()):
                    continue
                if l.startswith('!'):
                    exc = True
                    l = l[1:]
                else:
                    exc = False
                print(os.path.join(rp, l))


if __name__ == '__main__':
    _main()
