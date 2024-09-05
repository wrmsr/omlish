"""
https://github.com/pandas-dev/pandas/tree/bc9b1c3c4b979978dcdef42b900aa633cfeee28e/pandas/io/parsers
https://github.com/pandas-dev/pandas/blob/bc9b1c3c4b979978dcdef42b900aa633cfeee28e/pandas/io/parsers/python_parser.py#L96
https://github.com/pandas-dev/pandas/blob/bc9b1c3c4b979978dcdef42b900aa633cfeee28e/pandas/io/parsers/readers.py#L95
"""
# BSD 3-Clause License
#
# Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team All rights
# reserved.
#
# Copyright (c) 2011-2024, Open source contributors.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import collections.abc
import copy
import csv
import datetime
import enum
import inspect
import io
import itertools
import os
import re
import sys
import types
import typing as ta
import warnings

import numpy as np


T = ta.TypeVar('T')
HashableT = ta.TypeVar('HashableT', bound=ta.Hashable)
SequenceT = ta.TypeVar('SequenceT', bound=ta.Sequence)


# region _typing.py


class ExtensionDtype:
    def __new__(cls, *args, **kwargs):
        raise TypeError


class ExtensionArray:
    def __new__(cls, *args, **kwargs):
        raise TypeError


PythonScalar = ta.Union[str, float, bool]
Scalar = ta.Union[PythonScalar, np.datetime64, np.timedelta64, datetime.date]

AnyStr_co = ta.TypeVar("AnyStr_co", str, bytes, covariant=True)
AnyStr_contra = ta.TypeVar("AnyStr_contra", str, bytes, contravariant=True)

IndexLabel = ta.Union[ta.Hashable, ta.Sequence[ta.Hashable]]

ArrayLike = ta.Union["ExtensionArray", np.ndarray]
ArrayLikeT = ta.TypeVar("ArrayLikeT", "ExtensionArray", np.ndarray)
AnyArrayLike = ta.Union[ArrayLike, "Index", "Series"]

NpDtype = ta.Union[str, np.dtype, ta.Type[ta.Union[str, complex, bool, object]]]
Dtype = ta.Union["ExtensionDtype", NpDtype]
AstypeArg = ta.Union["ExtensionDtype", "npt.DTypeLike"]

DtypeArg = ta.Union[Dtype, ta.Mapping[ta.Hashable, Dtype]]

DtypeBackend = ta.Literal["pyarrow", "numpy_nullable"]

FilePath = ta.Union[str, os.PathLike[str]]


_T_co = ta.TypeVar("_T_co", covariant=True)


class SequenceNotStr(ta.Protocol[_T_co]):
    @ta.overload
    def __getitem__(self, index: ta.SupportsIndex, /) -> _T_co: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[_T_co]: ...  # noqa

    def __contains__(self, value: object, /) -> bool: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> ta.Iterator[_T_co]: ...

    def index(self, value: ta.Any, start: int = ..., stop: int = ..., /) -> int: ...

    def count(self, value: ta.Any, /) -> int: ...

    def __reversed__(self) -> ta.Iterator[_T_co]: ...


ListLike = ta.Union[AnyArrayLike, SequenceNotStr, range]


UsecolsArgType = ta.Union[
    SequenceNotStr[ta.Hashable],
    range,
    AnyArrayLike,
    ta.Callable[[HashableT], bool],
    None,
]


class BaseBuffer(ta.Protocol):
    @property
    def mode(self) -> str:
        # for _get_filepath_or_buffer
        ...

    def seek(self, __offset: int, __whence: int = ...) -> int:
        # with one argument: gzip.GzipFile, bz2.BZ2File
        # with two arguments: zip.ZipFile, read_sas
        ...

    def seekable(self) -> bool:
        # for bz2.BZ2File
        ...

    def tell(self) -> int:
        # for zip.ZipFile, read_stata, to_stata
        ...


class ReadBuffer(BaseBuffer, ta.Protocol[AnyStr_co]):
    def read(self, __n: int = ...) -> AnyStr_co:
        # for BytesIOWrapper, gzip.GzipFile, bz2.BZ2File
        ...


class ReadCsvBuffer(ReadBuffer[AnyStr_co], ta.Protocol):
    def __iter__(self) -> ta.Iterator[AnyStr_co]:
        # for engine=python
        ...

    def fileno(self) -> int:
        # for _MMapWrapper
        ...

    def readline(self) -> AnyStr_co:
        # for engine=python
        ...

    @property
    def closed(self) -> bool:
        # for engine=pyarrow
        ...


CSVEngine = ta.Literal["c", "python", "pyarrow", "python-fwf"]

CompressionDict = dict[str, ta.Any]
CompressionOptions = ta.Optional[
    ta.Union[ta.Literal["infer", "gzip", "bz2", "zip", "xz", "zstd", "tar"], CompressionDict]
]

StorageOptions = ta.Optional[dict[str, ta.Any]]


# endregion


# region lib


class _NoDefault(enum.Enum):
    # We make this an Enum
    # 1) because it round-trips through pickle correctly (see GH#40397)
    # 2) because mypy does not understand singletons
    no_default = "NO_DEFAULT"

    def __repr__(self) -> str:
        return "<no_default>"


no_default = _NoDefault.no_default  # Sentinel indicating the default value.
NoDefault = ta.Literal[_NoDefault.no_default]


def is_bool(obj: object) -> bool:
    return isinstance(obj, (bool, np.bool_))


def is_array(obj: object) -> bool:
    return isinstance(obj, np.ndarray)


def is_list_like(obj: object, allow_sets: bool) -> bool:
    # first, performance short-cuts for the most common cases
    if is_array(obj):
        # exclude zero-dimensional numpy arrays, effectively scalars
        return bool(obj.shape)  # noqa
    elif isinstance(obj, list):
        return True
    # then the generic implementation
    return (
        # equiv: `isinstance(obj, abc.Iterable)`
            getattr(obj, "__iter__", None) is not None and not isinstance(obj, type)
            # we do not count strings/unicode/bytes as list-like
            # exclude Generic types that have __iter__
            and not isinstance(obj, (str, bytes, ta._GenericAlias))  # noqa
            # exclude zero-dimensional duck-arrays, effectively scalars
            and not (hasattr(obj, "ndim") and obj.ndim == 0)
            # exclude sets if allow_sets is False
            and not (allow_sets is False and isinstance(obj, collections.abc.Set))
    )


def is_integer(obj: object) -> bool:
    return isinstance(obj, (int, np.integer)) and not isinstance(obj, (bool, np.timedelta64))


def is_dict_like(obj: object) -> bool:
    """
    Check if the object is dict-like.

    Parameters
    ----------
    obj : The object to check

    Returns
    -------
    bool
        Whether `obj` has dict-like properties.

    Examples
    --------
    >>> from pandas.api.types import is_dict_like
    >>> is_dict_like({1: 2})
    True
    >>> is_dict_like([1, 2, 3])
    False
    >>> is_dict_like(dict)
    False
    >>> is_dict_like(dict())
    True
    """
    dict_like_attrs = ("__getitem__", "keys", "__contains__")
    return (
        all(hasattr(obj, attr) for attr in dict_like_attrs)
        # [GH 25196] exclude classes
        and not isinstance(obj, type)
    )


# endregion


def is_file_like(obj: object) -> bool:
    """
    Check if the object is a file-like object.

    For objects to be considered file-like, they must
    be an iterator AND have either a `read` and/or `write`
    method as an attribute.

    Note: file-like objects must be iterable, but
    iterable objects need not be file-like.

    Parameters
    ----------
    obj : The object to check

    Returns
    -------
    bool
        Whether `obj` has file-like properties.

    Examples
    --------
    >>> import io
    >>> from pandas.api.types import is_file_like
    >>> buffer = io.StringIO("data")
    >>> is_file_like(buffer)
    True
    >>> is_file_like([1, 2, 3])
    False
    """
    if not (hasattr(obj, "read") or hasattr(obj, "write")):
        return False

    return bool(hasattr(obj, "__iter__"))


def find_stack_level() -> int:
    """
    Find the first place in the stack that is not inside pandas
    (tests notwithstanding).
    """

    import pandas as pd

    pkg_dir = os.path.dirname(pd.__file__)
    test_dir = os.path.join(pkg_dir, "tests")

    # https://stackoverflow.com/questions/17407119/python-inspect-stack-is-slow
    frame: types.FrameType | None = inspect.currentframe()
    try:
        n = 0
        while frame:
            filename = inspect.getfile(frame)
            if filename.startswith(pkg_dir) and not filename.startswith(test_dir):
                frame = frame.f_back
                n += 1
            else:
                break
    finally:
        # See note in
        # https://docs.python.org/3/library/inspect.html#inspect.Traceback
        del frame
    return n


# region errors.py


class ParserError(ValueError):
    pass


class EmptyDataError(ValueError):
    pass


#


class ParserWarning(Warning):
    pass


# endregion


# region io/common.py


def dedup_names(
        names: ta.Sequence[ta.Hashable], is_potential_multiindex: bool
) -> ta.Sequence[ta.Hashable]:
    """
    Rename column names if duplicates exist.

    Currently the renaming is done by appending a period and an autonumeric,
    but a custom pattern may be supported in the future.

    Examples
    --------
    >>> dedup_names(["x", "y", "x", "x"], is_potential_multiindex=False)
    ['x', 'y', 'x.1', 'x.2']
    """
    names = list(names)  # so we can index
    counts: collections.defaultdict[ta.Hashable, int] = collections.defaultdict(int)

    for i, col in enumerate(names):
        cur_count = counts[col]

        while cur_count > 0:
            counts[col] = cur_count + 1

            if is_potential_multiindex:
                # for mypy
                assert isinstance(col, tuple)
                col = col[:-1] + (f"{col[-1]}.{cur_count}",)
            else:
                col = f"{col}.{cur_count}"
            cur_count = counts[col]

        names[i] = col
        counts[col] = cur_count + 1

    return names


# endregion


# region io/parsers/base_parser.py


