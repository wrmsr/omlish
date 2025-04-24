# Overview

Development utilities and support code.

# Notable packages

- **[cli](cli)** - The codebase's all-in-one CLI. This is not installed as an entrypoint / command when this package is
  itself installed - that is separated into the `omdev-cli` installable package so as to not pollute users' bin/
  directories when depping this lib for its utility code.

- **[amalg](amalg)** - The [amalgamator](#amalgamation).

# Amalgamation

Amalgamation is the process of stitching together multiple python source files into a single self-contained python
script. ['lite'](../omlish/README.md#lite-code) code is written in a style conducive to this.
