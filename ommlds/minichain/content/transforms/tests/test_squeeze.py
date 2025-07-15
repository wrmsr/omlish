from ..squeeze import squeeze_content


def test_squeeze():
    print(squeeze_content([['hi'], '', ['there']]))