class ParserBase:
    class BadLineHandleMethod(enum.Enum):
        ERROR = 0
        WARN = 1
        SKIP = 2

    _implicit_index: bool
    _first_chunk: bool
    keep_default_na: bool
    dayfirst: bool
    cache_dates: bool
    usecols_dtype: str | None

    def __init__(self, kwds) -> None:
        self._implicit_index = False

        self.names = kwds.get("names")
        self.orig_names: ta.Sequence[ta.Hashable] | None = None

        self.index_col = kwds.get("index_col", None)
        self.unnamed_cols: set = set()
        self.index_names: ta.Sequence[ta.Hashable] | None = None
        self.col_names: ta.Sequence[ta.Hashable] | None = None

        parse_dates = kwds.pop("parse_dates", False)
        if parse_dates is None or is_bool(parse_dates):
            parse_dates = bool(parse_dates)
        elif not isinstance(parse_dates, list):
            raise TypeError(
                "Only booleans and lists are accepted "
                "for the 'parse_dates' parameter"
            )
        self.parse_dates: bool | list = parse_dates
        self.date_parser = kwds.pop("date_parser", no_default)
        self.date_format = kwds.pop("date_format", None)
        self.dayfirst = kwds.pop("dayfirst", False)

        self.na_values = kwds.get("na_values")
        self.na_fvalues = kwds.get("na_fvalues")
        self.na_filter = kwds.get("na_filter", False)
        self.keep_default_na = kwds.get("keep_default_na", True)

        self.dtype = copy.copy(kwds.get("dtype", None))
        self.converters = kwds.get("converters")
        self.dtype_backend = kwds.get("dtype_backend")

        self.true_values = kwds.get("true_values")
        self.false_values = kwds.get("false_values")
        self.cache_dates = kwds.pop("cache_dates", True)

        # validate header options for mi
        self.header = kwds.get("header")
        if is_list_like(self.header, allow_sets=False):
            if kwds.get("usecols"):
                raise ValueError(
                    "cannot specify usecols when specifying a multi-index header"
                )
            if kwds.get("names"):
                raise ValueError(
                    "cannot specify names when specifying a multi-index header"
                )

            # validate index_col that only contains integers
            if self.index_col is not None:
                # In this case we can pin down index_col as list[int]
                if is_integer(self.index_col):
                    self.index_col = [self.index_col]
                elif not (
                        is_list_like(self.index_col, allow_sets=False)
                        and all(map(is_integer, self.index_col))
                ):
                    raise ValueError(
                        "index_col must only contain integers of column positions "
                        "when specifying a multi-index header"
                    )
                else:
                    self.index_col = list(self.index_col)

        self._first_chunk = True

        self.usecols, self.usecols_dtype = _validate_usecols_arg(kwds["usecols"])

        # Fallback to error to pass a sketchy test(test_override_set_noconvert_columns)
        # Normally, this arg would get pre-processed earlier on
        self.on_bad_lines = kwds.get("on_bad_lines", self.BadLineHandleMethod.ERROR)

    def close(self) -> None:
        pass

    @ta.final
    def _should_parse_dates(self, i: int) -> bool:
        if isinstance(self.parse_dates, bool):
            return self.parse_dates
        else:
            if self.index_names is not None:
                name = self.index_names[i]
            else:
                name = None
            j = i if self.index_col is None else self.index_col[i]

            return (j in self.parse_dates) or (
                    name is not None and name in self.parse_dates
            )

    @ta.final
    def _extract_multi_indexer_columns(
            self,
            header,
            index_names: ta.Sequence[ta.Hashable] | None,
            passed_names: bool = False,
    ) -> tuple[
        ta.Sequence[ta.Hashable], ta.Sequence[ta.Hashable] | None, ta.Sequence[ta.Hashable] | None, bool
    ]:
        """
        Extract and return the names, index_names, col_names if the column
        names are a MultiIndex.

        Parameters
        ----------
        header: list of lists
            The header rows
        index_names: list, optional
            The names of the future index
        passed_names: bool, default False
            A flag specifying if names where passed

        """
        if len(header) < 2:
            return header[0], index_names, None, passed_names

        # the names are the tuples of the header that are not the index cols
        # 0 is the name of the index, assuming index_col is a list of column
        # numbers
        ic = self.index_col
        if ic is None:
            ic = []

        if not isinstance(ic, (list, tuple, np.ndarray)):
            ic = [ic]
        sic = set(ic)

        # clean the index_names
        index_names = header.pop(-1)
        index_names, _, _ = self._clean_index_names(index_names, self.index_col)

        # extract the columns
        field_count = len(header[0])

        # check if header lengths are equal
        if not all(len(header_iter) == field_count for header_iter in header[1:]):
            raise ParserError("Header rows must have an equal number of columns.")

        def extract(r):
            return tuple(r[i] for i in range(field_count) if i not in sic)

        columns = list(zip(*(extract(r) for r in header)))
        names = columns.copy()
        for single_ic in sorted(ic):
            names.insert(single_ic, single_ic)

        # Clean the column names (if we have an index_col).
        if len(ic):
            col_names = [
                r[ic[0]]
                if ((r[ic[0]] is not None) and r[ic[0]] not in self.unnamed_cols)
                else None
                for r in header
            ]
        else:
            col_names = [None] * len(header)

        passed_names = True

        return names, index_names, col_names, passed_names

    @ta.final
    def _maybe_make_multi_index_columns(
            self,
            columns: SequenceT,
            col_names: ta.Sequence[ta.Hashable] | None = None,
    ) -> SequenceT | MultiIndex:
        # possibly create a column mi here
        if is_potential_multi_index(columns):
            columns_mi = ta.cast("ta.Sequence[tuple[Hashable, ...]]", columns)
            return MultiIndex.from_tuples(columns_mi, names=col_names)
        return columns

    @ta.final
    def _make_index(
            self, alldata, columns, indexnamerow: list[Scalar] | None = None
    ) -> tuple[Index | None, ta.Sequence[ta.Hashable] | MultiIndex]:
        index: Index | None
        if isinstance(self.index_col, list) and len(self.index_col):
            to_remove = []
            indexes = []
            for idx in self.index_col:
                if isinstance(idx, str):
                    raise ValueError(f"Index {idx} invalid")
                to_remove.append(idx)
                indexes.append(alldata[idx])
            # remove index items from content and columns, don't pop in
            # loop
            for i in sorted(to_remove, reverse=True):
                alldata.pop(i)
                if not self._implicit_index:
                    columns.pop(i)
            index = self._agg_index(indexes)

            # add names for the index
            if indexnamerow:
                coffset = len(indexnamerow) - len(columns)
                index = index.set_names(indexnamerow[:coffset])
        else:
            index = None

        # maybe create a mi on the columns
        columns = self._maybe_make_multi_index_columns(columns, self.col_names)

        return index, columns

    @ta.final
    def _clean_mapping(self, mapping):
        """converts col numbers to names"""
        if not isinstance(mapping, dict):
            return mapping
        clean = {}
        # for mypy
        assert self.orig_names is not None

        for col, v in mapping.items():
            if isinstance(col, int) and col not in self.orig_names:
                col = self.orig_names[col]
            clean[col] = v
        if isinstance(mapping, collections.defaultdict):
            remaining_cols = set(self.orig_names) - set(clean.keys())
            clean.update({col: mapping[col] for col in remaining_cols})
        return clean

    @ta.final
    def _agg_index(self, index) -> Index:
        arrays = []
        converters = self._clean_mapping(self.converters)
        clean_dtypes = self._clean_mapping(self.dtype)

        if self.index_names is not None:
            names: ta.Iterable = self.index_names
        else:
            names = itertools.cycle([None])
        for i, (arr, name) in enumerate(zip(index, names)):
            if self._should_parse_dates(i):
                arr = date_converter(
                    arr,
                    col=self.index_names[i] if self.index_names is not None else None,
                    dayfirst=self.dayfirst,
                    cache_dates=self.cache_dates,
                    date_format=self.date_format,
                )

            if self.na_filter:
                col_na_values = self.na_values
                col_na_fvalues = self.na_fvalues
            else:
                col_na_values = set()
                col_na_fvalues = set()

            if isinstance(self.na_values, dict):
                assert self.index_names is not None
                col_name = self.index_names[i]
                if col_name is not None:
                    col_na_values, col_na_fvalues = get_na_values(
                        col_name, self.na_values, self.na_fvalues, self.keep_default_na
                    )
                else:
                    col_na_values, col_na_fvalues = set(), set()

            cast_type = None
            index_converter = False
            if self.index_names is not None:
                if isinstance(clean_dtypes, dict):
                    cast_type = clean_dtypes.get(self.index_names[i], None)

                if isinstance(converters, dict):
                    index_converter = converters.get(self.index_names[i]) is not None

            try_num_bool = not (
                    cast_type and is_string_dtype(cast_type) or index_converter
            )

            arr, _ = self._infer_types(
                arr, col_na_values | col_na_fvalues, cast_type is None, try_num_bool
            )
            if cast_type is not None:
                # Don't perform RangeIndex inference
                idx = Index(arr, name=name, dtype=cast_type)
            else:
                idx = ensure_index_from_sequences([arr], [name])
            arrays.append(idx)

        if len(arrays) == 1:
            return arrays[0]
        else:
            return MultiIndex.from_arrays(arrays)

    @ta.final
    def _set_noconvert_dtype_columns(
            self, col_indices: list[int], names: ta.Sequence[ta.Hashable]
    ) -> set[int]:
        """
        Set the columns that should not undergo dtype conversions.

        Currently, any column that is involved with date parsing will not
        undergo such conversions. If usecols is specified, the positions of the columns
        not to cast is relative to the usecols not to all columns.

        Parameters
        ----------
        col_indices: The indices specifying order and positions of the columns
        names: The column names which order is corresponding with the order
               of col_indices

        Returns
        -------
        A set of integers containing the positions of the columns not to convert.
        """
        usecols: list[int] | list[str] | None
        noconvert_columns = set()
        if self.usecols_dtype == "integer":
            # A set of integers will be converted to a list in
            # the correct order every single time.
            usecols = sorted(self.usecols)
        elif callable(self.usecols) or self.usecols_dtype not in ("empty", None):
            # The names attribute should have the correct columns
            # in the proper order for indexing with parse_dates.
            usecols = col_indices
        else:
            # Usecols is empty.
            usecols = None

        def _set(x) -> int:
            if usecols is not None and is_integer(x):
                x = usecols[x]

            if not is_integer(x):
                x = col_indices[names.index(x)]

            return x

        if isinstance(self.parse_dates, list):
            validate_parse_dates_presence(self.parse_dates, names)
            for val in self.parse_dates:
                noconvert_columns.add(_set(val))

        elif self.parse_dates:
            if isinstance(self.index_col, list):
                for k in self.index_col:
                    noconvert_columns.add(_set(k))
            elif self.index_col is not None:
                noconvert_columns.add(_set(self.index_col))

        return noconvert_columns

    @ta.final
    def _infer_types(
            self, values, na_values, no_dtype_specified, try_num_bool: bool = True
    ) -> tuple[ArrayLike, int]:
        """
        Infer types of values, possibly casting

        Parameters
        ----------
        values : ndarray
        na_values : set
        no_dtype_specified: Specifies if we want to cast explicitly
        try_num_bool : bool, default try
           try to cast values to numeric (first preference) or boolean

        Returns
        -------
        converted : ndarray or ExtensionArray
        na_count : int
        """
        na_count = 0
        if issubclass(values.dtype.type, (np.number, np.bool_)):
            # If our array has numeric dtype, we don't have to check for strings in isin
            na_values = np.array([val for val in na_values if not isinstance(val, str)])
            mask = isin(values, na_values)
            na_count = mask.astype("uint8", copy=False).sum()
            if na_count > 0:
                if is_integer_dtype(values):
                    values = values.astype(np.float64)
                np.putmask(values, mask, np.nan)
            return values, na_count

        dtype_backend = self.dtype_backend
        non_default_dtype_backend = (
                no_dtype_specified and dtype_backend is not no_default
        )
        result: ArrayLike

        if try_num_bool and is_object_dtype(values.dtype):
            # exclude e.g DatetimeIndex here
            try:
                result, result_mask = maybe_convert_numeric(
                    values,
                    na_values,
                    False,
                    convert_to_masked_nullable=non_default_dtype_backend,  # type: ignore[arg-type]
                )
            except (ValueError, TypeError):
                # e.g. encountering datetime string gets ValueError
                #  TypeError can be raised in floatify
                na_count = sanitize_objects(values, na_values)
                result = values
            else:
                if non_default_dtype_backend:
                    if result_mask is None:
                        result_mask = np.zeros(result.shape, dtype=np.bool_)

                    if result_mask.all():
                        result = IntegerArray(
                            np.ones(result_mask.shape, dtype=np.int64), result_mask
                        )
                    elif is_integer_dtype(result):
                        result = IntegerArray(result, result_mask)
                    elif is_bool_dtype(result):
                        result = BooleanArray(result, result_mask)
                    elif is_float_dtype(result):
                        result = FloatingArray(result, result_mask)

                    na_count = result_mask.sum()
                else:
                    na_count = isna(result).sum()
        else:
            result = values
            if values.dtype == np.object_:
                na_count = sanitize_objects(values, na_values)

        if result.dtype == np.object_ and try_num_bool:
            result, bool_mask = libops.maybe_convert_bool(
                np.asarray(values),
                true_values=self.true_values,
                false_values=self.false_values,
                convert_to_masked_nullable=non_default_dtype_backend,  # type: ignore[arg-type]
            )
            if result.dtype == np.bool_ and non_default_dtype_backend:
                if bool_mask is None:
                    bool_mask = np.zeros(result.shape, dtype=np.bool_)
                result = BooleanArray(result, bool_mask)
            elif result.dtype == np.object_ and non_default_dtype_backend:
                # read_excel sends array of datetime objects
                if not is_datetime_array(result, skipna=True):
                    dtype = StringDtype()
                    cls = dtype.construct_array_type()
                    result = cls._from_sequence(values, dtype=dtype)

        if dtype_backend == "pyarrow":
            pa = import_optional_dependency("pyarrow")
            if isinstance(result, np.ndarray):
                result = ArrowExtensionArray(pa.array(result, from_pandas=True))
            elif isinstance(result, BaseMaskedArray):
                if result._mask.all():
                    # We want an arrow null array here
                    result = ArrowExtensionArray(pa.array([None] * len(result)))
                else:
                    result = ArrowExtensionArray(
                        pa.array(result._data, mask=result._mask)
                    )
            else:
                result = ArrowExtensionArray(
                    pa.array(result.to_numpy(), from_pandas=True)
                )

        return result, na_count

    @ta.overload
    def _do_date_conversions(
            self,
            names: Index,
            data: DataFrame,
    ) -> DataFrame: ...

    @ta.overload
    def _do_date_conversions(
            self,
            names: ta.Sequence[ta.Hashable],
            data: ta.Mapping[ta.Hashable, ArrayLike],
    ) -> ta.Mapping[ta.Hashable, ArrayLike]: ...

    @ta.final
    def _do_date_conversions(
            self,
            names: ta.Sequence[ta.Hashable] | Index,
            data: ta.Mapping[ta.Hashable, ArrayLike] | DataFrame,
    ) -> ta.Mapping[ta.Hashable, ArrayLike] | DataFrame:
        if not isinstance(self.parse_dates, list):
            return data
        for colspec in self.parse_dates:
            if isinstance(colspec, int) and colspec not in data:
                colspec = names[colspec]
            if (isinstance(self.index_col, list) and colspec in self.index_col) or (
                    isinstance(self.index_names, list) and colspec in self.index_names
            ):
                continue
            result = date_converter(
                data[colspec],
                col=colspec,
                dayfirst=self.dayfirst,
                cache_dates=self.cache_dates,
                date_format=self.date_format,
            )
            # error: Unsupported target for indexed assignment
            # ("Mapping[Hashable, ExtensionArray | ndarray[Any, Any]] | DataFrame")
            data[colspec] = result  # type: ignore[index]

        return data

    @ta.final
    def _check_data_length(
            self,
            columns: ta.Sequence[ta.Hashable],
            data: ta.Sequence[ArrayLike],
    ) -> None:
        """Checks if length of data is equal to length of column names.

        One set of trailing commas is allowed. self.index_col not False
        results in a ParserError previously when lengths do not match.

        Parameters
        ----------
        columns: list of column names
        data: list of array-likes containing the data column-wise.
        """
        if not self.index_col and len(columns) != len(data) and columns:
            empty_str = is_object_dtype(data[-1]) and data[-1] == ""
            # error: No overload variant of "__ror__" of "ndarray" matches
            # argument type "ExtensionArray"
            empty_str_or_na = empty_str | isna(data[-1])  # type: ignore[operator]
            if len(columns) == len(data) - 1 and np.all(empty_str_or_na):
                return
            warnings.warn(
                "Length of header or names does not match length of data. This leads "
                "to a loss of data with index_col=False.",
                ParserWarning,
                stacklevel=find_stack_level(),
            )

    @ta.final
    def _validate_usecols_names(self, usecols: SequenceT, names: ta.Sequence) -> SequenceT:
        """
        Validates that all usecols are present in a given
        list of names. If not, raise a ValueError that
        shows what usecols are missing.

        Parameters
        ----------
        usecols : iterable of usecols
            The columns to validate are present in names.
        names : iterable of names
            The column names to check against.

        Returns
        -------
        usecols : iterable of usecols
            The `usecols` parameter if the validation succeeds.

        Raises
        ------
        ValueError : Columns were missing. Error message will list them.
        """
        missing = [c for c in usecols if c not in names]
        if len(missing) > 0:
            raise ValueError(
                f"Usecols do not match columns, columns expected but not found: "
                f"{missing}"
            )

        return usecols

    @ta.final
    def _clean_index_names(self, columns, index_col) -> tuple[list | None, list, list]:
        if not is_index_col(index_col):
            return None, columns, index_col

        columns = list(columns)

        # In case of no rows and multiindex columns we have to set index_names to
        # list of Nones GH#38292
        if not columns:
            return [None] * len(index_col), columns, index_col

        cp_cols = list(columns)
        index_names: list[str | int | None] = []

        # don't mutate
        index_col = list(index_col)

        for i, c in enumerate(index_col):
            if isinstance(c, str):
                index_names.append(c)
                for j, name in enumerate(cp_cols):
                    if name == c:
                        index_col[i] = j
                        columns.remove(name)
                        break
            else:
                name = cp_cols[c]
                columns.remove(name)
                index_names.append(name)

        # Only clean index names that were placeholders.
        for i, name in enumerate(index_names):
            if isinstance(name, str) and name in self.unnamed_cols:
                index_names[i] = None

        return index_names, columns, index_col

    @ta.final
    def _get_empty_meta(
            self, columns: ta.Sequence[HashableT], dtype: DtypeArg | None = None
    ) -> tuple[Index, list[HashableT], dict[HashableT, Series]]:
        columns = list(columns)

        index_col = self.index_col
        index_names = self.index_names

        # Convert `dtype` to a defaultdict of some kind.
        # This will enable us to write `dtype[col_name]`
        # without worrying about KeyError issues later on.
        dtype_dict: collections.defaultdict[ta.Hashable, ta.Any]
        if not is_dict_like(dtype):
            # if dtype == None, default will be object.
            dtype_dict = collections.defaultdict(lambda: dtype)
        else:
            dtype = ta.cast(dict, dtype)
            dtype_dict = collections.defaultdict(
                lambda: None,
                {columns[k] if is_integer(k) else k: v for k, v in dtype.items()},
            )

        # Even though we have no data, the "index" of the empty DataFrame
        # could for example still be an empty MultiIndex. Thus, we need to
        # check whether we have any index columns specified, via either:
        #
        # 1) index_col (column indices)
        # 2) index_names (column names)
        #
        # Both must be non-null to ensure a successful construction. Otherwise,
        # we have to create a generic empty Index.
        index: Index
        if (index_col is None or index_col is False) or index_names is None:
            index = default_index(0)
        else:
            # TODO: We could return default_index(0) if dtype_dict[name] is None
            data = [
                Index([], name=name, dtype=dtype_dict[name]) for name in index_names
            ]
            if len(data) == 1:
                index = data[0]
            else:
                index = MultiIndex.from_arrays(data)
            index_col.sort()

            for i, n in enumerate(index_col):
                columns.pop(n - i)

        col_dict = {
            col_name: Series([], dtype=dtype_dict[col_name]) for col_name in columns
        }

        return index, columns, col_dict


