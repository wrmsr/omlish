"""
https://iceberg.apache.org/spec/ <-- winner

https://github.com/delta-io/delta/blob/master/PROTOCOL.md
https://hudi.apache.org/tech-specshttps://hudi.apache.org/tech-specs/

https://yousry.medium.com/delta-lake-z-ordering-from-a-to-z-315063a42031

https://iorilan.medium.com/how-does-the-lsm-tree-work-7a9fa4b54c36
https://lucene.apache.org/core/3_0_3/fileformats.html#Segments%20File

==

syntax = "proto3";

package kleist;

import "google/protobuf/timestamp.proto";

message Index {
  map<string, Segment> segments = 1;
}

message Sequence {
  uint64 value = 1;
}

message Segment {
  uint64 generation = 1;
  google.protobuf.Timestamp created_at = 2;
  map<string, Split> splits = 3;
}

message Split {
  uint64 size_bytes = 1;
  uint64 num_records = 2;
  Sequence min_sequence = 3;
  Sequence max_sequence = 4;
}

message Record {
  Sequence sequence = 1;
  bytes data = 2;
}

Framing, LineFraming, BlockIterator

-

heavy on forking
 - fork to merge, serial output anyway
really shoot for arrow, s3, parquet
direct kinesis reading? json in kinesis?
 - kinesis transformers in lambdas?
fuckin kpl/kcl
 - do i really care
fucking dynamo
scanners, rebuilds


production:
 - db tailing

processing:
 - lambda
 - multiprocessing
 - serial

intermediate storage:
 - kv abstr

transport:
 - sqs
 - kinesis
 - multiprocessing
 - direct http
 - zmq

consumption:
 - raw kinesis / s3
 - http long-poll
 - push into db


resurrect zmq workers
avro w/o schema?
multitenant?

https://github.com/mhart/kinesalite
https://github.com/tebeka/fastavro/tree/master/fastavro
https://github.com/jminer/rust-avro

https://github.com/weld-project/weld/blob/master/weld/ast.rs
 - https://dawn.cs.stanford.edu/2017/04/25/weld/


https://github.com/postgres/postgres/blob/master/src/backend/replication/logical/reorderbuffer.c


merkle scanners?


wait_for_replication :| heartbest everywhere


run in docker-compose, api backplane, real services

flink has come a long way - matviews
"""

"""
- Framing, LineFraming, BlockIterator
- heavy on forking
 - fork to merge, serial output anyway
- db tailing
- raw kinesis / s3, - http long-poll, push into db, redis
- scanners, rebuilds
- avro w/o schema?
- multitenant?
- merkle scanners?
- wait_for_replication :| heartbeat everywhere
- run in docker-compose, api backplane, real services

https://github.com/uber/hudi/tree/master/hoodie-common/src/main/java/com/uber/hoodie/common/table/log
https://eng.uber.com/hoodie/
https://avro.apache.org/docs/1.8.0/spec.html#Schema+Resolution
"""
import datetime
import itertools
import typing as ta

from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class Index:
    segments: ta.Sequence['Segment']


Id = ta.NewType('Id', int)


@dc.dataclass(frozen=True)
class Segment:
    generation: int
    created_at: datetime.datetime
    splits: ta.Mapping[str, 'Split']


@dc.dataclass(frozen=True)
class Split:
    size_bytes: int
    num_records: int
    min_id: Id
    max_id: Id


@dc.dataclass(frozen=True)
class Record:
    id: Id
    data: bytes


def main():
    import tempfile
    import json

    def write_segment(gen: int, recs: ta.Iterable[Record], max_split: int = 25) -> Segment:
        recs = sorted(recs, key=lambda r: r.id)
        splits = {}
        for chunk in itertools.batched(recs, max_split):
            path = tempfile.mktemp()
            with open(path, 'w') as f:
                for rec in chunk:
                    f.write(json.dumps(rec._asdict()))
                    f.write('\n')
                sz = f.tell()
            splits[path] = Split(sz, len(chunk), chunk[0].id, chunk[-1].id)
        return Segment(
            gen,
            datetime.datetime.now(),
            splits,
        )

    idx = Index([
        write_segment(0, [Record(i, bytes([i])) for i in range(0, 100, 2)]),
        write_segment(0, [Record(i, bytes([i])) for i in range(1, 100, 2)]),
    ])

    print(idx)


if __name__ == '__main__':
    main()
