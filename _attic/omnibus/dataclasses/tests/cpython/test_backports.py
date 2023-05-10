import typing  # noqa
import typing as ta
import unittest
import unittest.mock as um

from ... import api as dc
from ....dev.testing import xfail


class TestBackports(unittest.TestCase):

    def test_init_false_no_default(self):
        # If init=False and no default value, then the field won't be
        #  present in the instance.
        @dc.dataclass
        class C:
            x: int = dc.field(init=False)

        self.assertNotIn('x', C().__dict__)

        @dc.dataclass
        class C:
            x: int
            y: int = 0
            z: int = dc.field(init=False)
            t: int = 10

        self.assertNotIn('z', C(0).__dict__)
        self.assertEqual(vars(C(5)), {'_t': 10, '_x': 5, '_y': 0})

    def test_missing_default(self):
        # Test that MISSING works the same as a default not being
        #  specified.
        @dc.dataclass
        class C:
            x: int = dc.field(default=dc.MISSING)

        with self.assertRaisesRegex(TypeError, r'__init__\(\) missing 1 required positional argument'):
            C()
        self.assertNotIn('_x', C.__dict__)

        @dc.dataclass
        class D:
            x: int

        with self.assertRaisesRegex(TypeError, r'__init__\(\) missing 1 required positional argument'):
            D()
        self.assertNotIn('_x', D.__dict__)

    def test_missing_default_factory(self):
        # Test that MISSING works the same as a default factory not
        #  being specified (which is really the same as a default not
        #  being specified, too).
        @dc.dataclass
        class C:
            x: int = dc.field(default_factory=dc.MISSING)

        with self.assertRaisesRegex(TypeError, r'__init__\(\) missing 1 required positional argument'):
            C()
        self.assertNotIn('_x', C.__dict__)

        @dc.dataclass
        class D:
            x: int = dc.field(default=dc.MISSING, default_factory=dc.MISSING)

        with self.assertRaisesRegex(TypeError, r'__init__\(\) missing 1 required positional argument'):
            D()
        self.assertNotIn('_x', D.__dict__)

    def test_init_var_inheritance(self):
        # Note that this deliberately tests that a dataclass need not
        #  have a __post_init__ function if it has an InitVar field.
        #  It could just be used in a derived class, as shown here.
        @dc.dataclass
        class Base:
            x: int
            init_base: dc.InitVar[int]

        # We can instantiate by passing the InitVar, even though
        #  it's not used.
        b = Base(0, 10)
        self.assertEqual(vars(b), {'_x': 0})

        @dc.dataclass
        class C(Base):
            y: int
            init_derived: dc.InitVar[int]

            def __post_init__(self, init_base, init_derived):
                self.x = self.x + init_base
                self.y = self.y + init_derived

        c = C(10, 11, 50, 51)
        self.assertEqual(vars(c), {'_x': 21, '_y': 101})

    @xfail
    def test_init_in_order(self):
        @dc.dataclass
        class C:
            a: int
            b: int = dc.field()
            c: list = dc.field(default_factory=list, init=False)
            d: list = dc.field(default_factory=list)
            e: int = dc.field(default=4, init=False)
            f: int = 4

        calls = []

        def setattr(self, name, value):
            calls.append((name, value))

        C.__setattr__ = setattr
        c = C(0, 1)  # noqa
        self.assertEqual(('a', 0), calls[0])
        self.assertEqual(('b', 1), calls[1])
        self.assertEqual(('c', []), calls[2])
        self.assertEqual(('d', []), calls[3])
        self.assertNotIn(('e', 4), calls)
        self.assertEqual(('f', 4), calls[4])

    def test_items_in_dicts(self):
        @dc.dataclass
        class C:
            a: int
            b: list = dc.field(default_factory=list, init=False)
            c: list = dc.field(default_factory=list)
            d: int = dc.field(default=4, init=False)
            e: int = 0

        c = C(0)
        # Class dict
        self.assertNotIn('_a', C.__dict__)
        self.assertNotIn('_b', C.__dict__)
        self.assertNotIn('_c', C.__dict__)
        self.assertEqual(C.d, 4)
        self.assertEqual(C.e, 0)
        # Instance dict
        self.assertIn('_a', c.__dict__)
        self.assertEqual(c.a, 0)
        self.assertIn('_b', c.__dict__)
        self.assertEqual(c.b, [])
        self.assertIn('_c', c.__dict__)
        self.assertEqual(c.c, [])
        self.assertNotIn('_d', c.__dict__)
        self.assertIn('_e', c.__dict__)
        self.assertEqual(c.e, 0)

    @xfail
    def test_field_metadata_mapping(self):
        # Make sure only a mapping can be passed as metadata
        #  zero length.
        with self.assertRaises(TypeError):
            @dc.dataclass
            class C:  # noqa
                i: int = dc.field(metadata=0)

        # Make sure an empty dict works.
        d = {}

        @dc.dataclass
        class C:  # noqa
            i: int = dc.field(metadata=d)

        self.assertFalse(dc.fields(C)[0].metadata)
        self.assertEqual(len(dc.fields(C)[0].metadata), 0)
        # Update should work (see bpo-35960).
        d['foo'] = 1
        self.assertEqual(len(dc.fields(C)[0].metadata), 1)
        self.assertEqual(dc.fields(C)[0].metadata['foo'], 1)
        with self.assertRaisesRegex(TypeError, 'does not support item assignment'):
            dc.fields(C)[0].metadata['test'] = 3

        # Make sure a non-empty dict works.
        d = {'test': 10, 'bar': '42', 3: 'three'}

        @dc.dataclass
        class C:
            i: int = dc.field(metadata=d)

        self.assertEqual(len(dc.fields(C)[0].metadata), 3)
        self.assertEqual(dc.fields(C)[0].metadata['test'], 10)
        self.assertEqual(dc.fields(C)[0].metadata['bar'], '42')
        self.assertEqual(dc.fields(C)[0].metadata[3], 'three')
        # Update should work.
        d['foo'] = 1
        self.assertEqual(len(dc.fields(C)[0].metadata), 4)
        self.assertEqual(dc.fields(C)[0].metadata['foo'], 1)
        with self.assertRaises(KeyError):
            # Non-existent key.
            dc.fields(C)[0].metadata['baz']
        with self.assertRaisesRegex(TypeError, 'does not support item assignment'):
            dc.fields(C)[0].metadata['test'] = 3

    @xfail
    def test_field_metadata_custom_mapping(self):
        # Try a custom mapping.
        class SimpleNameSpace:
            def __init__(self, **kw):
                self.__dict__.update(kw)

            def __getitem__(self, item):
                if item == 'xyzzy':
                    return 'plugh'
                return getattr(self, item)

            def __len__(self):
                return self.__dict__.__len__()

        @dc.dataclass
        class C:
            i: int = dc.field(metadata=SimpleNameSpace(a=10))

        self.assertEqual(len(dc.fields(C)[0].metadata), 1)
        self.assertEqual(dc.fields(C)[0].metadata['a'], 10)
        with self.assertRaises(AttributeError):
            dc.fields(C)[0].metadata['b']
        # Make sure we're still talking to our custom mapping.
        self.assertEqual(dc.fields(C)[0].metadata['xyzzy'], 'plugh')

    @xfail
    def test_overwriting_frozen(self):
        # frozen uses __setattr__ and __delattr__.
        with self.assertRaisesRegex(TypeError, 'Cannot overwrite attribute __setattr__'):
            @dc.dataclass(frozen=True)
            class C:  # noqa
                x: int

                def __setattr__(self):
                    pass

        with self.assertRaisesRegex(TypeError, 'Cannot overwrite attribute __delattr__'):
            @dc.dataclass(frozen=True)
            class C:  # noqa
                x: int

                def __delattr__(self):
                    pass

        @dc.dataclass(frozen=False)
        class C:  # noqa
            x: int

            def __setattr__(self, name, value):
                self.__dict__['_x'] = value * 2

        self.assertEqual(C(10).x, 20)

    def test_simple(self):
        @dc.dataclass
        class C:
            __slots__ = ('_x',)
            x: ta.Any

        # There was a bug where a variable in a slot was assumed to also have a default value (of type
        # types.MemberDescriptorType).
        with self.assertRaisesRegex(TypeError, r"__init__\(\) missing 1 required positional argument: 'x'"):
            C()

        # We can create an instance, and assign to x.
        c = C(10)
        self.assertEqual(c.x, 10)
        c.x = 5
        self.assertEqual(c.x, 5)

        # We can't assign to anything else.
        with self.assertRaisesRegex(AttributeError, "'C' object has no attribute 'y'"):
            c.y = 5

    def test_classvar_module_level_import(self):
        from . import dataclass_module_1
        from . import dataclass_module_1_str
        from . import dataclass_module_2
        from . import dataclass_module_2_str

        for m in (dataclass_module_1, dataclass_module_1_str, dataclass_module_2, dataclass_module_2_str):
            with self.subTest(m=m):
                # There's a difference in how the ClassVars are interpreted when using string annotations or not. See
                # the imported modules for details.
                if m.USING_STRINGS:
                    c = m.CV(10)
                else:
                    c = m.CV()
                self.assertEqual(c.cv0, 20)

                # There's a difference in how the InitVars are interpreted when using string annotations or not. See the
                # imported modules for details.
                c = m.IV(0, 1, 2, 3, 4)

                for field_name in ('iv0', 'iv1', 'iv2', 'iv3'):
                    with self.subTest(field_name=field_name):
                        with self.assertRaisesRegex(AttributeError, f"object has no attribute '{field_name}'"):
                            # Since field_name is an InitVar, it's not an instance field.
                            getattr(c, field_name)

                # iv4 is interpreted as an InitVar, so it won't exist on the instance.
                self.assertNotIn('not_iv4', c.__dict__)

    def test_init_var(self):
        def post_init(self, y):
            self.x *= y

        C = dc.make_dataclass(
            'C',
            [
                ('x', int),
                ('y', dc.InitVar[int]),
            ],
            namespace={'__post_init__': post_init},
        )
        c = C(2, 3)
        self.assertEqual(vars(c), {'_x': 6})
        self.assertEqual(len(dc.fields(c)), 1)

    def test_class_var(self):
        C = dc.make_dataclass(
            'C',
            [
                ('x', int),
                ('y', ta.ClassVar[int], 10),
                ('z', ta.ClassVar[int], dc.field(default=20)),
            ],
        )
        c = C(1)
        self.assertEqual(vars(c), {'_x': 1})
        self.assertEqual(len(dc.fields(c)), 1)
        self.assertEqual(C.y, 10)
        self.assertEqual(C.z, 20)

    def test_no_types(self):
        C = dc.make_dataclass('Point', ['x', 'y', 'z'])
        c = C(1, 2, 3)
        self.assertEqual(vars(c), {'_x': 1, '_y': 2, '_z': 3})
        self.assertEqual(C.__annotations__, {
            'x': 'typing.Any',
            'y': 'typing.Any',
            'z': 'typing.Any',
        })

        C = dc.make_dataclass('Point', ['x', ('y', int), 'z'])
        c = C(1, 2, 3)
        self.assertEqual(vars(c), {'_x': 1, '_y': 2, '_z': 3})
        self.assertEqual(C.__annotations__, {
            'x': 'typing.Any',
            'y': int,
            'z': 'typing.Any',
        })

    @xfail
    def test_descriptors_set_name(self):
        # See bpo-33141.

        # Create a descriptor.
        class D:
            def __set_name__(self, owner, name):
                self.name = name + 'x'

            def __get__(self, instance, owner):
                if instance is not None:
                    return 1
                return self

        # This is the case of just normal descriptor behavior, no
        #  dataclass code is involved in initializing the descriptor.
        @dc.dataclass
        class C:
            c: int = D()

        self.assertEqual(C.c.name, 'cx')

        # Now test with a default value and init=False, which is the
        #  only time this is really meaningful.  If not using
        #  init=False, then the descriptor will be overwritten, anyway.
        @dc.dataclass
        class C:
            c: int = dc.field(default=D(), init=False)

        self.assertEqual(C.c.name, 'cx')
        self.assertEqual(C().c, 1)

    @xfail
    def test_descriptors_non_descriptor(self):
        # PEP 487 says __set_name__ should work on non-descriptors.
        # Create a descriptor.

        class D:
            def __set_name__(self, owner, name):
                self.name = name + 'x'

        @dc.dataclass
        class C:
            c: int = dc.field(default=D(), init=False)

        self.assertEqual(C.c.name, 'cx')

    @xfail
    def test_descriptors_lookup_on_instance(self):
        # See bpo-33175.
        class D:
            pass

        d = D()
        # Create an attribute on the instance, not type.
        d.__set_name__ = um.Mock()

        # Make sure d.__set_name__ is not called.
        @dc.dataclass
        class C:
            i: int = dc.field(default=d, init=False)

        self.assertEqual(d.__set_name__.call_count, 0)

    @xfail
    def test_descriptors_lookup_on_class(self):
        # See bpo-33175.
        class D:
            pass

        D.__set_name__ = um.Mock()

        # Make sure D.__set_name__ is called.
        @dc.dataclass
        class C:
            i: int = dc.field(default=D(), init=False)

        self.assertEqual(D.__set_name__.call_count, 1)


if __name__ == '__main__':
    unittest.main()
