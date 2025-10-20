import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..binder import bind
from ..elements import Elements
from ..elements import as_elements
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from ..multis import MapBinding
from ..multis import SetBinder
from ..multis import SetBinding
from ..multis import is_map_multi_key
from ..multis import is_set_multi_key
from ..providers import FnProvider
from .id import Id


ItemT = ta.TypeVar('ItemT')


##


def bind_set_entry_const(
        multi_key: ta.Any,
        obj: ta.Any,
        *,
        tag: ta.Any | None = None,
) -> Elements:
    multi_key = as_key(multi_key)
    check.arg(is_set_multi_key(multi_key))

    if tag is None:
        tag = Id(id(obj), tag=multi_key.tag)
    obj_key: Key = Key(type(obj), tag=tag)

    return as_elements(
        bind(obj_key, to_const=obj),
        SetBinding(multi_key, obj_key),
    )


def bind_map_entry_const(
        multi_key: ta.Any,
        map_key: ta.Any,
        obj: ta.Any,
        *,
        tag: ta.Any | None = None,
) -> Elements:
    multi_key = as_key(multi_key)
    check.arg(is_map_multi_key(multi_key))

    if tag is None:
        tag = Id(id(obj), tag=multi_key.tag)
    obj_key: Key = Key(type(obj), tag=tag)

    return as_elements(
        bind(obj_key, to_const=obj),
        MapBinding(multi_key, map_key, obj_key),
    )


##


@ta.final
class ItemsBinderHelper(ta.Generic[ItemT]):
    def __init__(self, items_cls: ta.Any) -> None:
        self._items_cls = items_cls

    @cached.property
    def _item_rty(self) -> rfl.Type:
        rty = check.isinstance(rfl.type_(rfl.get_orig_class(self)), rfl.Generic)
        check.is_(rty.cls, self.__class__)
        return check.single(rty.args)

    @dc.dataclass(frozen=True, eq=False)
    class _ItemsBox:
        vs: ta.Sequence

    @cached.property
    def _items_box(self) -> type[_ItemsBox]:
        if isinstance(item_rty := self._item_rty, type):
            sfx = item_rty.__qualname__
        else:
            sfx = str(item_rty).replace("'", '')

        return lang.new_type(  # noqa
            f'{ItemsBinderHelper._ItemsBox.__qualname__}${sfx}@{id(self):x}',
            (ItemsBinderHelper._ItemsBox,),
            {},
        )

    @cached.property
    def _set_key(self) -> Key:
        return as_key(ta.AbstractSet[self._item_rty])  # type: ignore

    def bind_item_consts(self, *items: ItemT) -> Elements:
        return as_elements(
            bind_set_entry_const(self._set_key, self._items_box(items)),
        )

    @dc.dataclass(frozen=True, eq=False)
    @dc.extra_class_params(repr_id=True)
    class _ItemTag:
        pass

    def bind_item(self, **kwargs: ta.Any) -> Elements:
        tag = ItemsBinderHelper._ItemTag()
        item_key: Key = Key(ta.Any, tag=tag)
        items_box_key: Key = Key(self._items_box, tag=tag)
        return as_elements(
            bind(item_key, **kwargs),
            bind(
                items_box_key,
                to_provider=FnProvider(KwargsTarget.of(
                    lambda v: self._items_box([v]),
                    v=item_key,
                )),
            ),
            SetBinding(self._set_key, items_box_key),
        )

    def bind_items_provider(self, **kwargs: ta.Any) -> Elements:
        return as_elements(
            SetBinder[self._item_rty](),  # type: ignore
            bind(
                self._items_cls,
                to_provider=FnProvider(KwargsTarget.of(
                    lambda s: self._items_cls([v for i in s for v in i.vs]),
                    s=self._set_key,
                )),
                **kwargs,
            ),
        )


items_binder_helper = ItemsBinderHelper
