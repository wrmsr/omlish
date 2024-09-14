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

"""
partition transforms
Transform name	Description	Source types	Result type
identity	Source value, unmodified	Any	Source type
bucket[N]	Hash of value, mod N (see below)	int, long, decimal, date, time, timestamp, timestamptz, timestamp_ns, timestamptz_ns, string, uuid, fixed, binary	int
truncate[W]	Value truncated to width W (see below)	int, long, decimal, string, binary	Source type
year	Extract a date or timestamp year, as years from 1970	date, timestamp, timestamptz, timestamp_ns, timestamptz_ns	int
month	Extract a date or timestamp month, as months from 1970-01-01	date, timestamp, timestamptz, timestamp_ns, timestamptz_ns	int
day	Extract a date or timestamp day, as days from 1970-01-01	date, timestamp, timestamptz, timestamp_ns, timestamptz_ns	int
hour	Extract a timestamp hour, as hours from 1970-01-01 00:00:00	timestamp, timestamptz, timestamp_ns, timestamptz_ns	int
void	Always produces null	Any	Source type or int
"""

"""
bucket transform
def bucket_N(x) = (murmur3_x86_32_hash(x) & Integer.MAX_VALUE) % N
"""

"""
Truncate Transform Details
Type	Config	Truncate specification	Examples
int	W, width	v - (v % W) remainders must be positive [1]	W=10: 1 ￫ 0, -1 ￫ -10
long	W, width	v - (v % W) remainders must be positive [1]	W=10: 1 ￫ 0, -1 ￫ -10
decimal	W, width (no scale)	scaled_W = decimal(W, scale(v)) v - (v % scaled_W) [1, 2]	W=50, s=2: 10.65 ￫ 10.50
string	L, length	Substring of length L: v.substring(0, L) [3]	L=3: iceberg ￫ ice
binary	L, length	Sub array of length L: v.subarray(0, L) [4]	L=3: \x01\x02\x03\x04\x05 ￫ \x01\x02\x03
"""

"""
manifest file
v1	v2	Key	Value
required	required	schema	JSON representation of the table schema at the time the manifest was written
optional	required	schema-id	ID of the schema used to write the manifest as a string
required	required	partition-spec	JSON fields representation of the partition spec used to write the manifest
optional	required	partition-spec-id	ID of the partition spec used to write the manifest as a string
optional	required	format-version	Table format version number of the manifest as a string
required	content	Type of content files tracked by the manifest: "data" or "deletes"
"""

"""
manifest_entry
v1	v2	Field id, name	Type	Description
required	required	0 status	int with meaning: 0: EXISTING 1: ADDED 2: DELETED	Used to track additions and deletions. Deletes are informational only and not used in scans.
required	optional	1 snapshot_id	long	Snapshot id where the file was added, or deleted if status is 2. Inherited when null.
optional	3 sequence_number	long	Data sequence number of the file. Inherited when null and status is 1 (added).
optional	4 file_sequence_number	long	File sequence number indicating when the file was added. Inherited when null and status is 1 (added).
required	required	2 data_file	data_file struct (see below)	File path, partition tuple, metrics, ...
"""

"""
data_file
v1	v2	Field id, name	Type	Description
required	134 content	int with meaning: 0: DATA, 1: POSITION DELETES, 2: EQUALITY DELETES	Type of content stored by the data file: data, equality deletes, or position deletes (all v1 files are data files)
required	required	100 file_path	string	Full URI for the file with FS scheme
required	required	101 file_format	string	String file format name, avro, orc or parquet
required	required	102 partition	struct<...>	Partition data tuple, schema based on the partition spec output using partition field ids for the struct field ids
required	required	103 record_count	long	Number of records in this file
required	required	104 file_size_in_bytes	long	Total file size in bytes
required		105 block_size_in_bytes	long	Deprecated. Always write a default in v1. Do not write in v2.
optional		106 file_ordinal	int	Deprecated. Do not write.
optional		107 sort_columns	list<112: int>	Deprecated. Do not write.
optional	optional	108 column_sizes	map<117: int, 118: long>	Map from column id to the total size on disk of all regions that store the column. Does not include bytes necessary to read other columns, like footers. Leave null for row-oriented formats (Avro)
optional	optional	109 value_counts	map<119: int, 120: long>	Map from column id to number of values in the column (including null and NaN values)
optional	optional	110 null_value_counts	map<121: int, 122: long>	Map from column id to number of null values in the column
optional	optional	137 nan_value_counts	map<138: int, 139: long>	Map from column id to number of NaN values in the column
optional	optional	111 distinct_counts	map<123: int, 124: long>	Map from column id to number of distinct values in the column; distinct counts must be derived using values in the file by counting or using sketches, but not using methods like merging existing distinct counts
optional	optional	125 lower_bounds	map<126: int, 127: binary>	Map from column id to lower bound in the column serialized as binary [1]. Each value must be less than or equal to all non-null, non-NaN values in the column for the file [2]
optional	optional	128 upper_bounds	map<129: int, 130: binary>	Map from column id to upper bound in the column serialized as binary [1]. Each value must be greater than or equal to all non-null, non-Nan values in the column for the file [2]
optional	optional	131 key_metadata	binary	Implementation-specific key metadata for encryption
optional	optional	132 split_offsets	list<133: long>	Split offsets for the data file. For example, all row group offsets in a Parquet file. Must be sorted ascending
optional	135 equality_ids	list<136: int>	Field ids used to determine row equality in equality delete files. Required when content=2 and should be null otherwise. Fields with ids listed in this column must be present in the delete file
optional	optional	140 sort_order_id	int	ID representing sort order for this file [3].
"""