def date_converter(
        date_col,
        col: ta.Hashable,
        dayfirst: bool = False,
        cache_dates: bool = True,
        date_format: dict[ta.Hashable, str] | str | None = None,
):
    if date_col.dtype.kind in "Mm":
        return date_col

    date_fmt = date_format.get(col) if isinstance(date_format, dict) else date_format

    str_objs = ensure_string_array(np.asarray(date_col))
    try:
        result = to_datetime(
            str_objs,
            format=date_fmt,
            utc=False,
            dayfirst=dayfirst,
            cache=cache_dates,
        )
    except (ValueError, TypeError):
        # test_usecols_with_parse_dates4
        # test_multi_index_parse_dates
        return str_objs

    if isinstance(result, DatetimeIndex):
        arr = result.to_numpy()
        arr.flags.writeable = True
        return arr
    return result._values


parser_defaults = {
    "delimiter": None,
    "escapechar": None,
    "quotechar": '"',
    "quoting": csv.QUOTE_MINIMAL,
    "doublequote": True,
    "skipinitialspace": False,
    "lineterminator": None,
    "header": "infer",
    "index_col": None,
    "names": None,
    "skiprows": None,
    "skipfooter": 0,
    "nrows": None,
    "na_values": None,
    "keep_default_na": True,
    "true_values": None,
    "false_values": None,
    "converters": None,
    "dtype": None,
    "cache_dates": True,
    "thousands": None,
    "comment": None,
    "decimal": ".",
    # 'engine': 'c',
    "parse_dates": False,
    "dayfirst": False,
    "date_format": None,
    "usecols": None,
    # 'iterator': False,
    "chunksize": None,
    "encoding": None,
    "compression": None,
    "skip_blank_lines": True,
    "encoding_errors": "strict",
    "on_bad_lines": ParserBase.BadLineHandleMethod.ERROR,
    "dtype_backend": no_default,
}


# endregion


# region io/parsers/python_parser.py


# BOM character (byte order mark)
# This exists at the beginning of a file to indicate endianness
# of a file (stream). Unfortunately, this marker screws up parsing,
# so we need to remove it if we see it.
_BOM = "\ufeff"


