# @omlish-generated
# type: ignore
# ruff: noqa
# flake8: noqa
import dataclasses
import reprlib
import types


##


REGISTRY = {}


def _register(**kwargs):
    def inner(fn):
        REGISTRY[kwargs['plan_repr']] = (kwargs, fn)
        return fn
    return inner


##


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('all_matches', 'partial_parses', 'any_root', 'match_tree')), EqPlan(fields=('all_m"
        "atches', 'partial_parses', 'any_root', 'match_tree')), FrozenPlan(fields=('all_matches', 'partial_parses', 'an"
        "y_root', 'match_tree'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('all_matches', 'part"
        "ial_parses', 'any_root', 'match_tree'), cache=False), InitPlan(fields=(InitPlan.Field(name='all_matches', anno"
        "tation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='partial_parses', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='ini"
        "t.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='any_root', annotation=OpRef(name='init.fields.2.ann"
        "otation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='match_tree', anno"
        "tation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), s"
        "elf_param='self', std_params=(), kw_only_params=('all_matches', 'partial_parses', 'any_root', 'match_tree'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='all_matches', kw_only=True, fn=None), ReprPlan.Field(name='partial_parses', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='any_root', kw_only=True, fn=None), ReprPlan.Field(name='match_tree', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='539d9b0cdd4e831cff3bd7c0f04804ce66051513',
    cls_names=(
        ('omlish.text.abnf.engines.base', 'EngineCapabilities'),
    ),
)
def _process_dataclass__539d9b0cdd4e831cff3bd7c0f04804ce66051513():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                all_matches=self.all_matches,
                partial_parses=self.partial_parses,
                any_root=self.any_root,
                match_tree=self.match_tree,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.all_matches == other.all_matches and
                self.partial_parses == other.partial_parses and
                self.any_root == other.any_root and
                self.match_tree == other.match_tree
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'all_matches',
            'partial_parses',
            'any_root',
            'match_tree',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.all_matches,
                self.partial_parses,
                self.any_root,
                self.match_tree,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            all_matches: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            partial_parses: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            any_root: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            match_tree: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'all_matches', all_matches)
            __dataclass__object_setattr(self, 'partial_parses', partial_parses)
            __dataclass__object_setattr(self, 'any_root', any_root)
            __dataclass__object_setattr(self, 'match_tree', match_tree)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"all_matches={self.all_matches!r}")
            parts.append(f"partial_parses={self.partial_parses!r}")
            parts.append(f"any_root={self.any_root!r}")
            parts.append(f"match_tree={self.match_tree!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'is_rule', 'rule_name')), FrozenPlan(fields=('name', 'is_rule', 'rule_name"
        "'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='is_rule', annotation=OpRef(name='i"
        "nit.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='rule_name', annotation=OpRef(nam"
        "e='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('name', 'is_rule'"
        ", 'rule_name'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
        "())))"
    ),
    plan_repr_sha1='4af384cbf5bf3126d5b25a0a7d978c091850a03b',
    cls_names=(
        ('omlish.text.abnf.engines.lr.cfg', 'Nt'),
    ),
)
def _process_dataclass__4af384cbf5bf3126d5b25a0a7d978c091850a03b():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                name=self.name,
                is_rule=self.is_rule,
                rule_name=self.rule_name,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'name',
            'is_rule',
            'rule_name',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            is_rule: __dataclass__init__fields__1__annotation,
            rule_name: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'is_rule', is_rule)
            __dataclass__object_setattr(self, 'rule_name', rule_name)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('index', 'lhs', 'rhs', 'gaps')), FrozenPlan(fields=('index', 'lhs', 'rhs', 'gaps')"
        ", allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='index', annotation=OpRef(name='init"
        ".fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='lhs', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='rhs', annotation=OpRef(name='init.fie"
        "lds.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='gaps', annotation=OpRef(name='init.fiel"
        "ds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params"
        "=('index', 'lhs', 'rhs', 'gaps'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=())))"
    ),
    plan_repr_sha1='5a41133839b8f78abbdde874874e91a03b6fde0b',
    cls_names=(
        ('omlish.text.abnf.engines.lr.cfg', 'Production'),
    ),
)
def _process_dataclass__5a41133839b8f78abbdde874874e91a03b6fde0b():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                index=self.index,
                lhs=self.lhs,
                rhs=self.rhs,
                gaps=self.gaps,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'index',
            'lhs',
            'rhs',
            'gaps',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __init__(
            self,
            index: __dataclass__init__fields__0__annotation,
            lhs: __dataclass__init__fields__1__annotation,
            rhs: __dataclass__init__fields__2__annotation,
            gaps: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'lhs', lhs)
            __dataclass__object_setattr(self, 'rhs', rhs)
            __dataclass__object_setattr(self, 'gaps', gaps)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('spec', 'start', 'end')), EqPlan(fields=('spec', 'start', 'end')), FrozenPlan(fiel"
        "ds=('spec', 'start', 'end'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('spec', 'start'"
        ", 'end'), cache=False), InitPlan(fields=(InitPlan.Field(name='spec', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='start', annotation=OpRef(name='init.fields.1.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='end', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=('spec', 'start', 'end'), kw_only_params="
        "(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='spec', kw_only=False, fn=None), ReprPlan.Field(name='start', kw_only=False, fn=None), ReprPlan.Fie"
        "ld(name='end', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2e12975bcdf1599f7d88099033ee7d57e6fdf45f',
    cls_names=(
        ('omlish.text.abnf.engines.tokens.specs', 'Token'),
    ),
)
def _process_dataclass__2e12975bcdf1599f7d88099033ee7d57e6fdf45f():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                spec=self.spec,
                start=self.start,
                end=self.end,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.spec == other.spec and
                self.start == other.start and
                self.end == other.end
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'spec',
            'start',
            'end',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.spec,
                self.start,
                self.end,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            spec: __dataclass__init__fields__0__annotation,
            start: __dataclass__init__fields__1__annotation,
            end: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'spec', spec)
            __dataclass__object_setattr(self, 'start', start)
            __dataclass__object_setattr(self, 'end', end)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"spec={self.spec!r}")
            parts.append(f"start={self.start!r}")
            parts.append(f"end={self.end!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('index', 'name', 'kind', 'channel', 'literal_value', 'literal_case_insensitive')),"
        " EqPlan(fields=('index', 'name', 'kind', 'channel', 'literal_value', 'literal_case_insensitive')), FrozenPlan("
        "fields=('index', 'name', 'kind', 'channel', 'literal_value', 'literal_case_insensitive'), allow_dynamic_dunder"
        "_attrs=False), HashPlan(action='add', fields=('index', 'name', 'kind', 'channel', 'literal_value', 'literal_ca"
        "se_insensitive'), cache=False), InitPlan(fields=(InitPlan.Field(name='index', annotation=OpRef(name='init.fiel"
        "ds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.field"
        "s.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='kind', annotation=OpRef(name='init.fields"
        ".2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='channel', annotation=OpRef(name='init.fiel"
        "ds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='literal_v"
        "alue', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='literal_case_insensitive', annotation=OpRef(name='init.fields.5.annotation'), de"
        "fault=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'index', 'name', 'kind', 'channel', 'literal_value', 'literal_case_insensitive'), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='index', kw_only=True"
        ", fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='kind', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='channel', kw_only=True, fn=None), ReprPlan.Field(name='literal_value', kw_only=True"
        ", fn=None), ReprPlan.Field(name='literal_case_insensitive', kw_only=True, fn=None)), id=False, terse=False, de"
        "fault_fn=None)))"
    ),
    plan_repr_sha1='ec5f5af5a6f008424120bcad0f0b73c8f53cf6ee',
    cls_names=(
        ('omlish.text.abnf.engines.tokens.specs', 'TokenSpec'),
    ),
)
def _process_dataclass__ec5f5af5a6f008424120bcad0f0b73c8f53cf6ee():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                index=self.index,
                name=self.name,
                kind=self.kind,
                channel=self.channel,
                literal_value=self.literal_value,
                literal_case_insensitive=self.literal_case_insensitive,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.index == other.index and
                self.name == other.name and
                self.kind == other.kind and
                self.channel == other.channel and
                self.literal_value == other.literal_value and
                self.literal_case_insensitive == other.literal_case_insensitive
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'index',
            'name',
            'kind',
            'channel',
            'literal_value',
            'literal_case_insensitive',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.index,
                self.name,
                self.kind,
                self.channel,
                self.literal_value,
                self.literal_case_insensitive,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            index: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            kind: __dataclass__init__fields__2__annotation,
            channel: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            literal_value: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            literal_case_insensitive: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'channel', channel)
            __dataclass__object_setattr(self, 'literal_value', literal_value)
            __dataclass__object_setattr(self, 'literal_case_insensitive', literal_case_insensitive)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"index={self.index!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"kind={self.kind!r}")
            parts.append(f"channel={self.channel!r}")
            parts.append(f"literal_value={self.literal_value!r}")
            parts.append(f"literal_case_insensitive={self.literal_case_insensitive!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('grammar', 'root', 'specs', 'token_rule_specs', 'token_rule_ops', 'literal_specs',"
        " 'skip_wrappers', 'parser_rules')), EqPlan(fields=('grammar', 'root', 'specs', 'token_rule_specs', 'token_rule"
        "_ops', 'literal_specs', 'skip_wrappers', 'parser_rules')), FrozenPlan(fields=('grammar', 'root', 'specs', 'tok"
        "en_rule_specs', 'token_rule_ops', 'literal_specs', 'skip_wrappers', 'parser_rules'), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('grammar', 'root', 'specs', 'token_rule_specs', 'token_rule_ops', 'li"
        "teral_specs', 'skip_wrappers', 'parser_rules'), cache=False), InitPlan(fields=(InitPlan.Field(name='grammar', "
        "annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='root', a"
        "nnotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='specs', a"
        "nnotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='token_rul"
        "e_specs', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='token_rule_ops', annotation=OpRef(name='init.fields.4.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='literal_specs', annotation=OpRef(name='init.fields.5.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='skip_wrappers', annotation=OpRef(name='init.fields.6.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='parser_rules', annotation=OpRef(name='init.fields.7.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None)), self_param='self', std_params=(), kw_only_params=('grammar', 'root', 'specs', 'token_rule_specs'"
        ", 'token_rule_ops', 'literal_specs', 'skip_wrappers', 'parser_rules'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='grammar', kw_only=True, fn=None"
        "), ReprPlan.Field(name='root', kw_only=True, fn=None), ReprPlan.Field(name='specs', kw_only=True, fn=None), Re"
        "prPlan.Field(name='token_rule_specs', kw_only=True, fn=None), ReprPlan.Field(name='token_rule_ops', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='literal_specs', kw_only=True, fn=None), ReprPlan.Field(name='skip_wrappers'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='parser_rules', kw_only=True, fn=None)), id=False, terse=False, "
        "default_fn=None)))"
    ),
    plan_repr_sha1='2b0d5afd5ad2c92259ae4d9e5c77a36d0b111d44',
    cls_names=(
        ('omlish.text.abnf.engines.tokens.specs', 'TokenizedGrammar'),
    ),
)
def _process_dataclass__2b0d5afd5ad2c92259ae4d9e5c77a36d0b111d44():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__7__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                grammar=self.grammar,
                root=self.root,
                specs=self.specs,
                token_rule_specs=self.token_rule_specs,
                token_rule_ops=self.token_rule_ops,
                literal_specs=self.literal_specs,
                skip_wrappers=self.skip_wrappers,
                parser_rules=self.parser_rules,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.grammar == other.grammar and
                self.root == other.root and
                self.specs == other.specs and
                self.token_rule_specs == other.token_rule_specs and
                self.token_rule_ops == other.token_rule_ops and
                self.literal_specs == other.literal_specs and
                self.skip_wrappers == other.skip_wrappers and
                self.parser_rules == other.parser_rules
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'grammar',
            'root',
            'specs',
            'token_rule_specs',
            'token_rule_ops',
            'literal_specs',
            'skip_wrappers',
            'parser_rules',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.grammar,
                self.root,
                self.specs,
                self.token_rule_specs,
                self.token_rule_ops,
                self.literal_specs,
                self.skip_wrappers,
                self.parser_rules,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            grammar: __dataclass__init__fields__0__annotation,
            root: __dataclass__init__fields__1__annotation,
            specs: __dataclass__init__fields__2__annotation,
            token_rule_specs: __dataclass__init__fields__3__annotation,
            token_rule_ops: __dataclass__init__fields__4__annotation,
            literal_specs: __dataclass__init__fields__5__annotation,
            skip_wrappers: __dataclass__init__fields__6__annotation,
            parser_rules: __dataclass__init__fields__7__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'grammar', grammar)
            __dataclass__object_setattr(self, 'root', root)
            __dataclass__object_setattr(self, 'specs', specs)
            __dataclass__object_setattr(self, 'token_rule_specs', token_rule_specs)
            __dataclass__object_setattr(self, 'token_rule_ops', token_rule_ops)
            __dataclass__object_setattr(self, 'literal_specs', literal_specs)
            __dataclass__object_setattr(self, 'skip_wrappers', skip_wrappers)
            __dataclass__object_setattr(self, 'parser_rules', parser_rules)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"grammar={self.grammar!r}")
            parts.append(f"root={self.root!r}")
            parts.append(f"specs={self.specs!r}")
            parts.append(f"token_rule_specs={self.token_rule_specs!r}")
            parts.append(f"token_rule_ops={self.token_rule_ops!r}")
            parts.append(f"literal_specs={self.literal_specs!r}")
            parts.append(f"skip_wrappers={self.skip_wrappers!r}")
            parts.append(f"parser_rules={self.parser_rules!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('s',)), EqPlan(fields=('s',)), FrozenPlan(fields=('s',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('s',), cache=False), InitPlan(fields=(InitPlan.Field(name='s', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('s"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='s', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='30a5dd74853303d917aae5f67d4e7189615d1440',
    cls_names=(
        ('omlish.text.abnf.meta', 'MetaGrammarRuleMatchVisitor.AltOp'),
        ('omlish.text.abnf.meta', 'MetaGrammarRuleMatchVisitor.QuotedString'),
        ('omlish.text.abnf.meta', 'MetaGrammarRuleMatchVisitor.RuleName'),
        ('omlish.text.abnf.opto', '_CaseInsensitiveStringLiteralRegexItem'),
        ('omlish.text.abnf.opto', '_StringLiteralRegexItem'),
    ),
)
def _process_dataclass__30a5dd74853303d917aae5f67d4e7189615d1440():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                s=self.s,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.s == other.s
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            's',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.s,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            s: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 's', s)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"s={self.s!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'arg')), EqPlan(fields=('name', 'arg')), FrozenPlan(fields=('name', 'arg')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'arg'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='arg', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=('name', 'arg'), kw_only_params=(), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), R"
        "eprPlan.Field(name='arg', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='77f9e223cd2b11b886449dea89b694036e037244',
    cls_names=(
        ('omlish.text.abnf.meta', 'MetaGrammarRuleMatchVisitor.Modifier'),
    ),
)
def _process_dataclass__77f9e223cd2b11b886449dea89b694036e037244():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                name=self.name,
                arg=self.arg,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.arg == other.arg
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'name',
            'arg',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.arg,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            arg: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arg', arg)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"arg={self.arg!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('lo', 'hi')), EqPlan(fields=('lo', 'hi')), FrozenPlan(fields=('lo', 'hi'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('lo', 'hi'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='lo', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='hi', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
        "self', std_params=('lo', 'hi'), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='lo', kw_only=False, fn=None), ReprPlan.Field(name='hi"
        "', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9104a51696bc4129d13d616118c0f732322e677c',
    cls_names=(
        ('omlish.text.abnf.ops', 'RangeLiteral.Range'),
    ),
)
def _process_dataclass__9104a51696bc4129d13d616118c0f732322e677c():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                lo=self.lo,
                hi=self.hi,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.lo == other.lo and
                self.hi == other.hi
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'lo',
            'hi',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.lo,
                self.hi,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            lo: __dataclass__init__fields__0__annotation,
            hi: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'lo', lo)
            __dataclass__object_setattr(self, 'hi', hi)
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"lo={self.lo!r}")
            parts.append(f"hi={self.hi!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('min', 'max')), EqPlan(fields=('min', 'max')), FrozenPlan(fields=('min', 'max'), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('min', 'max'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='min', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields"
        ".0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='max', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('min', 'max'), kw_o"
        "nly_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate_fns=())))"
    ),
    plan_repr_sha1='3dce49e08774c707abbc7a6513e35ccdc43001c9',
    cls_names=(
        ('omlish.text.abnf.ops', 'Repeat.Times'),
    ),
)
def _process_dataclass__3dce49e08774c707abbc7a6513e35ccdc43001c9():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                min=self.min,
                max=self.max,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.min == other.min and
                self.max == other.max
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'min',
            'max',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.min,
                self.max,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            min: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            max: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'min', min)
            __dataclass__object_setattr(self, 'max', max)
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), FrozenPlan(fields=(), allow_dynamic_dunder_attrs=False), Ha"
        "shPlan(action='add', fields=(), cache=False), InitPlan(fields=(), self_param='self', std_params=(), kw_only_pa"
        "rams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1f7edfe11f2b721d6a656c46e698fedc95461bb',
    cls_names=(
        ('omlish.text.abnf.opto', '_RegexItem'),
    ),
)
def _process_dataclass__e1f7edfe11f2b721d6a656c46e698fedc95461bb():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__()  # noqa

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return True

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash(())

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
        ) -> __dataclass__None:
            pass

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            return f"{self.__class__.__qualname__}()"

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ps',)), EqPlan(fields=('ps',)), FrozenPlan(fields=('ps',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('ps',), cache=False), InitPlan(fields=(InitPlan.Field(name='ps', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('ps',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='ps', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='f7dc3147180d5d4dc248e9c0d94aa0f1e503c4c7',
    cls_names=(
        ('omlish.text.abnf.opto', '_RegexRegexItem'),
    ),
)
def _process_dataclass__f7dc3147180d5d4dc248e9c0d94aa0f1e503c4c7():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                ps=self.ps,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ps == other.ps
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'ps',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.ps,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            ps: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ps', ps)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ps={self.ps!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass
