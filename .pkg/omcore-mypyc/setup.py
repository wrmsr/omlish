import mypyc.build as mcb
import setuptools as st


st.setup(
    ext_modules=mcb.mypycify(
        [
            'omcore/reflect/core/__init__.py',
            'omcore/reflect/core/_mypycshim.py',
            'omcore/reflect/core/compat.py',
            'omcore/reflect/core/constraints.py',
            'omcore/reflect/core/copytype.py',
            'omcore/reflect/core/expandtype.py',
            'omcore/reflect/core/join.py',
            'omcore/reflect/core/meet.py',
            'omcore/reflect/core/solve.py',
            'omcore/reflect/core/strconv.py',
            'omcore/reflect/core/substitute.py',
            'omcore/reflect/core/subtypes.py',
            'omcore/reflect/core/symbols.py',
            'omcore/reflect/core/typekeys.py',
            'omcore/reflect/core/typeops.py',
            'omcore/reflect/core/types.py',
            'omcore/reflect/core/typetraverser.py',
            'omcore/reflect/core/typevisitor.py',
        ],
    ),
)