class PythonParser(ParserBase):
    _no_thousands_columns: set[int]

    def __init__(self, f: ReadCsvBuffer[str] | list, **kwds) -> None:
        """
        Workhorse function for processing nested list into DataFrame
        """
        super().__init__(kwds)

        self.data: ta.Iterator[list[str]] | list[list[Scalar]] = []
        self.buf: list = []
        self.pos = 0
        self.line_pos = 0

        self.skiprows = kwds["skiprows"]

        if callable(self.skiprows):
            self.skipfunc = self.skiprows
        else:
            self.skipfunc = lambda x: x in self.skiprows

        self.skipfooter = _validate_skipfooter_arg(kwds["skipfooter"])
        self.delimiter = kwds["delimiter"]

        self.quotechar = kwds["quotechar"]
        if isinstance(self.quotechar, str):
            self.quotechar = str(self.quotechar)

        self.escapechar = kwds["escapechar"]
        self.doublequote = kwds["doublequote"]
        self.skipinitialspace = kwds["skipinitialspace"]
        self.lineterminator = kwds["lineterminator"]
        self.quoting = kwds["quoting"]
        self.skip_blank_lines = kwds["skip_blank_lines"]

        # Passed from read_excel
        self.has_index_names = kwds.get("has_index_names", False)

        self.thousands = kwds["thousands"]
        self.decimal = kwds["decimal"]

        self.comment = kwds["comment"]

        # Set self.data to something that can read lines.
        if isinstance(f, list):
            # read_excel: f is a nested list, can contain non-str
            self.data = f
        else:
            assert hasattr(f, "readline")
            # yields list of str
            self.data = self._make_reader(f)

        # Get columns in two steps: infer from data, then
        # infer column indices from self.usecols if it is specified.
        self._col_indices: list[int] | None = None
        columns: list[list[Scalar | None]]
        (
            columns,
            self.num_original_columns,
            self.unnamed_cols,
        ) = self._infer_columns()

        # Now self.columns has the set of columns that we will process.
        # The original set is stored in self.original_columns.
        # error: Cannot determine type of 'index_names'
        (
            self.columns,
            self.index_names,
            self.col_names,
            _,
        ) = self._extract_multi_indexer_columns(
            columns,
            self.index_names,  # type: ignore[has-type]
        )

        # get popped off for index
        self.orig_names: list[ta.Hashable] = list(self.columns)

        index_names, self.orig_names, self.columns = self._get_index_name()
        if self.index_names is None:
            self.index_names = index_names

        if self._col_indices is None:
            self._col_indices = list(range(len(self.columns)))

        self._no_thousands_columns = self._set_no_thousand_columns()

        if len(self.decimal) != 1:
            raise ValueError("Only length-1 decimal markers supported")

    @cache_readonly
    def num(self) -> re.Pattern:
        decimal = re.escape(self.decimal)
        if self.thousands is None:
            regex = rf"^[\-\+]?[0-9]*({decimal}[0-9]*)?([0-9]?(E|e)\-?[0-9]+)?$"
        else:
            thousands = re.escape(self.thousands)
            regex = (
                rf"^[\-\+]?([0-9]+{thousands}|[0-9])*({decimal}[0-9]*)?"
                rf"([0-9]?(E|e)\-?[0-9]+)?$"
            )
        return re.compile(regex)

    def _make_reader(self, f: ta.IO[str] | ReadCsvBuffer[str]) -> ta.Iterator[list[str]]:
        sep = self.delimiter

        if sep is None or len(sep) == 1:
            if self.lineterminator:
                raise ValueError(
                    "Custom line terminators not supported in python parser (yet)"
                )

            class MyDialect(csv.Dialect):
                delimiter = self.delimiter
                quotechar = self.quotechar
                escapechar = self.escapechar
                doublequote = self.doublequote
                skipinitialspace = self.skipinitialspace
                quoting = self.quoting
                lineterminator = "\n"

            dia = MyDialect

            if sep is not None:
                dia.delimiter = sep
            else:
                # attempt to sniff the delimiter from the first valid line,
                # i.e. no comment line and not in skiprows
                line = f.readline()
                lines = self._check_comments([[line]])[0]
                while self.skipfunc(self.pos) or not lines:
                    self.pos += 1
                    line = f.readline()
                    lines = self._check_comments([[line]])[0]
                lines_str = ta.cast(list[str], lines)

                # since `line` was a string, lines will be a list containing
                # only a single string
                line = lines_str[0]

                self.pos += 1
                self.line_pos += 1
                sniffed = csv.Sniffer().sniff(line)
                dia.delimiter = sniffed.delimiter

                # Note: encoding is irrelevant here
                line_rdr = csv.reader(io.StringIO(line), dialect=dia)
                self.buf.extend(list(line_rdr))

            # Note: encoding is irrelevant here
            reader = csv.reader(f, dialect=dia, strict=True)

        else:

            def _read():
                line = f.readline()
                pat = re.compile(sep)

                yield pat.split(line.strip())

                for line in f:
                    yield pat.split(line.strip())

            reader = _read()

        return reader

    def read(
            self, rows: int | None = None
    ) -> tuple[
        Index | None,
        ta.Sequence[ta.Hashable] | MultiIndex,
        ta.Mapping[ta.Hashable, ArrayLike | Series],
    ]:
        try:
            content = self._get_lines(rows)
        except StopIteration:
            if self._first_chunk:
                content = []
            else:
                self.close()
                raise

        # done with first read, next time raise StopIteration
        self._first_chunk = False

        index: Index | None
        columns: ta.Sequence[ta.Hashable] = list(self.orig_names)
        if not len(content):  # pragma: no cover
            # DataFrame with the right metadata, even though it's length 0
            # error: Cannot determine type of 'index_col'
            names = dedup_names(
                self.orig_names,
                is_potential_multi_index(
                    self.orig_names,
                    self.index_col,  # type: ignore[has-type]
                ),
            )
            index, columns, col_dict = self._get_empty_meta(
                names,
                self.dtype,
            )
            conv_columns = self._maybe_make_multi_index_columns(columns, self.col_names)
            return index, conv_columns, col_dict

        # handle new style for names in index
        indexnamerow = None
        if self.has_index_names and sum(
                int(v == "" or v is None) for v in content[0]
        ) == len(columns):
            indexnamerow = content[0]
            content = content[1:]

        alldata = self._rows_to_cols(content)
        data, columns = self._exclude_implicit_index(alldata)

        conv_data = self._convert_data(data)
        conv_data = self._do_date_conversions(columns, conv_data)

        index, result_columns = self._make_index(alldata, columns, indexnamerow)

        return index, result_columns, conv_data

    def _exclude_implicit_index(
            self,
            alldata: list[np.ndarray],
    ) -> tuple[ta.Mapping[ta.Hashable, np.ndarray], ta.Sequence[ta.Hashable]]:
        # error: Cannot determine type of 'index_col'
        names = dedup_names(
            self.orig_names,
            is_potential_multi_index(
                self.orig_names,
                self.index_col,  # type: ignore[has-type]
            ),
        )

        offset = 0
        if self._implicit_index:
            # error: Cannot determine type of 'index_col'
            offset = len(self.index_col)  # type: ignore[has-type]

        len_alldata = len(alldata)
        self._check_data_length(names, alldata)

        return {
            name: alldata[i + offset] for i, name in enumerate(names) if i < len_alldata
        }, names

    # legacy
    def get_chunk(
            self, size: int | None = None
    ) -> tuple[
        Index | None,
        ta.Sequence[ta.Hashable] | MultiIndex,
        ta.Mapping[ta.Hashable, ArrayLike | Series],
    ]:
        if size is None:
            # error: "PythonParser" has no attribute "chunksize"
            size = self.chunksize  # type: ignore[attr-defined]
        return self.read(rows=size)

    def _convert_data(
            self,
            data: ta.Mapping[ta.Hashable, np.ndarray],
    ) -> ta.Mapping[ta.Hashable, ArrayLike]:
        # apply converters
        clean_conv = self._clean_mapping(self.converters)
        clean_dtypes = self._clean_mapping(self.dtype)

        # Apply NA values.
        clean_na_values = {}
        clean_na_fvalues = {}

        if isinstance(self.na_values, dict):
            for col in self.na_values:
                if col is not None:
                    na_value = self.na_values[col]
                    na_fvalue = self.na_fvalues[col]

                    if isinstance(col, int) and col not in self.orig_names:
                        col = self.orig_names[col]

                    clean_na_values[col] = na_value
                    clean_na_fvalues[col] = na_fvalue
        else:
            clean_na_values = self.na_values
            clean_na_fvalues = self.na_fvalues

        return self._convert_to_ndarrays(
            data,
            clean_na_values,
            clean_na_fvalues,
            clean_conv,
            clean_dtypes,
        )

    @ta.final
    def _convert_to_ndarrays(
            self,
            dct: ta.Mapping,
            na_values,
            na_fvalues,
            converters=None,
            dtypes=None,
    ) -> dict[ta.Any, np.ndarray]:
        result = {}
        parse_date_cols = validate_parse_dates_presence(self.parse_dates, self.columns)
        for c, values in dct.items():
            conv_f = None if converters is None else converters.get(c, None)
            if isinstance(dtypes, dict):
                cast_type = dtypes.get(c, None)
            else:
                # single dtype or None
                cast_type = dtypes

            if self.na_filter:
                col_na_values, col_na_fvalues = get_na_values(
                    c, na_values, na_fvalues, self.keep_default_na
                )
            else:
                col_na_values, col_na_fvalues = set(), set()

            if c in parse_date_cols:
                # GH#26203 Do not convert columns which get converted to dates
                # but replace nans to ensure to_datetime works
                mask = isin(values, set(col_na_values) | col_na_fvalues)  # pyright: ignore[reportArgumentType]
                np.putmask(values, mask, np.nan)
                result[c] = values
                continue

            if conv_f is not None:
                # conv_f applied to data before inference
                if cast_type is not None:
                    warnings.warn(
                        (
                            "Both a converter and dtype were specified "
                            f"for column {c} - only the converter will be used."
                        ),
                        ParserWarning,
                        stacklevel=find_stack_level(),
                    )

                try:
                    values = map_infer(values, conv_f)
                except ValueError:
                    mask = isin(values, list(na_values)).view(np.uint8)
                    values = map_infer_mask(values, conv_f, mask)

                cvals, na_count = self._infer_types(
                    values,
                    set(col_na_values) | col_na_fvalues,
                    cast_type is None,
                    try_num_bool=False,
                    )
            else:
                is_ea = is_extension_array_dtype(cast_type)
                is_str_or_ea_dtype = is_ea or is_string_dtype(cast_type)
                # skip inference if specified dtype is object
                # or casting to an EA
                try_num_bool = not (cast_type and is_str_or_ea_dtype)

                # general type inference and conversion
                cvals, na_count = self._infer_types(
                    values,
                    set(col_na_values) | col_na_fvalues,
                    cast_type is None,
                    try_num_bool,
                    )

                # type specified in dtype param or cast_type is an EA
                if cast_type is not None:
                    cast_type = pandas_dtype(cast_type)
                if cast_type and (cvals.dtype != cast_type or is_ea):
                    if not is_ea and na_count > 0:
                        if is_bool_dtype(cast_type):
                            raise ValueError(f"Bool column has NA values in column {c}")
                    cvals = self._cast_types(cvals, cast_type, c)

            result[c] = cvals
        return result

    @ta.final
    def _cast_types(self, values: ArrayLike, cast_type: DtypeObj, column) -> ArrayLike:
        """
        Cast values to specified type

        Parameters
        ----------
        values : ndarray or ExtensionArray
        cast_type : np.dtype or ExtensionDtype
           dtype to cast values to
        column : string
            column name - used only for error reporting

        Returns
        -------
        converted : ndarray or ExtensionArray
        """
        if isinstance(cast_type, CategoricalDtype):
            known_cats = cast_type.categories is not None

            if not is_object_dtype(values.dtype) and not known_cats:
                # TODO: this is for consistency with
                # c-parser which parses all categories
                # as strings
                values = ensure_string_array(
                    values, skipna=False, convert_na_value=False
                )

            cats = Index(values).unique().dropna()
            values = Categorical._from_inferred_categories(
                cats, cats.get_indexer(values), cast_type, true_values=self.true_values
            )

        # use the EA's implementation of casting
        elif isinstance(cast_type, ExtensionDtype):
            array_type = cast_type.construct_array_type()
            try:
                if isinstance(cast_type, BooleanDtype):
                    # error: Unexpected keyword argument "true_values" for
                    # "_from_sequence_of_strings" of "ExtensionArray"
                    values_str = [str(val) for val in values]
                    return array_type._from_sequence_of_strings(  # type: ignore[call-arg]
                        values_str,
                        dtype=cast_type,
                        true_values=self.true_values,  # pyright: ignore[reportCallIssue]
                        false_values=self.false_values,  # pyright: ignore[reportCallIssue]
                        none_values=self.na_values,  # pyright: ignore[reportCallIssue]
                    )
                else:
                    return array_type._from_sequence_of_strings(values, dtype=cast_type)
            except NotImplementedError as err:
                raise NotImplementedError(
                    f"Extension Array: {array_type} must implement "
                    "_from_sequence_of_strings in order to be used in parser methods"
                ) from err

        elif isinstance(values, ExtensionArray):
            values = values.astype(cast_type, copy=False)
        elif issubclass(cast_type.type, str):
            # TODO: why skipna=True here and False above? some tests depend
            #  on it here, but nothing fails if we change it above
            #  (as no tests get there as of 2022-12-06)
            values = ensure_string_array(
                values, skipna=True, convert_na_value=False
            )
        else:
            try:
                values = astype_array(values, cast_type, copy=True)
            except ValueError as err:
                raise ValueError(
                    f"Unable to convert column {column} to type {cast_type}"
                ) from err
        return values

    @cache_readonly
    def _have_mi_columns(self) -> bool:
        if self.header is None:
            return False

        header = self.header
        if isinstance(header, (list, tuple, np.ndarray)):
            return len(header) > 1
        else:
            return False

    def _infer_columns(
            self,
    ) -> tuple[list[list[Scalar | None]], int, set[Scalar | None]]:
        names = self.names
        num_original_columns = 0
        clear_buffer = True
        unnamed_cols: set[Scalar | None] = set()

        if self.header is not None:
            header = self.header
            have_mi_columns = self._have_mi_columns

            if isinstance(header, (list, tuple, np.ndarray)):
                # we have a mi columns, so read an extra line
                if have_mi_columns:
                    header = list(header) + [header[-1] + 1]
            else:
                header = [header]

            columns: list[list[Scalar | None]] = []
            for level, hr in enumerate(header):
                try:
                    line = self._buffered_line()

                    while self.line_pos <= hr:
                        line = self._next_line()

                except StopIteration as err:
                    if 0 < self.line_pos <= hr and (
                            not have_mi_columns or hr != header[-1]
                    ):
                        # If no rows we want to raise a different message and if
                        # we have mi columns, the last line is not part of the header
                        joi = list(map(str, header[:-1] if have_mi_columns else header))
                        msg = f"[{','.join(joi)}], len of {len(joi)}, "
                        raise ValueError(
                            f"Passed header={msg}"
                            f"but only {self.line_pos} lines in file"
                        ) from err

                    # We have an empty file, so check
                    # if columns are provided. That will
                    # serve as the 'line' for parsing
                    if have_mi_columns and hr > 0:
                        if clear_buffer:
                            self.buf.clear()
                        columns.append([None] * len(columns[-1]))
                        return columns, num_original_columns, unnamed_cols

                    if not self.names:
                        raise EmptyDataError("No columns to parse from file") from err

                    line = self.names[:]

                this_columns: list[Scalar | None] = []
                this_unnamed_cols = []

                for i, c in enumerate(line):
                    if c == "":
                        if have_mi_columns:
                            col_name = f"Unnamed: {i}_level_{level}"
                        else:
                            col_name = f"Unnamed: {i}"

                        this_unnamed_cols.append(i)
                        this_columns.append(col_name)
                    else:
                        this_columns.append(c)

                if not have_mi_columns:
                    counts: collections.defaultdict = collections.defaultdict(int)
                    # Ensure that regular columns are used before unnamed ones
                    # to keep given names and mangle unnamed columns
                    col_loop_order = [
                        i
                        for i in range(len(this_columns))
                        if i not in this_unnamed_cols
                    ] + this_unnamed_cols

                    # TODO: Use pandas.io.common.dedup_names instead (see #50371)
                    for i in col_loop_order:
                        col = this_columns[i]
                        old_col = col
                        cur_count = counts[col]

                        if cur_count > 0:
                            while cur_count > 0:
                                counts[old_col] = cur_count + 1
                                col = f"{old_col}.{cur_count}"
                                if col in this_columns:
                                    cur_count += 1
                                else:
                                    cur_count = counts[col]

                            if (
                                    self.dtype is not None
                                    and is_dict_like(self.dtype)
                                    and self.dtype.get(old_col) is not None
                                    and self.dtype.get(col) is None
                            ):
                                self.dtype.update({col: self.dtype.get(old_col)})
                        this_columns[i] = col
                        counts[col] = cur_count + 1
                elif have_mi_columns:
                    # if we have grabbed an extra line, but its not in our
                    # format so save in the buffer, and create an blank extra
                    # line for the rest of the parsing code
                    if hr == header[-1]:
                        lc = len(this_columns)
                        # error: Cannot determine type of 'index_col'
                        sic = self.index_col  # type: ignore[has-type]
                        ic = len(sic) if sic is not None else 0
                        unnamed_count = len(this_unnamed_cols)

                        # if wrong number of blanks or no index, not our format
                        if (lc != unnamed_count and lc - ic > unnamed_count) or ic == 0:
                            clear_buffer = False
                            this_columns = [None] * lc
                            self.buf = [self.buf[-1]]

                columns.append(this_columns)
                unnamed_cols.update({this_columns[i] for i in this_unnamed_cols})

                if len(columns) == 1:
                    num_original_columns = len(this_columns)

            if clear_buffer:
                self.buf.clear()

            first_line: list[Scalar] | None
            if names is not None:
                # Read first row after header to check if data are longer
                try:
                    first_line = self._next_line()
                except StopIteration:
                    first_line = None

                len_first_data_row = 0 if first_line is None else len(first_line)

                if len(names) > len(columns[0]) and len(names) > len_first_data_row:
                    raise ValueError(
                        "Number of passed names did not match "
                        "number of header fields in the file"
                    )
                if len(columns) > 1:
                    raise TypeError("Cannot pass names with multi-index columns")

                if self.usecols is not None:
                    # Set _use_cols. We don't store columns because they are
                    # overwritten.
                    self._handle_usecols(columns, names, num_original_columns)
                else:
                    num_original_columns = len(names)
                if self._col_indices is not None and len(names) != len(
                        self._col_indices
                ):
                    columns = [[names[i] for i in sorted(self._col_indices)]]
                else:
                    columns = [names]
            else:
                columns = self._handle_usecols(
                    columns, columns[0], num_original_columns
                )
        else:
            ncols = len(self._header_line)
            num_original_columns = ncols

            if not names:
                columns = [list(range(ncols))]
                columns = self._handle_usecols(columns, columns[0], ncols)
            elif self.usecols is None or len(names) >= ncols:
                columns = self._handle_usecols([names], names, ncols)
                num_original_columns = len(names)
            elif not callable(self.usecols) and len(names) != len(self.usecols):
                raise ValueError(
                    "Number of passed names did not match number of "
                    "header fields in the file"
                )
            else:
                # Ignore output but set used columns.
                columns = [names]
                self._handle_usecols(columns, columns[0], ncols)

        return columns, num_original_columns, unnamed_cols

    @cache_readonly
    def _header_line(self):
        # Store line for reuse in _get_index_name
        if self.header is not None:
            return None

        try:
            line = self._buffered_line()
        except StopIteration as err:
            if not self.names:
                raise EmptyDataError("No columns to parse from file") from err

            line = self.names[:]
        return line

    def _handle_usecols(
            self,
            columns: list[list[Scalar | None]],
            usecols_key: list[Scalar | None],
            num_original_columns: int,
    ) -> list[list[Scalar | None]]:
        """
        Sets self._col_indices

        usecols_key is used if there are string usecols.
        """
        col_indices: set[int] | list[int]
        if self.usecols is not None:
            if callable(self.usecols):
                col_indices = evaluate_callable_usecols(self.usecols, usecols_key)
            elif any(isinstance(u, str) for u in self.usecols):
                if len(columns) > 1:
                    raise ValueError(
                        "If using multiple headers, usecols must be integers."
                    )
                col_indices = []

                for col in self.usecols:
                    if isinstance(col, str):
                        try:
                            col_indices.append(usecols_key.index(col))
                        except ValueError:
                            self._validate_usecols_names(self.usecols, usecols_key)
                    else:
                        col_indices.append(col)
            else:
                missing_usecols = [
                    col for col in self.usecols if col >= num_original_columns
                ]
                if missing_usecols:
                    raise ParserError(
                        "Defining usecols with out-of-bounds indices is not allowed. "
                        f"{missing_usecols} are out-of-bounds.",
                    )
                col_indices = self.usecols

            columns = [
                [n for i, n in enumerate(column) if i in col_indices]
                for column in columns
            ]
            self._col_indices = sorted(col_indices)
        return columns

    def _buffered_line(self) -> list[Scalar]:
        """
        Return a line from buffer, filling buffer if required.
        """
        if len(self.buf) > 0:
            return self.buf[0]
        else:
            return self._next_line()

    def _check_for_bom(self, first_row: list[Scalar]) -> list[Scalar]:
        """
        Checks whether the file begins with the BOM character.
        If it does, remove it. In addition, if there is quoting
        in the field subsequent to the BOM, remove it as well
        because it technically takes place at the beginning of
        the name, not the middle of it.
        """
        # first_row will be a list, so we need to check
        # that that list is not empty before proceeding.
        if not first_row:
            return first_row

        # The first element of this row is the one that could have the
        # BOM that we want to remove. Check that the first element is a
        # string before proceeding.
        if not isinstance(first_row[0], str):
            return first_row

        # Check that the string is not empty, as that would
        # obviously not have a BOM at the start of it.
        if not first_row[0]:
            return first_row

        # Since the string is non-empty, check that it does
        # in fact begin with a BOM.
        first_elt = first_row[0][0]
        if first_elt != _BOM:
            return first_row

        first_row_bom = first_row[0]
        new_row: str

        if len(first_row_bom) > 1 and first_row_bom[1] == self.quotechar:
            start = 2
            quote = first_row_bom[1]
            end = first_row_bom[2:].index(quote) + 2

            # Extract the data between the quotation marks
            new_row = first_row_bom[start:end]

            # Extract any remaining data after the second
            # quotation mark.
            if len(first_row_bom) > end + 1:
                new_row += first_row_bom[end + 1 :]

        else:
            # No quotation so just remove BOM from first element
            new_row = first_row_bom[1:]

        new_row_list: list[Scalar] = [new_row]
        return new_row_list + first_row[1:]

    def _is_line_empty(self, line: ta.Sequence[Scalar]) -> bool:
        """
        Check if a line is empty or not.

        Parameters
        ----------
        line : str, array-like
            The line of data to check.

        Returns
        -------
        boolean : Whether or not the line is empty.
        """
        return not line or all(not x for x in line)

    def _next_line(self) -> list[Scalar]:
        if isinstance(self.data, list):
            while self.skipfunc(self.pos):
                if self.pos >= len(self.data):
                    break
                self.pos += 1

            while True:
                try:
                    line = self._check_comments([self.data[self.pos]])[0]
                    self.pos += 1
                    # either uncommented or blank to begin with
                    if not self.skip_blank_lines and (
                            self._is_line_empty(self.data[self.pos - 1]) or line
                    ):
                        break
                    if self.skip_blank_lines:
                        ret = self._remove_empty_lines([line])
                        if ret:
                            line = ret[0]
                            break
                except IndexError as err:
                    raise StopIteration from err
        else:
            while self.skipfunc(self.pos):
                self.pos += 1
                next(self.data)

            while True:
                orig_line = self._next_iter_line(row_num=self.pos + 1)
                self.pos += 1

                if orig_line is not None:
                    line = self._check_comments([orig_line])[0]

                    if self.skip_blank_lines:
                        ret = self._remove_empty_lines([line])

                        if ret:
                            line = ret[0]
                            break
                    elif self._is_line_empty(orig_line) or line:
                        break

        # This was the first line of the file,
        # which could contain the BOM at the
        # beginning of it.
        if self.pos == 1:
            line = self._check_for_bom(line)

        self.line_pos += 1
        self.buf.append(line)
        return line

    def _alert_malformed(self, msg: str, row_num: int) -> None:
        """
        Alert a user about a malformed row, depending on value of
        `self.on_bad_lines` enum.

        If `self.on_bad_lines` is ERROR, the alert will be `ParserError`.
        If `self.on_bad_lines` is WARN, the alert will be printed out.

        Parameters
        ----------
        msg: str
            The error message to display.
        row_num: int
            The row number where the parsing error occurred.
            Because this row number is displayed, we 1-index,
            even though we 0-index internally.
        """
        if self.on_bad_lines == self.BadLineHandleMethod.ERROR:
            raise ParserError(msg)
        if self.on_bad_lines == self.BadLineHandleMethod.WARN:
            warnings.warn(
                f"Skipping line {row_num}: {msg}\n",
                ParserWarning,
                stacklevel=find_stack_level(),
            )

    def _next_iter_line(self, row_num: int) -> list[Scalar] | None:
        """
        Wrapper around iterating through `self.data` (CSV source).

        When a CSV error is raised, we check for specific
        error messages that allow us to customize the
        error message displayed to the user.

        Parameters
        ----------
        row_num: int
            The row number of the line being parsed.
        """
        try:
            assert not isinstance(self.data, list)
            line = next(self.data)
            # lie about list[str] vs list[Scalar] to minimize ignores
            return line  # type: ignore[return-value]
        except csv.Error as e:
            if self.on_bad_lines in (
                    self.BadLineHandleMethod.ERROR,
                    self.BadLineHandleMethod.WARN,
            ):
                msg = str(e)

                if "NULL byte" in msg or "line contains NUL" in msg:
                    msg = (
                        "NULL byte detected. This byte "
                        "cannot be processed in Python's "
                        "native csv library at the moment, "
                        "so please pass in engine='c' instead"
                    )

                if self.skipfooter > 0:
                    reason = (
                        "Error could possibly be due to "
                        "parsing errors in the skipped footer rows "
                        "(the skipfooter keyword is only applied "
                        "after Python's csv library has parsed "
                        "all rows)."
                    )
                    msg += ". " + reason

                self._alert_malformed(msg, row_num)
            return None

    def _check_comments(self, lines: list[list[Scalar]]) -> list[list[Scalar]]:
        if self.comment is None:
            return lines
        ret = []
        for line in lines:
            rl = []
            for x in line:
                if (
                        not isinstance(x, str)
                        or self.comment not in x
                        or x in self.na_values
                ):
                    rl.append(x)
                else:
                    x = x[: x.find(self.comment)]
                    if len(x) > 0:
                        rl.append(x)
                    break
            ret.append(rl)
        return ret

    def _remove_empty_lines(self, lines: list[list[T]]) -> list[list[T]]:
        """
        Iterate through the lines and remove any that are
        either empty or contain only one whitespace value

        Parameters
        ----------
        lines : list of list of Scalars
            The array of lines that we are to filter.

        Returns
        -------
        filtered_lines : list of list of Scalars
            The same array of lines with the "empty" ones removed.
        """
        # Remove empty lines and lines with only one whitespace value
        ret = [
            line
            for line in lines
            if (
                    len(line) > 1
                    or len(line) == 1
                    and (not isinstance(line[0], str) or line[0].strip())
            )
        ]
        return ret

    def _check_thousands(self, lines: list[list[Scalar]]) -> list[list[Scalar]]:
        if self.thousands is None:
            return lines

        return self._search_replace_num_columns(
            lines=lines, search=self.thousands, replace=""
        )

    def _search_replace_num_columns(
            self, lines: list[list[Scalar]], search: str, replace: str
    ) -> list[list[Scalar]]:
        ret = []
        for line in lines:
            rl = []
            for i, x in enumerate(line):
                if (
                        not isinstance(x, str)
                        or search not in x
                        or i in self._no_thousands_columns
                        or not self.num.search(x.strip())
                ):
                    rl.append(x)
                else:
                    rl.append(x.replace(search, replace))
            ret.append(rl)
        return ret

    def _check_decimal(self, lines: list[list[Scalar]]) -> list[list[Scalar]]:
        if self.decimal == parser_defaults["decimal"]:
            return lines

        return self._search_replace_num_columns(
            lines=lines, search=self.decimal, replace="."
        )

    def _get_index_name(
            self,
    ) -> tuple[ta.Sequence[ta.Hashable] | None, list[ta.Hashable], list[ta.Hashable]]:
        """
        Try several cases to get lines:

        0) There are headers on row 0 and row 1 and their
        total summed lengths equals the length of the next line.
        Treat row 0 as columns and row 1 as indices
        1) Look for implicit index: there are more columns
        on row 1 than row 0. If this is true, assume that row
        1 lists index columns and row 0 lists normal columns.
        2) Get index from the columns if it was listed.
        """
        columns: ta.Sequence[ta.Hashable] = self.orig_names
        orig_names = list(columns)
        columns = list(columns)

        line: list[Scalar] | None
        if self._header_line is not None:
            line = self._header_line
        else:
            try:
                line = self._next_line()
            except StopIteration:
                line = None

        next_line: list[Scalar] | None
        try:
            next_line = self._next_line()
        except StopIteration:
            next_line = None

        # implicitly index_col=0 b/c 1 fewer column names
        implicit_first_cols = 0
        if line is not None:
            # leave it 0, #2442
            # Case 1
            # error: Cannot determine type of 'index_col'
            index_col = self.index_col  # type: ignore[has-type]
            if index_col is not False:
                implicit_first_cols = len(line) - self.num_original_columns

            # Case 0
            if (
                    next_line is not None
                    and self.header is not None
                    and index_col is not False
            ):
                if len(next_line) == len(line) + self.num_original_columns:
                    # column and index names on diff rows
                    self.index_col = list(range(len(line)))
                    self.buf = self.buf[1:]

                    for c in reversed(line):
                        columns.insert(0, c)

                    # Update list of original names to include all indices.
                    orig_names = list(columns)
                    self.num_original_columns = len(columns)
                    return line, orig_names, columns

        if implicit_first_cols > 0:
            # Case 1
            self._implicit_index = True
            if self.index_col is None:
                self.index_col = list(range(implicit_first_cols))

            index_name = None

        else:
            # Case 2
            (index_name, _, self.index_col) = self._clean_index_names(
                columns, self.index_col
            )

        return index_name, orig_names, columns

    def _rows_to_cols(self, content: list[list[Scalar]]) -> list[np.ndarray]:
        col_len = self.num_original_columns

        if self._implicit_index:
            col_len += len(self.index_col)

        max_len = max(len(row) for row in content)

        # Check that there are no rows with too many
        # elements in their row (rows with too few
        # elements are padded with NaN).
        # error: Non-overlapping identity check (left operand type: "List[int]",
        # right operand type: "Literal[False]")
        if (
                max_len > col_len
                and self.index_col is not False  # type: ignore[comparison-overlap]
                and self.usecols is None
        ):
            footers = self.skipfooter if self.skipfooter else 0
            bad_lines = []

            iter_content = enumerate(content)
            content_len = len(content)
            content = []

            for i, _content in iter_content:
                actual_len = len(_content)

                if actual_len > col_len:
                    if callable(self.on_bad_lines):
                        new_l = self.on_bad_lines(_content)
                        if new_l is not None:
                            content.append(new_l)
                    elif self.on_bad_lines in (
                            self.BadLineHandleMethod.ERROR,
                            self.BadLineHandleMethod.WARN,
                    ):
                        row_num = self.pos - (content_len - i + footers)
                        bad_lines.append((row_num, actual_len))

                        if self.on_bad_lines == self.BadLineHandleMethod.ERROR:
                            break
                else:
                    content.append(_content)

            for row_num, actual_len in bad_lines:
                msg = (
                    f"Expected {col_len} fields in line {row_num + 1}, saw "
                    f"{actual_len}"
                )
                if (
                        self.delimiter
                        and len(self.delimiter) > 1
                        and self.quoting != csv.QUOTE_NONE
                ):
                    # see gh-13374
                    reason = (
                        "Error could possibly be due to quotes being "
                        "ignored when a multi-char delimiter is used."
                    )
                    msg += ". " + reason

                self._alert_malformed(msg, row_num + 1)

        # see gh-13320
        zipped_content = list(to_object_array(content, min_width=col_len).T)

        if self.usecols:
            assert self._col_indices is not None
            col_indices = self._col_indices

            if self._implicit_index:
                zipped_content = [
                    a
                    for i, a in enumerate(zipped_content)
                    if (
                            i < len(self.index_col)
                            or i - len(self.index_col) in col_indices
                    )
                ]
            else:
                zipped_content = [
                    a for i, a in enumerate(zipped_content) if i in col_indices
                ]
        return zipped_content

    def _get_lines(self, rows: int | None = None) -> list[list[Scalar]]:
        lines = self.buf
        new_rows = None

        # already fetched some number
        if rows is not None:
            # we already have the lines in the buffer
            if len(self.buf) >= rows:
                new_rows, self.buf = self.buf[:rows], self.buf[rows:]

            # need some lines
            else:
                rows -= len(self.buf)

        if new_rows is None:
            if isinstance(self.data, list):
                if self.pos > len(self.data):
                    raise StopIteration
                if rows is None:
                    new_rows = self.data[self.pos :]
                    new_pos = len(self.data)
                else:
                    new_rows = self.data[self.pos : self.pos + rows]
                    new_pos = self.pos + rows

                new_rows = self._remove_skipped_rows(new_rows)
                lines.extend(new_rows)
                self.pos = new_pos

            else:
                new_rows = []
                try:
                    if rows is not None:
                        row_index = 0
                        row_ct = 0
                        offset = self.pos if self.pos is not None else 0
                        while row_ct < rows:
                            new_row = next(self.data)
                            if not self.skipfunc(offset + row_index):
                                row_ct += 1
                            row_index += 1
                            new_rows.append(new_row)

                        len_new_rows = len(new_rows)
                        new_rows = self._remove_skipped_rows(new_rows)
                        lines.extend(new_rows)
                    else:
                        rows = 0

                        while True:
                            next_row = self._next_iter_line(row_num=self.pos + rows + 1)
                            rows += 1

                            if next_row is not None:
                                new_rows.append(next_row)
                        len_new_rows = len(new_rows)

                except StopIteration:
                    len_new_rows = len(new_rows)
                    new_rows = self._remove_skipped_rows(new_rows)
                    lines.extend(new_rows)
                    if len(lines) == 0:
                        raise
                self.pos += len_new_rows

            self.buf = []
        else:
            lines = new_rows

        if self.skipfooter:
            lines = lines[: -self.skipfooter]

        lines = self._check_comments(lines)
        if self.skip_blank_lines:
            lines = self._remove_empty_lines(lines)
        lines = self._check_thousands(lines)
        return self._check_decimal(lines)

    def _remove_skipped_rows(self, new_rows: list[list[Scalar]]) -> list[list[Scalar]]:
        if self.skiprows:
            return [
                row for i, row in enumerate(new_rows) if not self.skipfunc(i + self.pos)
            ]
        return new_rows

    def _set_no_thousand_columns(self) -> set[int]:
        no_thousands_columns: set[int] = set()
        if self.columns and self.parse_dates:
            assert self._col_indices is not None
            no_thousands_columns = self._set_noconvert_dtype_columns(
                self._col_indices, self.columns
            )
        if self.columns and self.dtype:
            assert self._col_indices is not None
            for i, col in zip(self._col_indices, self.columns):
                if not isinstance(self.dtype, dict) and not is_numeric_dtype(
                        self.dtype
                ):
                    no_thousands_columns.add(i)
                if (
                        isinstance(self.dtype, dict)
                        and col in self.dtype
                        and (
                        not is_numeric_dtype(self.dtype[col])
                        or is_bool_dtype(self.dtype[col])
                )
                ):
                    no_thousands_columns.add(i)
        return no_thousands_columns


