"""
TODO:
 - idiom / manifest to 'watch repos'?
  - like, watch repo for changes to review, after manually checking update to latest rev?

Targets:
 - https://github.com/jmespath-community/python-jmespath @ aef45e9d665de662eee31b06aeb8261e2bc8b90a
 - https://github.com/pgjones/hypercorn @ 84d06b8cf47798d2df7722273341e720ec0ea102
 - https://github.com/python/cpython : Lib/dataclasses.py @ 3e3a4d231518f91ff2f3c5a085b3849e32f1d548
 - https://github.com/python/cpython : Lib/test/test_dataclasses @ 3e3a4d231518f91ff2f3c5a085b3849e32f1d548
 - https://github.com/python/cpython : Parser/Parser.asdl @ ca269e58c290be8ca11bb728004ea842d9f85e3a
 - https://github.com/python/cpython : Parser/asdl.py @ 21d2a9ab2f4dcbf1be462d3b7f7a231a46bc1cb7
 - https://github.com/python/cpython : Python/hamt.c @ 6810928927e4d12d9a5dd90e672afb096882b730
 - https://github.com/theskumar/python-dotenv : src/dotenv @ 4d505f2c9bc3569791e64bca0f2e4300f43df0e0
"""
import dataclasses as dc


@dc.dataclass(frozen=True)
class GitWatch:
    repo: str
    rev: str
    path: str | None = None
