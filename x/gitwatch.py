"""
TODO:
 - idiom / manifest to 'watch repos'?
  - like, watch repo for changes to review, after manually checking update to latest rev?
  - !!! just gh urls are more convenient lol - blob vs tree already does the right thing
   - !!! @omlish-gitwatch https:// ...
   - dedupe, update all together - handle amalgs naively / correctly
 - TODO: watch only certain branch

 - https://github.com/jmespath-community/python-jmespath/tree/aef45e9d665de662eee31b06aeb8261e2bc8b90a
 - https://github.com/pgjones/hypercorn/tree/84d06b8cf47798d2df7722273341e720ec0ea102
 - https://github.com/pypa/packaging/blob/2c885fe91a54559e2382902dce28428ad2887be5/src/packaging/specifiers.py
 - https://github.com/pypa/packaging/blob/2c885fe91a54559e2382902dce28428ad2887be5/src/packaging/version.py
 - https://github.com/pypa/packaging/blob/cf2cbe2aec28f87c6228a6fb136c27931c9af407/src/packaging/_parser.py#L65
 - https://github.com/pypa/packaging/blob/cf2cbe2aec28f87c6228a6fb136c27931c9af407/src/packaging/utils.py
 - https://github.com/pypa/wheel/blob/7bb46d7727e6e89fe56b3c78297b3af2672bbbe2/src/wheel/wheelfile.py
 - https://github.com/python/cpython/blob/21d2a9ab2f4dcbf1be462d3b7f7a231a46bc1cb7/Parser/asdl.py
 - https://github.com/python/cpython/blob/3e3a4d231518f91ff2f3c5a085b3849e32f1d548/Lib/dataclasses.py
 - https://github.com/python/cpython/blob/6810928927e4d12d9a5dd90e672afb096882b730/Parser/Python.asdl
 - https://github.com/python/cpython/blob/6810928927e4d12d9a5dd90e672afb096882b730/Python/hamt.c
 - https://github.com/python/cpython/blob/f5009b69e0cd94b990270e04e65b9d4d2b365844/Lib/tomllib/_parser.py
 - https://github.com/python/cpython/tree/3e3a4d231518f91ff2f3c5a085b3849e32f1d548/Lib/test/test_dataclasses
 - https://github.com/theskumar/python-dotenv/tree/4d505f2c9bc3569791e64bca0f2e4300f43df0e0/src/dotenv
 - https://github.com/tusharsadhwani/yen/blob/8d1bb0c1232c7b0159caefb1bf3a5348b93f7b43/src/yen/github.py
 - https://github.com/umlet/pwk/blob/dc23b3400108a71947a695f1fa1df0f514b42528/pwk
"""
import dataclasses as dc


@dc.dataclass(frozen=True)
class GitWatch:
    repo: str
    rev: str
    path: str | None = None
