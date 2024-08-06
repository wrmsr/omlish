import io
import csv
import os.path


def test_csv():
    from .. import csvloader

    with open(os.path.join(os.path.dirname(__file__), 'csvs', 'sales100.csv'), 'r') as f:
        buf = f.read()

    rows = csvloader.loads(buf.strip())
    assert len(rows) == 101

    def _coerce(v):
        try:
            return int(v)
        except ValueError:
            pass
        try:
            return float(v)
        except ValueError:
            pass
        return v

    rows2 = [list(map(_coerce, r)) for r in csv.reader(io.StringIO(buf))]

    assert rows == rows2
