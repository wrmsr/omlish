import copy
import typing as ta
import urllib.parse


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')


##


class _Missing:
    def __repr__(self) -> str:
        return 'no value'

    def __reduce__(self) -> str:
        return '_missing'


_missing = _Missing()


class TypeConversionDict(dict[K, V]):
    """
    Works like a regular dict but the :meth:`get` method can perform type conversions.  :class:`MultiDict` and
    :class:`CombinedMultiDict` are subclasses of this class and provide the same feature.
    """

    @ta.overload  # type: ignore[override]
    def get(self, key: K) -> V | None:
        ...

    @ta.overload
    def get(self, key: K, default: V) -> V:  # noqa
        ...

    @ta.overload
    def get(self, key: K, default: T) -> V | T:  # noqa
        ...

    @ta.overload
    def get(self, key: str, type: ta.Callable[[V], T]) -> T | None:  # noqa
        ...

    @ta.overload
    def get(self, key: str, default: T, type: ta.Callable[[V], T]) -> T:  # noqa
        ...

    def get(  # type: ignore[misc]
            self,
            key: K,
            default: V | T | None = None,
            type: ta.Callable[[V], T] | None = None,  # noqa
    ) -> V | T | None:
        """
        Return the default value if the requested data doesn't exist. If `type` is provided and is a callable it should
        convert the value, return it or raise a :exc:`ValueError` if that is not possible.  In this case the function
        will return the default as if the value was not found:

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key can't be looked up.  If not further specified `None`
            is returned.
        :param type: A callable that is used to cast the value in the :class:`MultiDict`.  If a :exc:`ValueError` or a
            :exc:`TypeError` is raised by this callable the default value is returned.
        """

        try:
            rv = self[key]
        except KeyError:
            return default

        if type is None:
            return rv

        try:
            return type(rv)
        except (ValueError, TypeError):
            return default