class FixedWidthReader(ta.Iterator):
    """
    A reader of fixed-width lines.
    """

    def __init__(
            self,
            f: ta.IO[str] | ReadCsvBuffer[str],
            colspecs: list[tuple[int, int]] | ta.Literal["infer"],
            delimiter: str | None,
            comment: str | None,
            skiprows: set[int] | None = None,
            infer_nrows: int = 100,
    ) -> None:
        self.f = f
        self.buffer: ta.Iterator | None = None
        self.delimiter = "\r\n" + delimiter if delimiter else "\n\r\t "
        self.comment = comment
        if colspecs == "infer":
            self.colspecs = self.detect_colspecs(
                infer_nrows=infer_nrows, skiprows=skiprows
            )
        else:
            self.colspecs = colspecs

        if not isinstance(self.colspecs, (tuple, list)):
            raise TypeError(
                "column specifications must be a list or tuple, "
                f"input was a {type(colspecs).__name__}"
            )

        for colspec in self.colspecs:
            if not (
                    isinstance(colspec, (tuple, list))
                    and len(colspec) == 2
                    and isinstance(colspec[0], (int, np.integer, type(None)))
                    and isinstance(colspec[1], (int, np.integer, type(None)))
            ):
                raise TypeError(
                    "Each column specification must be "
                    "2 element tuple or list of integers"
                )

    def get_rows(self, infer_nrows: int, skiprows: set[int] | None = None) -> list[str]:
        """
        Read rows from self.f, skipping as specified.

        We distinguish buffer_rows (the first <= infer_nrows
        lines) from the rows returned to detect_colspecs
        because it's simpler to leave the other locations
        with skiprows logic alone than to modify them to
        deal with the fact we skipped some rows here as
        well.

        Parameters
        ----------
        infer_nrows : int
            Number of rows to read from self.f, not counting
            rows that are skipped.
        skiprows: set, optional
            Indices of rows to skip.

        Returns
        -------
        detect_rows : list of str
            A list containing the rows to read.

        """
        if skiprows is None:
            skiprows = set()
        buffer_rows = []
        detect_rows = []
        for i, row in enumerate(self.f):
            if i not in skiprows:
                detect_rows.append(row)
            buffer_rows.append(row)
            if len(detect_rows) >= infer_nrows:
                break
        self.buffer = iter(buffer_rows)
        return detect_rows

    def detect_colspecs(
            self, infer_nrows: int = 100, skiprows: set[int] | None = None
    ) -> list[tuple[int, int]]:
        # Regex escape the delimiters
        delimiters = "".join([rf"\{x}" for x in self.delimiter])
        pattern = re.compile(f"([^{delimiters}]+)")
        rows = self.get_rows(infer_nrows, skiprows)
        if not rows:
            raise EmptyDataError("No rows from which to infer column width")
        max_len = max(map(len, rows))
        mask = np.zeros(max_len + 1, dtype=int)
        if self.comment is not None:
            rows = [row.partition(self.comment)[0] for row in rows]
        for row in rows:
            for m in pattern.finditer(row):
                mask[m.start() : m.end()] = 1
        shifted = np.roll(mask, 1)
        shifted[0] = 0
        edges = np.where((mask ^ shifted) == 1)[0]
        edge_pairs = list(zip(edges[::2], edges[1::2]))
        return edge_pairs

    def __next__(self) -> list[str]:
        # Argument 1 to "next" has incompatible type "Union[IO[str],
        # ReadCsvBuffer[str]]"; expected "SupportsNext[str]"
        if self.buffer is not None:
            try:
                line = next(self.buffer)
            except StopIteration:
                self.buffer = None
                line = next(self.f)  # type: ignore[arg-type]
        else:
            line = next(self.f)  # type: ignore[arg-type]
        # Note: 'colspecs' is a sequence of half-open intervals.
        return [line[from_:to].strip(self.delimiter) for (from_, to) in self.colspecs]


