from .. import scan


def test_scan():
    assert list(scan.scan(r'{:x} {:x}', '0x10 20')) == [0x10, 0x20]

    m = scan.Scanner('{} x {asdf:}').scan('ab x cd')
    print(m)

    assert scan.Scanner('a {v:x}').scan('a abc')['v'] == 0xabc

    # s = scan.Scanner('ab{{{cd}}}ef{gh}ij')
    print(scan.scan('ab {} cd', 'ab x cd'))
    print(scan.scan('{} x {:}', 'ab x cd'))
    print(scan.scan('ab {x} cd', 'ab x cd'))
    print(scan.scan('ab {x:} cd', 'ab x cd'))
    print(scan.scan('ab {x:d} cd', 'ab 82 cd'))

    assert list(scan.scan('{:w} {^:w}', 'x    y').values) == ['x', 'y']
    assert scan.scan('{:w} {:w}', 'x   y') is None

    scan.Scanner(r'{:/\w}')

    assert list(scan.scan(r'{:/abc}', 'abc')) == ['abc']
    assert scan.scan(r'{:/aBc}', 'abc') is None
    assert list(scan.scan(r'{!:/aBc}', 'abc')) == ['abc']
    assert list(scan.scan(r'{:/aBc}', 'abc', ignore_case=True)) == ['abc']
    assert scan.scan(r'{!:/aBc}', 'abc', ignore_case=True) is None
