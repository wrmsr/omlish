# ruff: noqa: UP006 UP007 UP045
"""
https://docs.python.org/3/library/unittest.html#command-line-interface
~ https://github.com/python/cpython/tree/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/unittest
"""
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
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All Rights
# Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
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
import dataclasses as dc
import types
import typing as ta
import unittest

from ...lite.abstract import Abstract
from .types import UnittestTest


##


class UnittestTargetLoader:
    def __init__(
            self,
            *,
            test_name_patterns: ta.Optional[ta.Sequence[str]] = None,
            module: ta.Union[str, types.ModuleType, None] = None,
            loader: ta.Optional[unittest.loader.TestLoader] = None,
    ) -> None:
        super().__init__()

        self._test_name_patterns = test_name_patterns
        self._module = module
        self._loader = loader

    #

    class Target(Abstract):
        pass

    class ModuleTarget(Target):
        pass

    @dc.dataclass(frozen=True)
    class NamesTarget(Target):
        test_names: ta.Optional[ta.Sequence[str]] = None

    @dc.dataclass(frozen=True)
    class DiscoveryTarget(Target):
        start: ta.Optional[str] = None
        pattern: ta.Optional[str] = None
        top: ta.Optional[str] = None

    def load(self, target: Target) -> UnittestTest:
        loader = self._loader
        if loader is None:
            loader = unittest.loader.TestLoader()

        if self._test_name_patterns:
            loader.testNamePatterns = self._test_name_patterns  # type: ignore[assignment]

        if isinstance(target, UnittestTargetLoader.DiscoveryTarget):
            return ta.cast(UnittestTest, loader.discover(
                target.start,  # type: ignore[arg-type]
                target.pattern,  # type: ignore[arg-type]
                target.top,
            ))

        module: ta.Any = self._module
        if isinstance(module, str):
            module = __import__(module)
            for part in module.split('.')[1:]:
                module = getattr(module, part)

        if isinstance(target, UnittestTargetLoader.ModuleTarget):
            return ta.cast(UnittestTest, loader.loadTestsFromModule(module))

        elif isinstance(target, UnittestTargetLoader.NamesTarget):
            return ta.cast(UnittestTest, loader.loadTestsFromNames(
                target.test_names,  # type: ignore[arg-type]
                module,
            ))

        else:
            raise TypeError(target)
