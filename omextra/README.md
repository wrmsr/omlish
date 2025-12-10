# Overview

Core-like code not appropriate for inclusion in `omlish` for one reason or another. A bit like
[`golang.org/x`](https://pkg.go.dev/golang.org/x) but even less suitable for production use.

Code here is usually in the process of either moving out of or moving into `omlish` proper, or being demoted to the
unpublished `x` root dir, or just being deleted.

# Notable packages

- **[text.antlr](https://github.com/wrmsr/omlish/blob/master/omextra/text/antlr)** -
  [ANTLR](https://www.antlr.org/)-related code. The codebase is generally moving away from antlr in favor of an internal
  [abnf engine](https://github.com/wrmsr/omlish/blob/master/omextra/text/abnf), but I have other projects that need the
  full power of antlr, so it may remain as an optional dep for utility code (much like sqlalchemy).
