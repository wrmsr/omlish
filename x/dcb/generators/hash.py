import dataclasses as dc
import typing as ta

from omlish import check

from ..ops import AddMethodOp
from ..ops import Op
from ..ops import SetAttrOp
from .base import Generator
from .base import Plan
from .base import PlanContext
from .base import PlanResult
from .registry import register_generator_type
from .utils import build_attr_tuple_str


##


HashAction: ta.TypeAlias = ta.Literal['set_none', 'add', 'exception']


# See https://bugs.python.org/issue32929#msg312829 for an if-statement version of this table.
HASH_ACTIONS: ta.Mapping[tuple[bool, bool, bool, bool], HashAction | None] = {
    #
    # +-------------------------------------- unsafe_hash?
    # |      +------------------------------- eq?
    # |      |      +------------------------ frozen?
    # |      |      |      +----------------  has-explicit-hash?
    # v      v      v      v
    (False, False, False, False): None,
    (False, False, False, True): None,
    (False, False, True, False): None,
    (False, False, True, True): None,
    (False, True, False, False): 'set_none',
    (False, True, False, True): None,
    (False, True, True, False): 'add',
    (False, True, True, True): None,
    (True, False, False, False): 'add',
    (True, False, False, True): 'exception',
    (True, False, True, False): 'add',
    (True, False, True, True): 'exception',
    (True, True, False, False): 'add',
    (True, True, False, True): 'exception',
    (True, True, True, False): 'add',
    (True, True, True, True): 'exception',
}


def _raise_hash_action_exception(cls: type) -> ta.NoReturn:
    raise TypeError(f'Cannot overwrite attribute __hash__ in class {cls.__name__}')


CACHED_HASH_ATTR = '__dataclass_hash__'


#


@dc.dataclass(frozen=True)
class HashPlan(Plan):
    action: HashAction

    _: dc.KW_ONLY

    fields: tuple[str, ...] | None = None
    cache: bool | None = None


@register_generator_type(HashPlan)
class HashGenerator(Generator[HashPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[HashPlan] | None:
        class_hash = ctx.cls.__dict__.get('__hash__', dc.MISSING)
        has_explicit_hash = not (class_hash is dc.MISSING or (class_hash is None and '__eq__' in ctx.cls.__dict__))

        action = HASH_ACTIONS[(
            bool(ctx.cs.unsafe_hash),
            bool(ctx.cs.eq),
            bool(ctx.cs.frozen),
            has_explicit_hash,
        )]

        if action == 'set_none':
            return PlanResult(HashPlan(action))

        elif action == 'exception':
            _raise_hash_action_exception(ctx.cls)

        elif action == 'add':
            fields = tuple(
                f.name
                for f in ctx.ana.instance_fields
                if (f.compare if f.hash is None else f.hash)
            )

            return PlanResult(HashPlan(
                'add',
                fields=fields,
                cache=ctx.cs.cache_hash,
            ))

        elif action is None:
            return None

        else:
            raise ValueError(action)

    def generate(self, pl: HashPlan) -> ta.Iterable[Op]:
        if pl.action == 'set_none':
            return [SetAttrOp('__hash__', None, 'replace')]

        elif pl.action != 'add':
            raise ValueError(pl.action)

        lines = [
            'def __hash__(self):',
        ]

        self_tuple = build_attr_tuple_str('self', *check.not_none(pl.fields))

        if pl.cache:
            lines.extend([
                f'    try:',
                f'        return self.{CACHED_HASH_ATTR}',
                f'    except AttributeError:',
                f'        pass',
                f'    object.__setattr__(self, {CACHED_HASH_ATTR!r}, h := hash({self_tuple}))',
                f'    return h',
            ])
        else:
            lines.append(
                f'    return hash({self_tuple})',
            )

        lines.append('')

        return [
            AddMethodOp('__hash__', '\n'.join(lines)),
        ]
