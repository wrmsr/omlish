A pretty direct extraction of mypy's core datamodel and algorithms, retargeted for use at runtime, powered by type
annotations rather than textual source. This may or may not replace `omlish.reflect` - I really don't know yet.

The root package - especially `universe` - will have to be heavily overhauled (or outright replaced) before actual use,
but its current form has at least served to drive development of the core subpackage.

The core remains mypyc compatible.