"""
snapshot
v1	v2	Field	Description
required	required	snapshot-id	A unique long ID
optional	optional	parent-snapshot-id	The snapshot ID of the snapshot's parent. Omitted for any snapshot with no parent
required	sequence-number	A monotonically increasing long that tracks the order of changes to a table
required	required	timestamp-ms	A timestamp when the snapshot was created, used for garbage collection and table inspection
optional	required	manifest-list	The location of a manifest list for this snapshot that tracks manifest files with additional metadata
optional		manifests	A list of manifest file locations. Must be omitted if manifest-list is present
optional	required	summary	A string map that summarizes the snapshot changes, including operation (see below)
optional	optional	schema-id	ID of the table's current schema when the snapshot was created
"""

"""
Manifest list files store manifest_file, a struct with the following fields:
v1	v2	Field id, name	Type	Description
required	required	500 manifest_path	string	Location of the manifest file
required	required	501 manifest_length	long	Length of the manifest file in bytes
required	required	502 partition_spec_id	int	ID of a partition spec used to write the manifest; must be listed in table metadata partition-specs
required	517 content	int with meaning: 0: data, 1: deletes	The type of files tracked by the manifest, either data or delete files; 0 for all v1 manifests
required	515 sequence_number	long	The sequence number when the manifest was added to the table; use 0 when reading v1 manifest lists
required	516 min_sequence_number	long	The minimum data sequence number of all live data or delete files in the manifest; use 0 when reading v1 manifest lists
required	required	503 added_snapshot_id	long	ID of the snapshot where the manifest file was added
optional	required	504 added_files_count	int	Number of entries in the manifest that have status ADDED (1), when null this is assumed to be non-zero
optional	required	505 existing_files_count	int	Number of entries in the manifest that have status EXISTING (0), when null this is assumed to be non-zero
optional	required	506 deleted_files_count	int	Number of entries in the manifest that have status DELETED (2), when null this is assumed to be non-zero
optional	required	512 added_rows_count	long	Number of rows in all of files in the manifest that have status ADDED, when null this is assumed to be non-zero
optional	required	513 existing_rows_count	long	Number of rows in all of files in the manifest that have status EXISTING, when null this is assumed to be non-zero
optional	required	514 deleted_rows_count	long	Number of rows in all of files in the manifest that have status DELETED, when null this is assumed to be non-zero
optional	optional	507 partitions	list<508: field_summary> (see below)	A list of field summaries for each partition field in the spec. Each field in the list corresponds to a field in the manifest file’s partition spec.
optional	optional	519 key_metadata	binary
"""

"""
field_summary is a struct with the following fields:

v1	v2	Field id, name	Type	Description
required	required	509 contains_null	boolean	Whether the manifest contains at least one partition with a null value for the field
optional	optional	518 contains_nan	boolean	Whether the manifest contains at least one partition with a NaN value for the field
optional	optional	510 lower_bound	bytes [1]	Lower bound for the non-null, non-NaN values in the partition field, or null if all values are null or NaN [2]
optional	optional	511 upper_bound	bytes [1]	Upper bound for the non-null, non-NaN values in the partition field, or null if all values are null or NaN [2]
"""

