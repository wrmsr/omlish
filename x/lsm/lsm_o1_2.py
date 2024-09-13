import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional


# Define the frozen dataclasses
@dataclass(frozen=True)
class Sequence:
    value: int


@dataclass(frozen=True)
class Record:
    sequence: Sequence
    data: bytes


@dataclass(frozen=True)
class Split:
    size_bytes: int
    num_records: int
    min_sequence: Sequence
    max_sequence: Sequence


@dataclass(frozen=True)
class Segment:
    generation: int
    created_at: str  # ISO format datetime string
    splits: Dict[str, Split]  # Key: split filename, Value: Split object


@dataclass(frozen=True)
class Index:
    segments: Dict[str, Segment]  # Key: segment filename, Value: Segment object


class LSMTree:
    def __init__(self, directory='lsm_data', memtable_threshold=5):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.memtable: List[Record] = []
        self.memtable_threshold = memtable_threshold
        self.sequence_counter = 0
        self.index = self.load_index()
        self.lock = threading.Lock()

    def load_index(self) -> Index:
        index_file = os.path.join(self.directory, 'index.json')
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
                return index_from_dict(index_data)
        else:
            return Index(segments={})

    def save_index(self):
        index_file = os.path.join(self.directory, 'index.json')
        with open(index_file, 'w') as f:
            json.dump(index_to_dict(self.index), f, indent=2)

    def insert(self, data: bytes):
        with self.lock:
            sequence = Sequence(self.sequence_counter)
            self.sequence_counter += 1
            record = Record(sequence, data)
            self.memtable.append(record)
            if len(self.memtable) >= self.memtable_threshold:
                self.flush_memtable()

    def flush_memtable(self):
        generation = int(time.time() * 1000)
        segment_filename = f'segment_{generation}.json'
        segment_path = os.path.join(self.directory, segment_filename)

        # Serialize records to dicts
        records_data = [record_to_dict(record) for record in self.memtable]
        with open(segment_path, 'w') as f:
            json.dump(records_data, f, indent=2)

        # Create segment metadata
        size_bytes = os.path.getsize(segment_path)
        num_records = len(self.memtable)
        min_sequence = self.memtable[0].sequence
        max_sequence = self.memtable[-1].sequence
        split = Split(size_bytes, num_records, min_sequence, max_sequence)
        segment = Segment(
            generation=generation,
            created_at=datetime.now().isoformat(),
            splits={segment_filename: split}
        )

        # Update index
        self.index.segments[segment_filename] = segment
        self.save_index()

        # Clear memtable
        self.memtable = []

    def search(self, sequence_value: int) -> Optional[bytes]:
        # Search memtable first
        with self.lock:
            for record in self.memtable:
                if record.sequence.value == sequence_value:
                    return record.data

        # Search disk segments
        for segment_name, segment in sorted(self.index.segments.items(), reverse=True):
            for split_name, split in segment.splits.items():
                if split.min_sequence.value <= sequence_value <= split.max_sequence.value:
                    segment_path = os.path.join(self.directory, split_name)
                    with open(segment_path, 'r') as f:
                        records_data = json.load(f)
                        for record_data in records_data:
                            record = record_from_dict(record_data)
                            if record.sequence.value == sequence_value:
                                return record.data
        return None

    def compact_segments(self):
        # Simple compaction: merge all segments into one
        all_records = []

        # Read all segments
        for segment_name in list(self.index.segments.keys()):
            segment = self.index.segments.pop(segment_name)
            for split_name in segment.splits.keys():
                segment_path = os.path.join(self.directory, split_name)
                with open(segment_path, 'r') as f:
                    records_data = json.load(f)
                    all_records.extend([record_from_dict(rd) for rd in records_data])
                os.remove(segment_path)  # Remove old segment file

        if not all_records:
            return

        # Sort records by sequence value
        all_records.sort(key=lambda r: r.sequence.value)

        # Write merged segment
        generation = int(time.time() * 1000)
        segment_filename = f'segment_{generation}.json'
        segment_path = os.path.join(self.directory, segment_filename)
        records_data = [record_to_dict(record) for record in all_records]
        with open(segment_path, 'w') as f:
            json.dump(records_data, f, indent=2)

        # Create new segment metadata
        size_bytes = os.path.getsize(segment_path)
        num_records = len(all_records)
        min_sequence = all_records[0].sequence
        max_sequence = all_records[-1].sequence
        split = Split(size_bytes, num_records, min_sequence, max_sequence)
        segment = Segment(
            generation=generation,
            created_at=datetime.now().isoformat(),
            splits={segment_filename: split}
        )

        # Update index
        self.index.segments[segment_filename] = segment
        self.save_index()

    def print_index(self):
        print(json.dumps(index_to_dict(self.index), indent=2))


# Helper functions for serialization and deserialization
def sequence_to_dict(sequence: Sequence) -> Dict:
    return {'value': sequence.value}


def sequence_from_dict(data: Dict) -> Sequence:
    return Sequence(value=data['value'])


def record_to_dict(record: Record) -> Dict:
    return {
        'sequence': sequence_to_dict(record.sequence),
        'data': record.data.decode('utf-8')  # Assuming data is bytes
    }


def record_from_dict(data: Dict) -> Record:
    return Record(
        sequence=sequence_from_dict(data['sequence']),
        data=data['data'].encode('utf-8')
    )


def split_to_dict(split: Split) -> Dict:
    return {
        'size_bytes': split.size_bytes,
        'num_records': split.num_records,
        'min_sequence': sequence_to_dict(split.min_sequence),
        'max_sequence': sequence_to_dict(split.max_sequence)
    }


def split_from_dict(data: Dict) -> Split:
    return Split(
        size_bytes=data['size_bytes'],
        num_records=data['num_records'],
        min_sequence=sequence_from_dict(data['min_sequence']),
        max_sequence=sequence_from_dict(data['max_sequence'])
    )


def segment_to_dict(segment: Segment) -> Dict:
    return {
        'generation': segment.generation,
        'created_at': segment.created_at,
        'splits': {k: split_to_dict(v) for k, v in segment.splits.items()}
    }


def segment_from_dict(data: Dict) -> Segment:
    return Segment(
        generation=data['generation'],
        created_at=data['created_at'],
        splits={k: split_from_dict(v) for k, v in data['splits'].items()}
    )


def index_to_dict(index: Index) -> Dict:
    return {
        'segments': {k: segment_to_dict(v) for k, v in index.segments.items()}
    }


def index_from_dict(data: Dict) -> Index:
    return Index(
        segments={k: segment_from_dict(v) for k, v in data['segments'].items()}
    )


# Example usage
if __name__ == '__main__':
    lsm = LSMTree(memtable_threshold=3)

    # Insert data
    lsm.insert(b'First record')
    lsm.insert(b'Second record')
    lsm.insert(b'Third record')
    lsm.insert(b'Fourth record')
    lsm.insert(b'Fifth record')

    # Search for a record
    result = lsm.search(2)
    if result:
        print(f'Record found: {result.decode("utf-8")}')
    else:
        print('Record not found')

    # Compact segments
    lsm.compact_segments()

    # Print index
    lsm.print_index()
