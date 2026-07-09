A pretty direct extraction of mypy's core datamodel and algorithms, retargeted for use at runtime, powered by runtime
type forms (`typing.` annotations) rather than textual source.

Many of the `Type` nodes are partially or fully unreferenced - if so, they exist as living placeholders and provide
structural parity with mypy proper.

In general, when the core's capability needs to grow, it will continue to attempt to mimic mypy proper to the degree
possible.

The core remains mypyc compatible (and is in practice used compiled through it) but that isn't currently wired into any
build or deployment process.
