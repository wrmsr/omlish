"""
TODO:
 - metaclass:
  - cleanup confer
 - descriptors - check_type/validators don't handle setters lol
 - deep_frozen?
 - field:
  - frozen
  - pickle/transient
  - mangled
  - doc
  - derive
  - check_type
 - class
  - strict_eq
  - allow_setattr
  - mangler
 - observable
 - c/py gen
 - iterable
 - proto/jsonschema gen
 - enums
 - nodal
 - embedding? forward kwargs in general? or only for replace?

TODO refs:
 - batch up exec calls
  - https://github.com/python/cpython/commit/8945b7ff55b87d11c747af2dad0e3e4d631e62d6
 - add doc parameter to dataclasses.field
  - https://github.com/python/cpython/commit/9c7657f09914254724683d91177aed7947637be5
 - add decorator argument to make_dataclass
  - https://github.com/python/cpython/commit/3e3a4d231518f91ff2f3c5a085b3849e32f1d548
"""
