"""
https://github.com/apache/arrow/blob/7a24729341d4b7cc56ce072df86d2d28b4ddcf96/python/pyarrow/_csv.pyx#L605

read_csv(
    input_file,
    read_options=None,
    parse_options=None,
    convert_options=None,
    memory_pool=None,
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
    use_threads=None,
    *,
    block_size=None,
    skip_rows=None,
    skip_rows_after_names=None,
    column_names=None,
    autogenerate_column_names=None,
    encoding='utf8',
):
 - use_threadsbool, optional (default True)
     Whether to use multiple threads to accelerate reading
 - block_sizeint, optional
     How much bytes to process at a time from the input stream. This will determine multi-threading granularity as well
     as the size of individual record batches or table chunks. Minimum valid value for block size is 1
 - skip_rowsint, optional (default 0)
     The number of rows to skip before the column names (if any) and the CSV data.
 - skip_rows_after_namesint, optional (default 0)
     The number of rows to skip after the column names. This number can be larger than the number of rows in one block,
     and empty rows are counted. The order of application is as follows: - skip_rows is applied (if non-zero); - column
     names are read (unless column_names is set); - skip_rows_after_names is applied (if non-zero).
 - column_nameslist, optional
     The column names of the target table. If empty, fall back on autogenerate_column_names.
 - autogenerate_column_namesbool, optional (default False)
     Whether to autogenerate column names if column_names is empty. If true, column names will be of the form “f0”,
     “f1”… If false, column names will be read from the first CSV row after skip_rows.
 - encodingstr, optional (default ‘utf8’)
     The character encoding of the CSV data. Columns that cannot decode using this encoding can still be read as Binary.

class pyarrow.csv.ParseOptions(
    delimiter=None,
    *,
    quote_char=None,
    double_quote=None,
    escape_char=None,
    newlines_in_values=None,
    ignore_empty_lines=None,
    invalid_row_handler=None,
):
 - delimiter1-character str, optional (default ‘,’)
     The character delimiting individual cells in the CSV data.
 - quote_char1-character str or False, optional (default ‘”’)
     The character used optionally for quoting CSV values (False if quoting is not allowed).
 - double_quotebool, optional (default True)
     Whether two quotes in a quoted CSV value denote a single quote in the data.
 - escape_char1-character str or False, optional (default False)
     The character used optionally for escaping special characters (False if escaping is not allowed).
 - newlines_in_valuesbool, optional (default False)
     Whether newline characters are allowed in CSV values. Setting this to True reduces the performance of
     multi-threaded CSV reading.
 - ignore_empty_linesbool, optional (default True)
     Whether empty lines are ignored in CSV input. If False, an empty line is interpreted as containing a single empty
     value (assuming a one-column CSV file).
 - invalid_row_handlercallable(), optional (default None)
     If not None, this object is called for each CSV row that fails parsing (because of a mismatching number of
     columns). It should accept a single InvalidRow argument and return either “skip” or “error” depending on the
     desired outcome.
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

    source = io.BytesIO(s.encode())
    tbl = pa.csv.read_csv(source)

    print(tbl)