class FixedWidthFieldParser(PythonParser):
    """
    Specialization that Converts fixed-width fields into DataFrames.
    See PythonParser for details.
    """

    def __init__(self, f: ReadCsvBuffer[str], **kwds) -> None:
        # Support iterators, convert to a list.
        self.colspecs = kwds.pop("colspecs")
        self.infer_nrows = kwds.pop("infer_nrows")
        PythonParser.__init__(self, f, **kwds)

    def _make_reader(self, f: ta.IO[str] | ReadCsvBuffer[str]) -> FixedWidthReader:
        return FixedWidthReader(
            f,
            self.colspecs,
            self.delimiter,
            self.comment,
            self.skiprows,
            self.infer_nrows,
        )

    def _remove_empty_lines(self, lines: list[list[T]]) -> list[list[T]]:
        """
        Returns the list of lines without the empty ones. With fixed-width
        fields, empty lines become arrays of empty strings.

        See PythonParser._remove_empty_lines.
        """
        return [
            line
            for line in lines
            if any(not isinstance(e, str) or e.strip() for e in line)
        ]


# endregion


# region io/parsers/readers.py


class _C_Parser_Defaults(ta.TypedDict):
    na_filter: ta.Literal[True]
    low_memory: ta.Literal[True]
    memory_map: ta.Literal[False]
    float_precision: None


_c_parser_defaults: _C_Parser_Defaults = {
    "na_filter": True,
    "low_memory": True,
    "memory_map": False,
    "float_precision": None,
}


class _Fwf_Defaults(ta.TypedDict):
    colspecs: ta.Literal["infer"]
    infer_nrows: ta.Literal[100]
    widths: None


_fwf_defaults: _Fwf_Defaults = {"colspecs": "infer", "infer_nrows": 100, "widths": None}
_c_unsupported = {"skipfooter"}


