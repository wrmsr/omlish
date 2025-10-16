from ... import inject as inj


def test_const_fn():
    cf = inj.ConstFn(420)
    assert cf() == 420

    assert cf.origins.lst
    assert 'test_utils.py' in repr(cf.origins.lst[0])

    assert inj.create_injector(inj.bind(int, to_fn=inj.ConstFn(421)))[int] == 421