class MultiDict(TypeConversionDict[K, V]):
    """
    A :class:`MultiDict` is a dictionary subclass customized to deal with multiple values for the same key which is for
    example used by the parsing functions in the wrappers.  This is necessary because some HTML form elements pass
    multiple values for the same key.

    :class:`MultiDict` implements all standard dictionary methods. Internally, it saves all values for a key as a list,
    but the standard dict access methods will only return the first value for a key. If you want to gain access to the
    other values, too, you have to use the `list` methods as explained below.

    Basic Usage:

    >>> d = MultiDict([('a', 'b'), ('a', 'c')])
    >>> d
    MultiDict([('a', 'b'), ('a', 'c')])
    >>> d['a']
    'b'
    >>> d.getlist('a')
    ['b', 'c']
    >>> 'a' in d
    True

    It behaves like a normal dict thus all dict functions will only return the first value when multiple values for one
    key are found.

    From Werkzeug 0.3 onwards, the `KeyError` raised by this class is also a subclass of the
    :exc:`~exceptions.BadRequest` HTTP exception and will render a page for a ``400 BAD REQUEST`` if caught in a
    catch-all for HTTP exceptions.

    A :class:`MultiDict` can be constructed from an iterable of ``(key, value)`` tuples, a dict, a :class:`MultiDict` or
    from Werkzeug 0.2 onwards some keyword parameters.

    :param mapping: the initial value for the :class:`MultiDict`.  Either a regular dict, an iterable of ``(key,
    value)`` tuples or `None`.
    """

    def __init__(
            self,
            mapping: ta.Union[
                'MultiDict[K, V]',
                ta.Mapping[K, V | list[V] | tuple[V, ...] | set[V]],
                ta.Iterable[tuple[K, V]],
                None,
            ] = None,
    ) -> None:
        if mapping is None:
            super().__init__()
        elif isinstance(mapping, MultiDict):
            super().__init__((k, vs[:]) for k, vs in mapping.lists())
        elif isinstance(mapping, ta.Mapping):
            tmp = {}
            for key, value in mapping.items():
                if isinstance(value, (list, tuple, set)):
                    value = list(value)

                    if not value:
                        continue
                else:
                    value = [value]
                tmp[key] = value
            super().__init__(tmp)  # type: ignore[arg-type]
        else:
            tmp = {}
            for key, value in mapping:
                tmp.setdefault(key, []).append(value)
            super().__init__(tmp)  # type: ignore[arg-type]

    def __getstate__(self) -> ta.Any:
        return dict(self.lists())

    def __setstate__(self, value: ta.Any) -> None:
        super().clear()
        super().update(value)

    def __iter__(self) -> ta.Iterator[K]:
        # https://github.com/python/cpython/issues/87412
        # If __iter__ is not overridden, Python uses a fast path for dict(md), taking the data directly and getting
        # lists of values, rather than calling __getitem__ and getting only the first value.
        return super().__iter__()

    def __getitem__(self, key: K) -> V:
        """
        Return the first data value for this key; raises KeyError if not found.

        :param key: The key to be looked up.
        :raise KeyError: if the key does not exist.
        """

        if key in self:
            lst = super().__getitem__(key)
            if len(lst) > 0:  # type: ignore[arg-type]
                return lst[0]  # type: ignore[index]
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """
        Like :meth:`add` but removes an existing key first.

        :param key: the key for the value.
        :param value: the value to set.
        """

        super().__setitem__(key, [value])  # type: ignore[assignment]

    def add(self, key: K, value: V) -> None:
        """
        Adds a new value for the key.

        :param key: the key for the value.
        :param value: the value to add.
        """

        super().setdefault(key, []).append(value)  # type: ignore[arg-type,attr-defined]

    @ta.overload
    def getlist(self, key: K) -> list[V]:
        ...

    @ta.overload
    def getlist(self, key: K, type: ta.Callable[[V], T]) -> list[T]:
        ...

    def getlist(
            self,
            key: K,
            type: ta.Callable[[V], T] | None = None,  # noqa
    ) -> list[V] | list[T]:
        """
        Return the list of items for a given key. If that key is not in the `MultiDict`, the return value will be an
        empty list.  Just like `get`, `getlist` accepts a `type` parameter.  All items will be converted with the
        callable defined there.

        :param key: The key to be looked up.
        :param type: Callable to convert each value. If a ``ValueError`` or ``TypeError`` is raised, the value is
            omitted.
        :return: a :class:`list` of all the values for the key.
        """

        try:
            rv: list[V] = super().__getitem__(key)  # type: ignore[assignment]
        except KeyError:
            return []
        if type is None:
            return list(rv)
        result = []
        for item in rv:
            try:
                result.append(type(item))
            except (ValueError, TypeError):
                pass
        return result

    def setlist(self, key: K, new_list: ta.Iterable[V]) -> None:
        """
        Remove the old values for a key and add new ones.  Note that the list you pass the values in will be
        shallow-copied before it is inserted in the dictionary.

        >>> d = MultiDict()
        >>> d.setlist('foo', ['1', '2'])
        >>> d['foo']
        '1'
        >>> d.getlist('foo')
        ['1', '2']

        :param key: The key for which the values are set.
        :param new_list: An iterable with the new values for the key.  Old values are removed first.
        """

        super().__setitem__(key, list(new_list))  # type: ignore[assignment]

    @ta.overload
    def setdefault(self, key: K) -> None:
        ...

    @ta.overload
    def setdefault(self, key: K, default: V) -> V:
        ...

    def setdefault(self, key: K, default: V | None = None) -> V | None:
        """
        Returns the value for the key if it is in the dict, otherwise it returns `default` and sets that value for
        `key`.

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key is not in the dict.  If not further specified it's
            `None`.
        """

        if key not in self:
            self[key] = default  # type: ignore[assignment]

        return self[key]

    def setlistdefault(
            self,
            key: K,
            default_list: ta.Iterable[V] | None = None,
    ) -> list[V]:
        """
        Like `setdefault` but sets multiple values.  The list returned is not a copy, but the list that is actually used
        internally.  This means that you can put new values into the dict by appending items to the list:

        >>> d = MultiDict({"foo": 1})
        >>> d.setlistdefault("foo").extend([2, 3])
        >>> d.getlist("foo")
        [1, 2, 3]

        :param key: The key to be looked up.
        :param default_list: An iterable of default values.  It is either copied (in case it was a list) or converted
            into a list before returned.
        :return: a :class:`list`
        """

        if key not in self:
            super().__setitem__(key, list(default_list or ()))  # type: ignore[assignment]

        return super().__getitem__(key)  # type: ignore[return-value]

    def items(self, multi: bool = False) -> ta.Iterable[tuple[K, V]]:  # type: ignore[override]
        """
        Return an iterator of ``(key, value)`` pairs.

        :param multi: If set to `True` the iterator returned will have a pair for each value of each key.  Otherwise it
            will only contain pairs for the first value of each key.
        """

        values: list[V]

        for key, values in super().items():  # type: ignore[assignment]
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]

    def lists(self) -> ta.Iterable[tuple[K, list[V]]]:
        """
        Return a iterator of ``(key, values)`` pairs, where values is the list of all values associated with the key.
        """

        values: list[V]

        for key, values in super().items():  # type: ignore[assignment]
            yield key, list(values)

    def values(self) -> ta.Iterable[V]:  # type: ignore[override]
        """Returns an iterator of the first value on every key's value list."""

        values: list[V]

        for values in super().values():  # type: ignore[assignment]
            yield values[0]

    def listvalues(self) -> ta.Iterable[list[V]]:
        """
        Return an iterator of all values associated with a key.  Zipping :meth:`keys` and this is the same as calling
        :meth:`lists`:

        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> zip(d.keys(), d.listvalues()) == d.lists()
        True
        """

        return super().values()  # type: ignore[return-value]

    def copy(self) -> ta.Self:
        """Return a shallow copy of this object."""

        return self.__class__(self)

    def deepcopy(self, memo: ta.Any = None) -> ta.Self:
        """Return a deep copy of this object."""

        return self.__class__(copy.deepcopy(self.to_dict(flat=False), memo))

    @ta.overload
    def to_dict(self) -> dict[K, V]:
        ...

    @ta.overload
    def to_dict(self, flat: ta.Literal[False]) -> dict[K, list[V]]:
        ...

    def to_dict(self, flat: bool = True) -> dict[K, V] | dict[K, list[V]]:
        """
        Return the contents as regular dict.  If `flat` is `True` the returned dict will only have the first item
        present, if `flat` is `False` all values will be returned as lists.

        :param flat: If set to `False` the dict returned will have lists with all the values in it.  Otherwise it will
            only contain the first value for each key.
        :return: a :class:`dict`
        """

        if flat:
            return dict(self.items())
        return dict(self.lists())

    def update(  # type: ignore[override]  # noqa
            self,
            mapping: ta.Union[
                    'MultiDict[K, V]',
                    ta.Mapping[K, V | list[V] | tuple[V, ...] | set[V]],
                    ta.Iterable[tuple[K, V]],
            ],
    ) -> None:
        """
        update() extends rather than replaces existing key lists:

        >>> a = MultiDict({'x': 1})
        >>> b = MultiDict({'x': 2, 'y': 3})
        >>> a.update(b)
        >>> a
        MultiDict([('y', 3), ('x', 1), ('x', 2)])

        If the value list for a key in ``other_dict`` is empty, no new values will be added to the dict and the key will
        not be created:

        >>> x = {'empty_list': []}
        >>> y = MultiDict()
        >>> y.update(x)
        >>> y
        MultiDict([])
        """

        for key, value in iter_multi_items(mapping):
            self.add(key, value)

    def __or__(  # type: ignore[override]
            self,
            other: ta.Mapping[K, V | list[V] | tuple[V, ...] | set[V]],
    ) -> 'MultiDict[K, V]':
        if not isinstance(other, ta.Mapping):
            return NotImplemented  # type: ignore[unreachable]

        rv = self.copy()
        rv.update(other)
        return rv

    def __ior__(  # type: ignore[override]
            self,
            other: ta.Mapping[K, V | list[V] | tuple[V, ...] | set[V]] | ta.Iterable[tuple[K, V]],
    ) -> ta.Self:
        if not isinstance(other, (ta.Mapping, ta.Iterable)):
            return NotImplemented  # type: ignore[unreachable]

        self.update(other)
        return self

    @ta.overload
    def pop(self, key: K) -> V:
        ...

    @ta.overload
    def pop(self, key: K, default: V) -> V:
        ...

    @ta.overload
    def pop(self, key: K, default: T) -> V | T:
        ...

    def pop(
            self,
            key: K,
            default: V | T = _missing,  # type: ignore[assignment]
    ) -> V | T:
        """
        Pop the first item for a list on the dict.  Afterwards the key is removed from the dict, so additional values
        are discarded:

        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> d.pop("foo")
        1
        >>> "foo" in d
        False

        :param key: the key to pop.
        :param default: if provided the value to return if the key was not in the dictionary.
        """

        lst: list[V]

        try:
            lst = super().pop(key)  # type: ignore[assignment]

            if len(lst) == 0:
                raise KeyError(key)  # Noqa

            return lst[0]

        except KeyError:
            if default is not _missing:
                return default

            raise KeyError(key) from None

    def popitem(self) -> tuple[K, V]:
        """Pop an item from the dict."""

        item: tuple[K, list[V]]

        try:
            item = super().popitem()  # type: ignore[assignment]

            if len(item[1]) == 0:
                raise KeyError(item[0])  # noqa

            return item[0], item[1][0]

        except KeyError as e:
            raise KeyError(e.args[0]) from None

    def poplist(self, key: K) -> list[V]:
        """Pop the list for a key from the dict.  If the key is not in the dict an empty list is returned."""

        return super().pop(key, [])  # type: ignore[return-value]

    def popitemlist(self) -> tuple[K, list[V]]:
        """Pop a ``(key, list)`` tuple from the dict."""

        try:
            return super().popitem()  # type: ignore[return-value]
        except KeyError as e:
            raise KeyError(e.args[0]) from None

    def __copy__(self) -> ta.Self:
        return self.copy()

    def __deepcopy__(self, memo: ta.Any) -> ta.Self:
        return self.deepcopy(memo=memo)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({list(self.items(multi=True))!r})'


def iter_multi_items(
        mapping: ta.Union[
            'MultiDict[K, V]',
            ta.Mapping[K, V | list[V] | tuple[V, ...] | set[V]],
            ta.Iterable[tuple[K, V]],
        ],
) -> ta.Iterator[tuple[K, V]]:
    """
    Iterates over the items of a mapping yielding keys and values without dropping any from more complex structures.
    """

    if isinstance(mapping, MultiDict):
        yield from mapping.items(multi=True)
    elif isinstance(mapping, ta.Mapping):
        for key, value in mapping.items():
            if isinstance(value, (list, tuple, set)):
                for v in value:
                    yield key, v
            else:
                yield key, value
    else:
        yield from mapping


##


def urlencode(query: ta.Mapping[str, str] | ta.Iterable[tuple[str, str]]) -> str:
    items = [x for x in iter_multi_items(query) if x[1] is not None]
    # safe = https://url.spec.whatwg.org/#percent-encoded-bytes
    return urllib.parse.urlencode(items, safe="!$'()*,/:;?@")