class TextFileReader(ta.Iterator):
    """

    Passed dialect overrides any of the related parser options

    """

    def __init__(
            self,
            f: FilePath | ReadCsvBuffer[bytes] | ReadCsvBuffer[str] | list,
            engine: CSVEngine | None = None,
            **kwds,
    ) -> None:
        if engine is not None:
            engine_specified = True
        else:
            engine = "python"
            engine_specified = False
        self.engine = engine
        self._engine_specified = kwds.get("engine_specified", engine_specified)

        _validate_skipfooter(kwds)

        dialect = _extract_dialect(kwds)
        if dialect is not None:
            if engine == "pyarrow":
                raise ValueError(
                    "The 'dialect' option is not supported with the 'pyarrow' engine"
                )
            kwds = _merge_with_dialect_properties(dialect, kwds)

        if kwds.get("header", "infer") == "infer":
            kwds["header"] = 0 if kwds.get("names") is None else None

        self.orig_options = kwds

        # miscellanea
        self._currow = 0

        options = self._get_options_with_defaults(engine)
        options["storage_options"] = kwds.get("storage_options", None)

        self.chunksize = options.pop("chunksize", None)
        self.nrows = options.pop("nrows", None)

        self._check_file_or_buffer(f, engine)
        self.options, self.engine = self._clean_options(options, engine)

        if "has_index_names" in kwds:
            self.options["has_index_names"] = kwds["has_index_names"]

        self.handles: IOHandles | None = None
        self._engine = self._make_engine(f, self.engine)

    def close(self) -> None:
        if self.handles is not None:
            self.handles.close()
        self._engine.close()

    def _get_options_with_defaults(self, engine: CSVEngine) -> dict[str, ta.Any]:
        kwds = self.orig_options

        options = {}
        default: object | None

        for argname, default in parser_defaults.items():
            value = kwds.get(argname, default)

            # see gh-12935
            if (
                    engine == "pyarrow"
                    and argname in _pyarrow_unsupported
                    and value != default
                    and value != getattr(value, "value", default)
            ):
                raise ValueError(
                    f"The {argname!r} option is not supported with the "
                    f"'pyarrow' engine"
                )
            options[argname] = value

        for argname, default in _c_parser_defaults.items():
            if argname in kwds:
                value = kwds[argname]

                if engine != "c" and value != default:
                    # TODO: Refactor this logic, its pretty convoluted
                    if "python" in engine and argname not in _python_unsupported:
                        pass
                    elif "pyarrow" in engine and argname not in _pyarrow_unsupported:
                        pass
                    else:
                        raise ValueError(
                            f"The {argname!r} option is not supported with the "
                            f"{engine!r} engine"
                        )
            else:
                value = default
            options[argname] = value

        if engine == "python-fwf":
            for argname, default in _fwf_defaults.items():
                options[argname] = kwds.get(argname, default)

        return options

    def _check_file_or_buffer(self, f, engine: CSVEngine) -> None:
        # see gh-16530
        if is_file_like(f) and engine != "c" and not hasattr(f, "__iter__"):
            # The C engine doesn't need the file-like to have the "__iter__"
            # attribute. However, the Python engine needs "__iter__(...)"
            # when iterating through such an object, meaning it
            # needs to have that attribute
            raise ValueError(
                "The 'python' engine cannot iterate through this file buffer."
            )
        if hasattr(f, "encoding"):
            file_encoding = f.encoding
            orig_reader_enc = self.orig_options.get("encoding", None)
            any_none = file_encoding is None or orig_reader_enc is None
            if file_encoding != orig_reader_enc and not any_none:
                file_path = getattr(f, "name", None)
                raise ValueError(
                    f"The specified reader encoding {orig_reader_enc} is different "
                    f"from the encoding {file_encoding} of file {file_path}."
                )

    def _clean_options(
            self, options: dict[str, ta.Any], engine: CSVEngine
    ) -> tuple[dict[str, ta.Any], CSVEngine]:
        result = options.copy()

        fallback_reason = None

        # C engine not supported yet
        if engine == "c":
            if options["skipfooter"] > 0:
                fallback_reason = "the 'c' engine does not support skipfooter"
                engine = "python"

        sep = options["delimiter"]

        if sep is not None and len(sep) > 1:
            if engine == "c" and sep == r"\s+":
                # delim_whitespace passed on to pandas._libs.parsers.TextReader
                result["delim_whitespace"] = True
                del result["delimiter"]
            elif engine not in ("python", "python-fwf"):
                # wait until regex engine integrated
                fallback_reason = (
                    f"the '{engine}' engine does not support "
                    "regex separators (separators > 1 char and "
                    r"different from '\s+' are interpreted as regex)"
                )
                engine = "python"
        elif sep is not None:
            encodeable = True
            encoding = sys.getfilesystemencoding() or "utf-8"
            try:
                if len(sep.encode(encoding)) > 1:
                    encodeable = False
            except UnicodeDecodeError:
                encodeable = False
            if not encodeable and engine not in ("python", "python-fwf"):
                fallback_reason = (
                    f"the separator encoded in {encoding} "
                    f"is > 1 char long, and the '{engine}' engine "
                    "does not support such separators"
                )
                engine = "python"

        quotechar = options["quotechar"]
        if quotechar is not None and isinstance(quotechar, (str, bytes)):
            if (
                    len(quotechar) == 1
                    and ord(quotechar) > 127
                    and engine not in ("python", "python-fwf")
            ):
                fallback_reason = (
                    "ord(quotechar) > 127, meaning the "
                    "quotechar is larger than one byte, "
                    f"and the '{engine}' engine does not support such quotechars"
                )
                engine = "python"

        if fallback_reason and self._engine_specified:
            raise ValueError(fallback_reason)

        if engine == "c":
            for arg in _c_unsupported:
                del result[arg]

        if "python" in engine:
            for arg in _python_unsupported:
                if fallback_reason and result[arg] != _c_parser_defaults.get(arg):
                    raise ValueError(
                        "Falling back to the 'python' engine because "
                        f"{fallback_reason}, but this causes {arg!r} to be "
                        "ignored as it is not supported by the 'python' engine."
                    )
                del result[arg]

        if fallback_reason:
            warnings.warn(
                (
                    "Falling back to the 'python' engine because "
                    f"{fallback_reason}; you can avoid this warning by specifying "
                    "engine='python'."
                ),
                ParserWarning,
                stacklevel=find_stack_level(),
            )

        index_col = options["index_col"]
        names = options["names"]
        converters = options["converters"]
        na_values = options["na_values"]
        skiprows = options["skiprows"]

        validate_header_arg(options["header"])

        if index_col is True:
            raise ValueError("The value of index_col couldn't be 'True'")
        if is_index_col(index_col):
            if not isinstance(index_col, (list, tuple, np.ndarray)):
                index_col = [index_col]
        result["index_col"] = index_col

        names = list(names) if names is not None else names

        # type conversion-related
        if converters is not None:
            if not isinstance(converters, dict):
                raise TypeError(
                    "Type converters must be a dict or subclass, "
                    f"input was a {type(converters).__name__}"
                )
        else:
            converters = {}

        # Converting values to NA
        keep_default_na = options["keep_default_na"]
        floatify = engine != "pyarrow"
        na_values, na_fvalues = _clean_na_values(
            na_values, keep_default_na, floatify=floatify
        )

        # handle skiprows; this is internally handled by the
        # c-engine, so only need for python and pyarrow parsers
        if engine == "pyarrow":
            if not is_integer(skiprows) and skiprows is not None:
                # pyarrow expects skiprows to be passed as an integer
                raise ValueError(
                    "skiprows argument must be an integer when using "
                    "engine='pyarrow'"
                )
        else:
            if is_integer(skiprows):
                skiprows = range(skiprows)
            if skiprows is None:
                skiprows = set()
            elif not callable(skiprows):
                skiprows = set(skiprows)

        # put stuff back
        result["names"] = names
        result["converters"] = converters
        result["na_values"] = na_values
        result["na_fvalues"] = na_fvalues
        result["skiprows"] = skiprows

        return result, engine

    def __next__(self) -> DataFrame:
        try:
            return self.get_chunk()
        except StopIteration:
            self.close()
            raise

    def _make_engine(
            self,
            f: FilePath | ReadCsvBuffer[bytes] | ReadCsvBuffer[str] | list | ta.IO,
            engine: CSVEngine = "c",
    ) -> ParserBase:
        mapping: dict[str, type[ParserBase]] = {
            "c": CParserWrapper,
            "python": PythonParser,
            "pyarrow": ArrowParserWrapper,
            "python-fwf": FixedWidthFieldParser,
        }

        if engine not in mapping:
            raise ValueError(
                f"Unknown engine: {engine} (valid options are {mapping.keys()})"
            )
        if not isinstance(f, list):
            # open file here
            is_text = True
            mode = "r"
            if engine == "pyarrow":
                is_text = False
                mode = "rb"
            elif (
                    engine == "c"
                    and self.options.get("encoding", "utf-8") == "utf-8"
                    and isinstance(stringify_path(f), str)
            ):
                # c engine can decode utf-8 bytes, adding TextIOWrapper makes
                # the c-engine especially for memory_map=True far slower
                is_text = False
                if "b" not in mode:
                    mode += "b"
            self.handles = get_handle(
                f,
                mode,
                encoding=self.options.get("encoding", None),
                compression=self.options.get("compression", None),
                memory_map=self.options.get("memory_map", False),
                is_text=is_text,
                errors=self.options.get("encoding_errors", "strict"),
                storage_options=self.options.get("storage_options", None),
            )
            assert self.handles is not None
            f = self.handles.handle

        elif engine != "python":
            msg = f"Invalid file path or buffer object type: {type(f)}"
            raise ValueError(msg)

        try:
            return mapping[engine](f, **self.options)
        except Exception:
            if self.handles is not None:
                self.handles.close()
            raise

    def _failover_to_python(self) -> None:
        raise AbstractMethodError(self)

    def read(self, nrows: int | None = None) -> DataFrame:
        if self.engine == "pyarrow":
            try:
                # error: "ParserBase" has no attribute "read"
                df = self._engine.read()  # type: ignore[attr-defined]
            except Exception:
                self.close()
                raise
        else:
            nrows = validate_integer("nrows", nrows)
            try:
                # error: "ParserBase" has no attribute "read"
                (
                    index,
                    columns,
                    col_dict,
                ) = self._engine.read(  # type: ignore[attr-defined]
                    nrows
                )
            except Exception:
                self.close()
                raise

            if index is None:
                if col_dict:
                    # Any column is actually fine:
                    new_rows = len(next(iter(col_dict.values())))
                    index = RangeIndex(self._currow, self._currow + new_rows)
                else:
                    new_rows = 0
            else:
                new_rows = len(index)

            if hasattr(self, "orig_options"):
                dtype_arg = self.orig_options.get("dtype", None)
            else:
                dtype_arg = None

            if isinstance(dtype_arg, dict):
                dtype = collections.defaultdict(lambda: None)  # type: ignore[var-annotated]
                dtype.update(dtype_arg)
            elif dtype_arg is not None and pandas_dtype(dtype_arg) in (
                    np.str_,
                    np.object_,
            ):
                dtype = collections.defaultdict(lambda: dtype_arg)
            else:
                dtype = None

            if dtype is not None:
                new_col_dict = {}
                for k, v in col_dict.items():
                    d = (
                        dtype[k]
                        if pandas_dtype(dtype[k]) in (np.str_, np.object_)
                        else None
                    )
                    new_col_dict[k] = Series(v, index=index, dtype=d, copy=False)
            else:
                new_col_dict = col_dict

            df = DataFrame(
                new_col_dict,
                columns=columns,
                index=index,
                copy=False,
            )

            self._currow += new_rows
        return df

    def get_chunk(self, size: int | None = None) -> DataFrame:
        if size is None:
            size = self.chunksize
        if self.nrows is not None:
            if self._currow >= self.nrows:
                raise StopIteration
            if size is None:
                size = self.nrows - self._currow
            else:
                size = min(size, self.nrows - self._currow)
        return self.read(nrows=size)

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: types.TracebackType | None,
    ) -> None:
        self.close()


# endregion


# region io/parsers/c_parser_wrapper.py


