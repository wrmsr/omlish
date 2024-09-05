"""
https://github.com/apache/arrow/blob/7a24729341d4b7cc56ce072df86d2d28b4ddcf96/python/pyarrow/_csv.pyx#L605

read_csv(
    input_file: str | Path | FileLike,
    read_options: ReadOptions | None = None,
    parse_options: ParseOptions | None = None,
    convert_options: ConvertOptions | None = None,
    memory_pool: MemoryPool | None = None,
):
 - input_file : string, path or file-like object
     The location of CSV data.  If a string or path, and if it ends with a recognized compressed file extension (e.g.
     ".gz" or ".bz2"), the data is automatically decompressed when reading.
 - read_options : pyarrow.csv.ReadOptions, optional
     Options for the CSV reader (see pyarrow.csv.ReadOptions constructor for defaults)
 - parse_options : pyarrow.csv.ParseOptions, optional
     Options for the CSV parser (see pyarrow.csv.ParseOptions constructor for defaults)
 - convert_options : pyarrow.csv.ConvertOptions, optional
     Options for converting CSV data (see pyarrow.csv.ConvertOptions constructor for defaults)
 - memory_pool : MemoryPool, optional
     Pool to allocate Table memory from

class pyarrow.csv.ReadOptions(
    use_threads: bool = True,
    block_size: int | None = None,
    skip_rows: int = 0,
    skip_rows_after_names: int = 0,
    column_names: ta.Sequence[str] | None = None,
    autogenerate_column_names: bool = False,
    encoding: str = 'utf8',
):
 - use_threads : bool, optional (default True)
     Whether to use multiple threads to accelerate reading
 - block_size : int, optional
     How much bytes to process at a time from the input stream. This will determine multi-threading granularity as well
     as the size of individual record batches or table chunks. Minimum valid value for block size is 1
 - skip_rows : int, optional (default 0)
     The number of rows to skip before the column names (if any) and the CSV data.
 - skip_rows_after_names : int, optional (default 0)
     The number of rows to skip after the column names. This number can be larger than the number of rows in one block,
     and empty rows are counted. The order of application is as follows: - skip_rows is applied (if non-zero); - column
     names are read (unless column_names is set); - skip_rows_after_names is applied (if non-zero).
 - column_names : list, optional
     The column names of the target table. If empty, fall back on autogenerate_column_names.
 - autogenerate_column_names : bool, optional (default False)
     Whether to autogenerate column names if column_names is empty. If true, column names will be of the form “f0”,
     “f1”… If false, column names will be read from the first CSV row after skip_rows.
 - encoding : str, optional (default ‘utf8’)
     The character encoding of the CSV data. Columns that cannot decode using this encoding can still be read as Binary.

class pyarrow.csv.ParseOptions(
    delimiter: Char = ',',
    quote_char: Char = '"',
    double_quote: bool = True,
    escape_char : Char | ta.Literal[False] = False,
    newlines_in_values: bool = False,
    ignore_empty_lines: bool = False,
    invalid_row_handler: ta.Callable[[ta.Any], ta.Literal['skip', 'error'] | None = None,
):
 - delimiter : 1-character str, optional (default ‘,’)
     The character delimiting individual cells in the CSV data.
 - quote_char : 1-character str or False, optional (default ‘”’)
     The character used optionally for quoting CSV values (False if quoting is not allowed).
 - double_quote : bool, optional (default True)
     Whether two quotes in a quoted CSV value denote a single quote in the data.
 - escape_char : 1-character str or False, optional (default False)
     The character used optionally for escaping special characters (False if escaping is not allowed).
 - newlines_in_values : bool, optional (default False)
     Whether newline characters are allowed in CSV values. Setting this to True reduces the performance of
     multi-threaded CSV reading.
 - ignore_empty_lines : bool, optional (default True)
     Whether empty lines are ignored in CSV input. If False, an empty line is interpreted as containing a single empty
     value (assuming a one-column CSV file).
 - invalid_row_handler : callable(), optional (default None)
     If not None, this object is called for each CSV row that fails parsing (because of a mismatching number of
     columns). It should accept a single InvalidRow argument and return either “skip” or “error” depending on the
     desired outcome.

class pyarrow.csv.ConvertOptions(
    check_utf8: bool = True,
    column_types: pa.Schema | dict | None = None,
    null_values: ta.Sequence | None = None,
    true_values: taSequence | None = None,
    false_values: ta.Sequence | None = None,
    decimal_point: Char = '.',
    strings_can_be_null: bool = False,
    quoted_strings_can_be_null: bool = True,
    include_columns: ta.Sequence[str] | None = None,
    include_missing_columns: bool = False,
    auto_dict_encode: bool = False,
    auto_dict_max_cardinality: int | None = None,
    timestamp_parsers: ta.Sequence[ta.Callable] | None = None,
):
 - check_utf8 : bool, optional (default True)
     Whether to check UTF8 validity of string columns.
 - column_types : pyarrow.Schema or dict, optional
     Explicitly map column names to column types. Passing this argument disables type inference on the defined columns.
 - null_values : list, optional
     A sequence of strings that denote nulls in the data (defaults are appropriate in most cases). Note that by default,
     string columns are not checked for null values. To enable null checking for those, specify
     strings_can_be_null=True.
 - true_values : list, optional
     A sequence of strings that denote true booleans in the data (defaults are appropriate in most cases).
 - false_values : list, optional
     A sequence of strings that denote false booleans in the data (defaults are appropriate in most cases).
 - decimal_point : 1-character str, optional (default ‘.’)
     The character used as decimal point in floating-point and decimal data.
 - strings_can_be_null : bool, optional (default False)
     Whether string / binary columns can have null values. If true, then strings in null_values are considered null for
     string columns. If false, then all strings are valid string values.
 - quoted_strings_can_be_null : bool, optional (default True)
     Whether quoted values can be null. If true, then strings in “null_values” are also considered null when they appear
     quoted in the CSV file. Otherwise, quoted values are never considered null.
 - include_columns : list, optional
     The names of columns to include in the Table. If empty, the Table will include all columns from the CSV file. If
     not empty, only these columns will be included, in this order.
 - include_missing_columns : bool, optional (default False)
     If false, columns in include_columns but not in the CSV file will error out. If true, columns in include_columns
     but not in the CSV file will produce a column of nulls (whose type is selected using column_types, or null by
     default). This option is ignored if include_columns is empty.
 - auto_dict_encode : bool, optional (default False)
     Whether to try to automatically dict-encode string / binary data. If true, then when type inference detects a
     string or binary column, it it dict-encoded up to auto_dict_max_cardinality distinct values (per chunk), after
     which it switches to regular encoding. This setting is ignored for non-inferred columns (those in column_types).
 - auto_dict_max_cardinality : int, optional
     The maximum dictionary cardinality for auto_dict_encode. This value is per chunk.
 - timestamp_parsers : list, optional
     A sequence of strptime()-compatible format strings, tried in order when attempting to infer or convert timestamp
     values (the special value ISO8601() can also be given). By default, a fast built-in ISO-8601 parser is used.
"""
import io

import pyarrow as pa
import pyarrow.csv


def test_pyarrow_csv():
    s = (
        "animals,n_legs,entry\n"
        "Flamingo,2,2022-03-01\n"
        "Horse,4,2022-03-02\n"
        "Brittle stars,5,2022-03-03\n"
        "Centipede,100,2022-03-04"
    )

    pa.csv.ConvertOptions

    source = io.BytesIO(s.encode())
    tbl = pa.csv.read_csv(source)

    print(tbl)
