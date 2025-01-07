from .. import linehisto


def test_linehisto():
    kh = linehisto.KeyedHisto()
    khr = linehisto.KeyedHistoRenderer(kh)

    print(khr.render_to_str())

    kh.inc('foo')
    print(khr.render_to_str())
