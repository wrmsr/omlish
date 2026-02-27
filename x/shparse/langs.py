import typing as ta

from .errors import Error
from .errors import GenericError


##


# LangVariant describes a shell language variant to use when tokenizing and
# parsing shell code. The zero value is [LANG_BASH].
LangVariant = ta.NewType('LangVariant', int)

# TODO(v4): the zero value should be left as an unset and invalid value.
# TODO(v4): the type should be uint32 now that we use this as a bitset;
# an unsigned integer is clearer, and being agnostic to uint size avoids issues.


# LANG_BASH corresponds to the GNU Bash language, as described in its
# manual at https:#www.gnu.org/software/bash/manual/bash.html.
#
# We currently follow Bash version 5.2.
#
# Its string representation is "bash".
LANG_BASH = LangVariant(1 << 0)  # 1

# LANG_POSIX corresponds to the POSIX Shell language, as described at
# https:#pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html.
#
# Its string representation is "posix" or "sh".
LANG_POSIX = LangVariant(1 << 1)  # 2

# LANG_MIR_BSD_KORN corresponds to the MirBSD Korn Shell, also known as
# mksh, as described at http:#www.mirbsd.org/htman/i386/man1/mksh.htm.
# Note that it shares some features with Bash, due to the shared
# ancestry that is ksh.
#
# We currently follow mksh version 59.
#
# Its string representation is "mksh".
LANG_MIR_BSD_KORN = LangVariant(1 << 2)  # 4

# LANG_BATS corresponds to the Bash Automated Testing System language,
# as described at https:#github.com/bats-core/bats-core. Note that
# it's just a small extension of the Bash language.
#
# Its string representation is "bats".
LANG_BATS = LangVariant(1 << 3)  # 8

# LANG_ZSH corresponds to the Z shell, as described at https:#www.zsh.org/.
#
# Note that its support in the syntax package is experimental and
# incomplete for now. See https:#github.com/mvdan/sh/issues/120.
#
# We currently follow Zsh version 5.9.
#
# Its string representation is "zsh".
LANG_ZSH = LangVariant(1 << 4)  # 16

# LANG_AUTO corresponds to automatic language detection,
# commonly used by end-user applications like shfmt,
# which can guess a file's language variant given its filename or shebang.
#
# At this time, [Variant] does not support LANG_AUTO.
LANG_AUTO = LangVariant(1 << 5)  # 32

# LANG_BASH_LEGACY is what [LANG_BASH] used to be, when it was zero.
# We still support it for the sake of backwards compatibility.
LANG_BASH_LEGACY = LangVariant(0)

# LANG_RESOLVED_VARIANTS contains all known variants except [LANG_AUTO],
# which is meant to resolve to another variant.
LANG_RESOLVED_VARIANTS = LANG_BASH | LANG_POSIX | LANG_MIR_BSD_KORN | LANG_BATS | LANG_ZSH

# LANG_RESOLVED_VARIANTS_COUNT is LANG_RESOLVED_VARIANTS.count() as a constant.
# TODO: Can we compute this as a constant expression somehow?
# For example, if we had log2, we could do log2(LANG_AUTO).
LANG_RESOLVED_VARIANTS_COUNT = 5

# langBashLike contains Bash plus all variants which are extensions of it.
LANG_BASH_LIKE = LANG_BASH | LANG_BATS


def lang_string(l: LangVariant) -> str:
    if l == LANG_BASH_LEGACY or l == LANG_BASH:
        return 'bash'
    elif l == LANG_POSIX:
        return 'posix'
    elif l == LANG_MIR_BSD_KORN:
        return 'mksh'
    elif l == LANG_BATS:
        return 'bats'
    elif l == LANG_ZSH:
        return 'zsh'
    elif l == LANG_AUTO:
        return 'auto'
    else:
        return 'unknown shell language variant'


def lang_from_string(s: str) -> LangVariant | Error:
    if s == 'bash':
        return LANG_BASH
    elif s == 'posix' or s == 'sh':
        return LANG_POSIX
    elif s == 'mksh':
        return LANG_MIR_BSD_KORN
    elif s == 'bats':
        return LANG_BATS
    elif s == 'zsh':
        return LANG_ZSH
    elif s == 'auto':
        return LANG_AUTO
    else:
        return GenericError('unknown shell language variant: %r' % (s,))


def lang_in(l: LangVariant, l2: LangVariant) -> bool:
    return l & l2 == l


def lang_bits(l: LangVariant) -> list[LangVariant]:
    return [
        LangVariant(1 << i)
        for i in range(LANG_RESOLVED_VARIANTS_COUNT)
        if l & (1 << i) != 0
    ]