"""
The snapshot reference object records all the information of a reference including snapshot ID, reference type and Snapshot Retention Policy.

v1	v2	Field name	Type	Description
required	required	snapshot-id	long	A reference's snapshot ID. The tagged snapshot or latest snapshot of a branch.
required	required	type	string	Type of the reference, tag or branch
optional	optional	min-snapshots-to-keep	int	For branch type only, a positive number for the minimum number of snapshots to keep in a branch while expiring snapshots. Defaults to table property history.expire.min-snapshots-to-keep.
optional	optional	max-snapshot-age-ms	long	For branch type only, a positive number for the max age of snapshots to keep when expiring, including the latest snapshot. Defaults to table property history.expire.max-snapshot-age-ms.
optional	optional	max-ref-age-ms	long	For snapshot references except the main branch, a positive number for the max age of the snapshot reference to keep while expiring snapshots. Defaults to table property history.expire.max-ref-age-ms. The main branch never expires.
"""

"""
Table metadata consists of the following fields:

v1	v2	Field	Description
required	required	format-version	An integer version number for the format. Currently, this can be 1 or 2 based on the spec. Implementations must throw an exception if a table's version is higher than the supported version.
optional	required	table-uuid	A UUID that identifies the table, generated when the table is created. Implementations must throw an exception if a table's UUID does not match the expected UUID after refreshing metadata.
required	required	location	The table's base location. This is used by writers to determine where to store data files, manifest files, and table metadata files.
required	last-sequence-number	The table's highest assigned sequence number, a monotonically increasing long that tracks the order of snapshots in a table.
required	required	last-updated-ms	Timestamp in milliseconds from the unix epoch when the table was last updated. Each table metadata file should update this field just before writing.
required	required	last-column-id	An integer; the highest assigned column ID for the table. This is used to ensure columns are always assigned an unused ID when evolving schemas.
required		schema	The table’s current schema. (Deprecated: use schemas and current-schema-id instead)
optional	required	schemas	A list of schemas, stored as objects with schema-id.
optional	required	current-schema-id	ID of the table's current schema.
required		partition-spec	The table’s current partition spec, stored as only fields. Note that this is used by writers to partition data, but is not used when reading because reads use the specs stored in manifest files. (Deprecated: use partition-specs and default-spec-id instead)
optional	required	partition-specs	A list of partition specs, stored as full partition spec objects.
optional	required	default-spec-id	ID of the "current" spec that writers should use by default.
optional	required	last-partition-id	An integer; the highest assigned partition field ID across all partition specs for the table. This is used to ensure partition fields are always assigned an unused ID when evolving specs.
optional	optional	properties	A string to string map of table properties. This is used to control settings that affect reading and writing and is not intended to be used for arbitrary metadata. For example, commit.retry.num-retries is used to control the number of commit retries.
optional	optional	current-snapshot-id	long ID of the current table snapshot; must be the same as the current ID of the main branch in refs.
optional	optional	snapshots	A list of valid snapshots. Valid snapshots are snapshots for which all data files exist in the file system. A data file must not be deleted from the file system until the last snapshot in which it was listed is garbage collected.
optional	optional	snapshot-log	A list (optional) of timestamp and snapshot ID pairs that encodes changes to the current snapshot for the table. Each time the current-snapshot-id is changed, a new entry should be added with the last-updated-ms and the new current-snapshot-id. When snapshots are expired from the list of valid snapshots, all entries before a snapshot that has expired should be removed.
optional	optional	metadata-log	A list (optional) of timestamp and metadata file location pairs that encodes changes to the previous metadata files for the table. Each time a new metadata file is created, a new entry of the previous metadata file location should be added to the list. Tables can be configured to remove oldest metadata log entries and keep a fixed-size log of the most recent entries after a commit.
optional	required	sort-orders	A list of sort orders, stored as full sort order objects.
optional	required	default-sort-order-id	Default sort order id of the table. Note that this could be used by writers, but is not used when reading because reads use the specs stored in manifest files.
optional	refs	A map of snapshot references. The map keys are the unique snapshot reference names in the table, and the map values are snapshot reference objects. There is always a main branch reference pointing to the current-snapshot-id even if the refs map is null.
optional	optional	statistics	A list (optional) of table statistics.
optional	optional	partition-statistics	A list (optional) of partition statistics.
"""