class TextReader:
    """
    _libs/parsers.pyx
    _libs/src/parser/*.c
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError


class CParserWrapper(ParserBase):
    low_memory: bool
    _reader: TextReader

    def __init__(self, src: ReadCsvBuffer[str], **kwds) -> None:
        super().__init__(kwds)
        self.kwds = kwds
        kwds = kwds.copy()

        self.low_memory = kwds.pop("low_memory", False)

        # #2442
        # error: Cannot determine type of 'index_col'
        kwds["allow_leading_cols"] = (
                self.index_col is not False  # type: ignore[has-type]
        )

        # GH20529, validate usecol arg before TextReader
        kwds["usecols"] = self.usecols

        # Have to pass int, would break tests using TextReader directly otherwise :(
        kwds["on_bad_lines"] = self.on_bad_lines.value

        for key in (
                "storage_options",
                "encoding",
                "memory_map",
                "compression",
        ):
            kwds.pop(key, None)

        kwds["dtype"] = ensure_dtype_objs(kwds.get("dtype", None))
        if "dtype_backend" not in kwds or kwds["dtype_backend"] is no_default:
            kwds["dtype_backend"] = "numpy"
        if kwds["dtype_backend"] == "pyarrow":
            # Fail here loudly instead of in cython after reading
            import_optional_dependency("pyarrow")
        self._reader = TextReader(src, **kwds)

        self.unnamed_cols = self._reader.unnamed_cols

        # error: Cannot determine type of 'names'
        passed_names = self.names is None  # type: ignore[has-type]

        if self._reader.header is None:
            self.names = None
        else:
            # error: Cannot determine type of 'names'
            # error: Cannot determine type of 'index_names'
            (
                self.names,  # type: ignore[has-type]
                self.index_names,
                self.col_names,
                passed_names,
            ) = self._extract_multi_indexer_columns(
                self._reader.header,
                self.index_names,  # type: ignore[has-type]
                passed_names,
            )

        # error: Cannot determine type of 'names'
        if self.names is None:  # type: ignore[has-type]
            self.names = list(range(self._reader.table_width))

        # gh-9755
        #
        # need to set orig_names here first
        # so that proper indexing can be done
        # with _set_noconvert_columns
        #
        # once names has been filtered, we will
        # then set orig_names again to names
        # error: Cannot determine type of 'names'
        self.orig_names = self.names[:]  # type: ignore[has-type]

        if self.usecols:
            usecols = evaluate_callable_usecols(self.usecols, self.orig_names)

            # GH 14671
            # assert for mypy, orig_names is List or None, None would error in issubset
            assert self.orig_names is not None
            if self.usecols_dtype == "string" and not set(usecols).issubset(
                    self.orig_names
            ):
                self._validate_usecols_names(usecols, self.orig_names)

            # error: Cannot determine type of 'names'
            if len(self.names) > len(usecols):  # type: ignore[has-type]
                # error: Cannot determine type of 'names'
                self.names = [  # type: ignore[has-type]
                    n
                    # error: Cannot determine type of 'names'
                    for i, n in enumerate(self.names)  # type: ignore[has-type]
                    if (i in usecols or n in usecols)
                ]

            # error: Cannot determine type of 'names'
            if len(self.names) < len(usecols):  # type: ignore[has-type]
                # error: Cannot determine type of 'names'
                self._validate_usecols_names(
                    usecols,
                    self.names,  # type: ignore[has-type]
                )

        # error: Cannot determine type of 'names'
        validate_parse_dates_presence(self.parse_dates, self.names)  # type: ignore[has-type]
        self._set_noconvert_columns()

        # error: Cannot determine type of 'names'
        self.orig_names = self.names  # type: ignore[has-type]

        # error: Cannot determine type of 'index_col'
        if self._reader.leading_cols == 0 and is_index_col(
                self.index_col  # type: ignore[has-type]
        ):
            (
                index_names,
                # error: Cannot determine type of 'names'
                self.names,  # type: ignore[has-type]
                self.index_col,
            ) = self._clean_index_names(
                # error: Cannot determine type of 'names'
                self.names,  # type: ignore[has-type]
                # error: Cannot determine type of 'index_col'
                self.index_col,  # type: ignore[has-type]
            )

            if self.index_names is None:
                self.index_names = index_names

        if self._reader.header is None and not passed_names:
            assert self.index_names is not None
            self.index_names = [None] * len(self.index_names)

        self._implicit_index = self._reader.leading_cols > 0

    def close(self) -> None:
        # close handles opened by C parser
        try:
            self._reader.close()
        except ValueError:
            pass

    def _set_noconvert_columns(self) -> None:
        """
        Set the columns that should not undergo dtype conversions.

        Currently, any column that is involved with date parsing will not
        undergo such conversions.
        """
        assert self.orig_names is not None
        # error: Cannot determine type of 'names'

        # much faster than using orig_names.index(x) xref GH#44106
        names_dict = {x: i for i, x in enumerate(self.orig_names)}
        col_indices = [names_dict[x] for x in self.names]  # type: ignore[has-type]
        # error: Cannot determine type of 'names'
        noconvert_columns = self._set_noconvert_dtype_columns(
            col_indices,
            self.names,  # type: ignore[has-type]
        )
        for col in noconvert_columns:
            self._reader.set_noconvert(col)

    def read(
            self,
            nrows: int | None = None,
    ) -> tuple[
        Index | MultiIndex | None,
        ta.Sequence[ta.Hashable] | MultiIndex,
        ta.Mapping[ta.Hashable, AnyArrayLike],
    ]:
        index: Index | MultiIndex | None
        column_names: ta.Sequence[ta.Hashable] | MultiIndex
        try:
            if self.low_memory:
                chunks = self._reader.read_low_memory(nrows)
                # destructive to chunks
                data = _concatenate_chunks(chunks, self.names)  # type: ignore[has-type]

            else:
                data = self._reader.read(nrows)
        except StopIteration:
            if self._first_chunk:
                self._first_chunk = False
                names = dedup_names(
                    self.orig_names,
                    is_potential_multi_index(self.orig_names, self.index_col),
                )
                index, columns, col_dict = self._get_empty_meta(
                    names,
                    dtype=self.dtype,
                )
                # error: Incompatible types in assignment (expression has type
                # "list[Hashable] | MultiIndex", variable has type "list[Hashable]")
                columns = self._maybe_make_multi_index_columns(  # type: ignore[assignment]
                    columns, self.col_names
                )

                columns = _filter_usecols(self.usecols, columns)

                col_dict = {k: v for k, v in col_dict.items() if k in columns}

                return index, columns, col_dict

            else:
                self.close()
                raise

        # Done with first read, next time raise StopIteration
        self._first_chunk = False

        # error: Cannot determine type of 'names'
        names = self.names  # type: ignore[has-type]

        if self._reader.leading_cols:
            # implicit index, no index names
            arrays = []

            if self.index_col and self._reader.leading_cols != len(self.index_col):
                raise ParserError(
                    "Could not construct index. Requested to use "
                    f"{len(self.index_col)} number of columns, but "
                    f"{self._reader.leading_cols} left to parse."
                )

            for i in range(self._reader.leading_cols):
                if self.index_col is None:
                    values = data.pop(i)
                else:
                    values = data.pop(self.index_col[i])

                if self._should_parse_dates(i):
                    values = date_converter(
                        values,
                        col=self.index_names[i]
                        if self.index_names is not None
                        else None,
                        dayfirst=self.dayfirst,
                        cache_dates=self.cache_dates,
                        date_format=self.date_format,
                    )
                arrays.append(values)

            index = ensure_index_from_sequences(arrays)

            names = _filter_usecols(self.usecols, names)

            names = dedup_names(names, is_potential_multi_index(names, self.index_col))

            # rename dict keys
            data_tups = sorted(data.items())
            data = {k: v for k, (i, v) in zip(names, data_tups)}

            date_data = self._do_date_conversions(names, data)

            # maybe create a mi on the columns
            column_names = self._maybe_make_multi_index_columns(names, self.col_names)

        else:
            # rename dict keys
            data_tups = sorted(data.items())

            # ugh, mutation

            # assert for mypy, orig_names is List or None, None would error in list(...)
            assert self.orig_names is not None
            names = list(self.orig_names)
            names = dedup_names(names, is_potential_multi_index(names, self.index_col))

            names = _filter_usecols(self.usecols, names)

            # columns as list
            alldata = [x[1] for x in data_tups]
            if self.usecols is None:
                self._check_data_length(names, alldata)

            data = {k: v for k, (i, v) in zip(names, data_tups)}

            date_data = self._do_date_conversions(names, data)
            index, column_names = self._make_index(alldata, names)

        return index, column_names, date_data


@ta.overload
def evaluate_callable_usecols(
        usecols: ta.Callable[[ta.Hashable], object],
        names: ta.Iterable[ta.Hashable],
) -> set[int]: ...


@ta.overload
def evaluate_callable_usecols(
        usecols: SequenceT, names: ta.Iterable[ta.Hashable]
) -> SequenceT: ...


def evaluate_callable_usecols(
        usecols: ta.Callable[[ta.Hashable], object] | SequenceT,
        names: ta.Iterable[ta.Hashable],
) -> SequenceT | set[int]:
    """
    Check whether or not the 'usecols' parameter
    is a callable.  If so, enumerates the 'names'
    parameter and returns a set of indices for
    each entry in 'names' that evaluates to True.
    If not a callable, returns 'usecols'.
    """
    if callable(usecols):
        return {i for i, name in enumerate(names) if usecols(name)}
    return usecols


# endregion


# region io/parsers/readers.py


class _read_shared(ta.TypedDict, ta.Generic[HashableT], total=False):
    # annotations shared between read_csv/fwf/table's overloads
    # NOTE: Keep in sync with the annotations of the implementation
    sep: str | None | NoDefault
    delimiter: str | None | NoDefault
    header: int | ta.Sequence[int] | None | ta.Literal['infer']
    names: ta.Sequence[ta.Hashable] | None | NoDefault
    index_col: IndexLabel | ta.Literal[False] | None
    usecols: UsecolsArgType
    dtype: DtypeArg | None
    engine: CSVEngine | None
    converters: ta.Mapping[HashableT, ta.Callable] | None
    true_values: list | None
    false_values: list | None
    skipinitialspace: bool
    skiprows: list[int] | int | ta.Callable[[ta.Hashable], bool] | None
    skipfooter: int
    nrows: int | None
    na_values: ta.Union[
        ta.Hashable,
        ta.Iterable[ta.Hashable],
        ta.Mapping[ta.Hashable, ta.Iterable[ta.Hashable]],
        None,
    ]
    keep_default_na: bool
    na_filter: bool
    skip_blank_lines: bool
    parse_dates: bool | ta.Sequence[ta.Hashable] | None
    date_format: str | dict[ta.Hashable, str] | None
    dayfirst: bool
    cache_dates: bool
    compression: CompressionOptions
    thousands: str | None
    decimal: str
    lineterminator: str | None
    quotechar: str
    quoting: int
    doublequote: bool
    escapechar: str | None
    comment: str | None
    encoding: str | None
    encoding_errors: str | None
    dialect: str | csv.Dialect | None
    on_bad_lines: str
    low_memory: bool
    memory_map: bool
    float_precision: ta.Literal['high', 'legacy', 'round_trip'] | None
    storage_options: StorageOptions | None
    dtype_backend: DtypeBackend | NoDefault


def read_csv(
        filepath_or_buffer: FilePath | ReadCsvBuffer[bytes] | ReadCsvBuffer[str],
        *,
        sep: str | None | NoDefault = no_default,
        delimiter: str | None | NoDefault = None,
        # Column and Index Locations and Names
        header: int | ta.Sequence[int] | None | ta.Literal['infer'] = 'infer',
        names: ta.Sequence[ta.Hashable] | None | NoDefault = no_default,
        index_col: IndexLabel | ta.Literal[False] | None = None,
        usecols: UsecolsArgType = None,
        # General Parsing Configuration
        dtype: DtypeArg | None = None,
        engine: CSVEngine | None = None,
        converters: ta.Mapping[HashableT, ta.Callable] | None = None,
        true_values: list | None = None,
        false_values: list | None = None,
        skipinitialspace: bool = False,
        skiprows: list[int] | int | ta.Callable[[ta.Hashable], bool] | None = None,
        skipfooter: int = 0,
        nrows: int | None = None,
        # NA and Missing Data Handling
        na_values: ta.Union[
            ta.Hashable,
            ta.Iterable[ta.Hashable],
            ta.Mapping[ta.Hashable, ta.Iterable[ta.Hashable]],
            None,
        ] = None,
        keep_default_na: bool = True,
        na_filter: bool = True,
        skip_blank_lines: bool = True,
        # Datetime Handling
        parse_dates: bool | ta.Sequence[ta.Hashable] | None = None,
        date_format: str | dict[ta.Hashable, str] | None = None,
        dayfirst: bool = False,
        cache_dates: bool = True,
        # Iteration
        iterator: bool = False,
        chunksize: int | None = None,
        # Quoting, Compression, and File Format
        compression: CompressionOptions = 'infer',
        thousands: str | None = None,
        decimal: str = '.',
        lineterminator: str | None = None,
        quotechar: str = "'",
        quoting: int = csv.QUOTE_MINIMAL,
        doublequote: bool = True,
        escapechar: str | None = None,
        comment: str | None = None,
        encoding: str | None = None,
        encoding_errors: str | None = 'strict',
        dialect: str | csv.Dialect | None = None,
        # Error Handling
        on_bad_lines: str = 'error',
        # Internal
        low_memory: bool = _c_parser_defaults['low_memory'],
        memory_map: bool = False,
        float_precision: ta.Literal['high', 'legacy', 'round_trip'] | None = None,
        storage_options: StorageOptions | None = None,
        dtype_backend: DtypeBackend | NoDefault = no_default,
) -> DataFrame | 'TextFileReader':
    raise NotImplementedError


# endregion
