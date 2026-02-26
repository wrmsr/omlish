A *manual*, near-direct, 'lite'-compatible translation of go-yaml (see LICENSE file):

  https://github.com/goccy/go-yaml/tree/8dd51ebb7f36f616b85f7b0e54539afa4341f22a

The primary reasons for.. doing this.. are as follows:

 - Most importantly for `@omlish-lite` usage - yaml parsing is, whether we like it or not, here to stay for things like
   docker-compose - and reading these files in amalgamated scripts like omdev.ci and omdev.pyproject is a hard
   requirement for them.

   Currently they require a system dependency on pyyaml, which violates amalg/lite isolation, and nearly defeats the
   whole point of it. An alternative is relying on some system utility (as they already rely om some very basic shell
   utilities), but there is no remotely standard or common yaml-to-json utility.

   An obvious alternative would be shamefully implement the '10% of yaml that covers 95% of usecases' with a garbage
   pile of regexes, but this codebase itself already uses anchors in its compose.yml, at which point (given the
   potential failure modes of automated infra machinery) that's extremely not acceptable.

 - Additionally, as giant yaml files are so pervasive these days, it's useful to be able to programmatically parse and
   manipulate them with full, perfect preservation of all stylistic choices, whitespace, comments, etc. This is already
   partially done here by wrapping pyyaml nodes, but it's not complete and very fragile.

It should remain symmetrical with the go-yaml codebase to allow for backporting of updates. Specifically:
 - The layout of the code in the source files, down to the order of their contents, is nearly identical
 - Its code is 'go-flavored' - for example it returns 'YamlErrorOr' rather than raises exceptions

Additionally:
 - Performance (beyond algorithmic) is of almost no concern: it's primarily intended to load a small number of config
   files a small number of times in any given process. If any but a trivial amount of yaml files need to be parsed, just
   use pyyaml ('s c-extension).

It's now ready for use, but not yet ready to be used by default.