"""
Statistics files metadata within statistics table metadata field is a struct with the following fields:

v1	v2	Field name	Type	Description
required	required	snapshot-id	string	ID of the Iceberg table's snapshot the statistics file is associated with.
required	required	statistics-path	string	Path of the statistics file. See Puffin file format.
required	required	file-size-in-bytes	long	Size of the statistics file.
required	required	file-footer-size-in-bytes	long	Total size of the statistics file's footer (not the footer payload size). See Puffin file format for footer definition.
optional	optional	key-metadata	Base64-encoded implementation-specific key metadata for encryption.	
required	required	blob-metadata	list<blob metadata> (see below)	A list of the blob metadata for statistics contained in the file with structure described below.
"""

"""
Blob metadata is a struct with the following fields:

v1	v2	Field name	Type	Description
required	required	type	string	Type of the blob. Matches Blob type in the Puffin file.
required	required	snapshot-id	long	ID of the Iceberg table's snapshot the blob was computed from.
required	required	sequence-number	long	Sequence number of the Iceberg table's snapshot the blob was computed from.
required	required	fields	list<integer>	Ordered list of fields, given by field ID, on which the statistic was calculated.
optional	optional	properties	map<string, string>	Additional properties associated with the statistic. Subset of Blob properties in the Puffin file.
"""

"""
partition-statistics field of table metadata is an optional list of structs with the following fields:

v1	v2	Field name	Type	Description
required	required	snapshot-id	long	ID of the Iceberg table's snapshot the partition statistics file is associated with.
required	required	statistics-path	string	Path of the partition statistics file. See Partition statistics file.
required	required	file-size-in-bytes	long	Size of the partition statistics file.
"""

"""
The schema of the partition statistics file is as follows:

v1	v2	Field id, name	Type	Description
required	required	1 partition	struct<..>	Partition data tuple, schema based on the unified partition type considering all specs in a table
required	required	2 spec_id	int	Partition spec id
required	required	3 data_record_count	long	Count of records in data files
required	required	4 data_file_count	int	Count of data files
required	required	5 total_data_file_size_in_bytes	long	Total size of data files in bytes
optional	optional	6 position_delete_record_count	long	Count of records in position delete files
optional	optional	7 position_delete_file_count	int	Count of position delete files
optional	optional	8 equality_delete_record_count	long	Count of records in equality delete files
optional	optional	9 equality_delete_file_count	int	Count of equality delete files
optional	optional	10 total_record_count	long	Accurate count of records in a partition after applying the delete files if any
optional	optional	11 last_updated_at	long	Timestamp in milliseconds from the unix epoch when the partition was last updated
optional	optional	12 last_updated_snapshot_id	long	ID of snapshot that last updated this partition
"""

"""
Position-based delete files store file_position_delete, a struct with the following fields:

Field id, name	Type	Description
2147483546 file_path	string	Full URI of a data file with FS scheme. This must match the file_path of the target data file in a manifest entry
2147483545 pos	long	Ordinal position of a deleted row in the target data file identified by file_path, starting at 0
2147483544 row	required struct<...> [1]	Deleted row values. Omit the column when not storing deleted rows.
"""

