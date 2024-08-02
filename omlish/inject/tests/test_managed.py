# import contextlib
# import typing as ta
#
# from ... import dataclasses as dc
# from ... import inject as inj
# from ... import lang


class SomeManager:
    ec = 0
    xc = 0

    def __enter__(self):
        self.ec += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.xc += 1


# def test_managed():
#     with inj.create_managed_injector(inj.as_elements(
#         inj.as_binding(420),
#         inj.managed(SomeManager),
#     )) as i:
#         assert i[int] == 420
#         sm = i[SomeManager]
#         assert (sm.ec, sm.xc) == (1, 0)
#     assert (sm.ec, sm.xc) == (1, 1)


# def test_custom_inject():
#     @dc.dataclass(frozen=True)
#     @dc.extra_params(cache_hash=True)
#     class _JankManagedTag(lang.Final):
#         tag: ta.Any
#
#     def jank_managed(a):
#         b = inj.as_binding(a)
#         mg_key = dc.replace(b.key, tag=_JankManagedTag(b.key.tag))
#
#         def prov(i: inj.Injector):
#             o = i[mg_key]
#             i[contextlib.ExitStack].enter_context(o)
#             return o
#
#         return inj.as_elements(
#             dc.replace(b, key=mg_key),
#             dc.replace(b, provider=inj.fn(prov, b.key.ty)),
#         )
#
#     with inj.create_managed_injector(inj.as_elements(
#             inj.bind(420),
#             jank_managed(SomeManager),
#     )) as i:
#         assert i[int] == 420
#         sm = i[SomeManager]
#         assert (sm.ec, sm.xc) == (1, 0)
#     assert (sm.ec, sm.xc) == (1, 1)
