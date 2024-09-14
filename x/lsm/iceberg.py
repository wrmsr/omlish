"""
https://iceberg.apache.org/spec/ <-- winner
"""
import enum


class PrimitiveType(enum.Enum):
    BOOLEAN = 'boolean'  # True or false
    INT = 'int'  # 32-bit signed integers; Can promote to long
    LONG = 'long'  # 64-bit signed integers
    FLOAT = 'float'  # 32-bit IEEE 754 floating point; Can promote to double
    DOUBLE = 'double'  # 64-bit IEEE 754 floating point
    DECIMAL = 'decimal(P,S)'  # Fixed-point decimal; precision P, scale S; Scale is fixed, precision must be 38 or less
    DATE = 'date'  # Calendar date without timezone or time
    TIME = 'time'  # Time of day, microsecond precision, without date, timezone
    TIMESTAMP = 'timestamp'  # Timestamp, microsecond precision, without timezone
    TIMESTAMPTZ = 'timestamptz'  # Timestamp, microsecond precision, with timezone
    TIMESTAMP_NS = 'timestamp_ns'  # Version 3: Timestamp, nanosecond precision, without timezone
    TIMESTAMPTZ_NS = 'timestamptz_ns'  # Version 3: Timestamp, nanosecond precision, with timezone
    STRING = 'string'  # Arbitrary-length character sequences; Encoded with UTF-8
    UUID = 'uuid'  # Universally unique identifiers; Should use 16-byte fixed
    FIXED = 'fixed(L)'  # Fixed-length byte array of length L
    BINARY = 'binary'  # Arbitrary-length byte array


"""
reserved fields
header = ["Field id", "name", "Type", "Description"]
[2147483646, "_file", "string", "Path of the file in which a row is stored"],
[2147483645, "_pos", "long", "Ordinal position of a row in the source data file"],
[2147483644, "_deleted", "boolean", "Whether the row has been deleted"],
[2147483643, "_spec_id", "int", "Spec ID used to track the file containing a row"],
[2147483642, "_partition", "struct", "Partition to which a row belongs"],
[2147483546, "file_path", "string", "Path of a file, used in position-based delete files"],
[2147483545, "pos", "long", "Ordinal position of a row, used in position-based delete files"],
[2147483544, "row", "struct<...>", "Deleted row values, used in position-based delete files"]
"""

def _main():
    pass


if __name__ == '__main___':
    _main()