"""
avro

Maps with non-string keys must use an array representation with the map logical type. The array representation or Avro’s map type may be used for maps with string keys.

Type	Avro type	Notes
boolean	boolean	
int	int	
long	long	
float	float	
double	double	
decimal(P,S)	{ "type": "fixed",
  "size": minBytesRequired(P),
  "logicalType": "decimal",
  "precision": P,
  "scale": S }	Stored as fixed using the minimum number of bytes for the given precision.
date	{ "type": "int",
  "logicalType": "date" }	Stores days from 1970-01-01.
time	{ "type": "long",
  "logicalType": "time-micros" }	Stores microseconds from midnight.
timestamp	{ "type": "long",
  "logicalType": "timestamp-micros",
  "adjust-to-utc": false }	Stores microseconds from 1970-01-01 00:00:00.000000. [1]
timestamptz	{ "type": "long",
  "logicalType": "timestamp-micros",
  "adjust-to-utc": true }	Stores microseconds from 1970-01-01 00:00:00.000000 UTC. [1]
timestamp_ns	{ "type": "long",
  "logicalType": "timestamp-nanos",
  "adjust-to-utc": false }	Stores nanoseconds from 1970-01-01 00:00:00.000000000. [1], [2]
timestamptz_ns	{ "type": "long",
  "logicalType": "timestamp-nanos",
  "adjust-to-utc": true }	Stores nanoseconds from 1970-01-01 00:00:00.000000000 UTC. [1], [2]
string	string	
uuid	{ "type": "fixed",
  "size": 16,
  "logicalType": "uuid" }	
fixed(L)	{ "type": "fixed",
  "size": L }	
binary	bytes	
struct	record	
list	array	
map	array of key-value records, or map when keys are strings (optional).	Array storage must use logical type name map and must store elements that are 2-field records. The first field is a non-null key and the second field is the value.

Field IDs

Iceberg struct, list, and map types identify nested types by ID. When writing data to Avro files, these IDs must be stored in the Avro schema to support ID-based column pruning.

IDs are stored as JSON integers in the following locations:

ID	Avro schema location	Property	Example
Struct field	Record field object	field-id	{ "type": "record", ...
  "fields": [
    { "name": "l",
      "type": ["null", "long"],
      "default": null,
      "field-id": 8 }
  ] }
List element	Array schema object	element-id	{ "type": "array",
  "items": "int",
  "element-id": 9 }
String map key	Map schema object	key-id	{ "type": "map",
  "values": "int",
  "key-id": 10,
  "value-id": 11 }
String map value	Map schema object	value-id	
Map key, value	Key, value fields in the element record.	field-id	{ "type": "array",
  "logicalType": "map",
  "items": {
    "type": "record",
    "name": "k12_v13",
    "fields": [
      { "name": "key",
        "type": "int",
        "field-id": 12 },
      { "name": "value",
        "type": "string",
        "field-id": 13 }
    ] } }
"""

"""
parquet

Type	Parquet physical type	Logical type	Notes
boolean	boolean		
int	int		
long	long		
float	float		
double	double		
decimal(P,S)	P <= 9: int32,
P <= 18: int64,
fixed otherwise	DECIMAL(P,S)	Fixed must use the minimum number of bytes that can store P.
date	int32	DATE	Stores days from 1970-01-01.
time	int64	TIME_MICROS with adjustToUtc=false	Stores microseconds from midnight.
timestamp	int64	TIMESTAMP_MICROS with adjustToUtc=false	Stores microseconds from 1970-01-01 00:00:00.000000.
timestamptz	int64	TIMESTAMP_MICROS with adjustToUtc=true	Stores microseconds from 1970-01-01 00:00:00.000000 UTC.
timestamp_ns	int64	TIMESTAMP_NANOS with adjustToUtc=false	Stores nanoseconds from 1970-01-01 00:00:00.000000000.
timestamptz_ns	int64	TIMESTAMP_NANOS with adjustToUtc=true	Stores nanoseconds from 1970-01-01 00:00:00.000000000 UTC.
string	binary	UTF8	Encoding must be UTF-8.
uuid	fixed_len_byte_array[16]	UUID	
fixed(L)	fixed_len_byte_array[L]		
binary	binary		
struct	group		
list	3-level list	LIST	See Parquet docs for 3-level representation.
map	3-level map	MAP	See Parquet docs for 3-level representation.
"""

"""
orc

Type	ORC type	ORC type attributes	Notes
boolean	boolean		
int	int		ORC tinyint and smallint would also map to int.
long	long		
float	float		
double	double		
decimal(P,S)	decimal		
date	date		
time	long	iceberg.long-type=TIME	Stores microseconds from midnight.
timestamp	timestamp	iceberg.timestamp-unit=MICROS	Stores microseconds from 2015-01-01 00:00:00.000000. [1], [2]
timestamptz	timestamp_instant	iceberg.timestamp-unit=MICROS	Stores microseconds from 2015-01-01 00:00:00.000000 UTC. [1], [2]
timestamp_ns	timestamp	iceberg.timestamp-unit=NANOS	Stores nanoseconds from 2015-01-01 00:00:00.000000000. [1]
timestamptz_ns	timestamp_instant	iceberg.timestamp-unit=NANOS	Stores nanoseconds from 2015-01-01 00:00:00.000000000 UTC. [1]
string	string		ORC varchar and char would also map to string.
uuid	binary	iceberg.binary-type=UUID	
fixed(L)	binary	iceberg.binary-type=FIXED & iceberg.length=L	The length would not be checked by the ORC reader and should be checked by the adapter.
binary	binary		
struct	struct		
list	array		
map	map	
"""

def _main():
    pass


if __name__ == '__main___':
    _main()
