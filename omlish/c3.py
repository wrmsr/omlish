# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import functools
import operator
import typing as ta


T = ta.TypeVar('T')


##


def merge(seqs: ta.MutableSequence[list[T]]) -> list[T]:
    """
    Merges MROs in *sequences* to a single MRO using the C3 algorithm.

    Adapted from https://www.python.org/download/releases/2.3/mro/.
    """

    result: list[T] = []
    candidate: T | None = None
    while True:
        seqs = [s for s in seqs if s]  # purge empty sequences
        if not seqs:
            return result
        for s1 in seqs:  # find merge candidates among seq heads
            candidate = s1[0]
            for s2 in seqs:
                if candidate in s2[1:]:
                    candidate = None
                    break  # reject the current head, it appears later
            else:
                break
        if candidate is None:
            raise RuntimeError('Inconsistent hierarchy')
        result.append(candidate)
        # remove the chosen candidate
        for seq in seqs:
            if seq[0] == candidate:
                del seq[0]


def _default_is_abstract(obj: ta.Any) -> bool:
    return hasattr(obj, '__abstractmethods__')


def mro(
        cls: T,
        abcs: ta.Sequence[T] | None = None,
        *,
        get_bases: ta.Callable[[T], ta.Sequence[T]] = operator.attrgetter('__bases__'),
        is_subclass: ta.Callable[[T, T], bool] = issubclass,  # type: ignore
        is_abstract: ta.Callable[[T], bool] = _default_is_abstract,
) -> list[T]:
    """
    Computes the method resolution order using extended C3 linearization.

    If no *abcs* are given, the algorithm works exactly like the built-in C3 linearization used for method resolution.

    If given, *abcs* is a list of abstract base classes that should be inserted into the resulting MRO. Unrelated ABCs
    are ignored and don't end up in the result. The algorithm inserts ABCs where their functionality is introduced, i.e.
    issubclass(cls, abc) returns True for the class itself but returns False for all its direct base classes. Implicit
    ABCs for a given class (either registered or inferred from the presence of a special method like __len__) are
    inserted directly after the last ABC explicitly listed in the MRO of said class. If two implicit ABCs end up next to
    each other in the resulting MRO, their ordering depends on the order of types in *abcs*.
    """

    for i, base in enumerate(reversed(get_bases(cls))):
        if is_abstract(base):
            boundary = len(get_bases(cls)) - i
            break  # Bases up to the last explicit ABC are considered first.
    else:
        boundary = 0
    abcs = list(abcs) if abcs else []
    explicit_bases = list(get_bases(cls)[:boundary])
    abstract_bases = []
    other_bases = list(get_bases(cls)[boundary:])
    for base in abcs:
        if (
                is_subclass(cls, base) and  # noqa
                not any(is_subclass(b, base) for b in get_bases(cls))  # noqa
        ):
            # If *cls* is the class that introduces behaviour described by an ABC *base*, insert said ABC to its MRO.
            abstract_bases.append(base)
    for base in abstract_bases:
        abcs.remove(base)
    rec = functools.partial(
        mro,
        abcs=abcs,
        get_bases=get_bases,
        is_subclass=is_subclass,
        is_abstract=is_abstract,
    )
    explicit_c3_mros = [rec(base) for base in explicit_bases]
    abstract_c3_mros = [rec(base) for base in abstract_bases]
    other_c3_mros = [rec(base) for base in other_bases]
    return merge(
        [[cls]] +  # noqa
        explicit_c3_mros + abstract_c3_mros + other_c3_mros +
        [explicit_bases] + [abstract_bases] + [other_bases],
    )


def compose_mro(
        cls: T,
        types: ta.Iterable[T],
        *,
        get_mro: ta.Callable[[T], ta.Sequence[T] | None] = operator.attrgetter('__mro__'),
        get_bases: ta.Callable[[T], ta.Sequence[T]] = operator.attrgetter('__bases__'),
        is_subclass: ta.Callable[[T, T], bool] = issubclass,  # type: ignore
        get_subclasses: ta.Callable[[T], ta.Iterable[T]] = operator.methodcaller('__subclasses__'),
        is_abstract: ta.Callable[[T], bool] = _default_is_abstract,
) -> list[T]:
    """
    Calculates the method resolution order for a given class *cls*.

    Includes relevant abstract base classes (with their respective bases) from the *types* list. Uses a modified C3
    linearization algorithm.
    """

    bases = set(get_mro(cls) or [])

    # Remove entries which are already present in the __mro__ or unrelated.
    def is_related(typ):
        return typ not in bases and get_mro(typ) is not None and is_subclass(cls, typ)

    types = [n for n in types if is_related(n)]

    # Remove entries which are strict bases of other entries (they will end up in the MRO anyway.
    def is_strict_base(typ):
        for other in types:  # noqa
            if typ != other and typ in (get_mro(other) or []):
                return True
        return False

    types = [n for n in types if not is_strict_base(n)]

    # Subclasses of the ABCs in *types* which are also implemented by *cls* can be used to stabilize ABC ordering.
    type_set = set(types)
    _mro = []
    for typ in types:
        found: list[list[T]] = []
        for sub in get_subclasses(typ):
            if sub not in bases and is_subclass(cls, sub):  # noqa
                found.append([s for s in (get_mro(sub) or []) if s in type_set])
        if not found:
            _mro.append(typ)
            continue

        # Favor subclasses with the biggest number of useful bases
        found.sort(key=len, reverse=True)
        for lst in found:
            for subcls in lst:
                if subcls not in _mro:
                    _mro.append(subcls)

    return mro(
        cls,
        abcs=_mro,
        get_bases=get_bases,
        is_subclass=is_subclass,
        is_abstract=is_abstract,
    )
