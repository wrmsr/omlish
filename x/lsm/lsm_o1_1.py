import json
import os
import threading
import time
from datetime import datetime


class Sequence:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {'value': self.value}

    @staticmethod
    def from_dict(data):
        return Sequence(data['value'])


class Record:
    def __init__(self, sequence, data):
        self.sequence = sequence
        self.data = data

    def to_dict(self):
        return {
            'sequence': self.sequence.to_dict(),
            'data': self.data.decode('utf-8')  # Assuming data is bytes
        }

    @staticmethod
    def from_dict(data):
        return Record(
            Sequence.from_dict(data['sequence']),
            data['data'].encode('utf-8')
        )


class Split:
    def __init__(self, size_bytes, num_records, min_sequence, max_sequence):
        self.size_bytes = size_bytes
        self.num_records = num_records
        self.min_sequence = min_sequence
        self.max_sequence = max_sequence

    def to_dict(self):
        return {
            'size_bytes': self.size_bytes,
            'num_records': self.num_records,
            'min_sequence': self.min_sequence.to_dict(),
            'max_sequence': self.max_sequence.to_dict()
        }

    @staticmethod
    def from_dict(data):
        return Split(
            data['size_bytes'],
            data['num_records'],
            Sequence.from_dict(data['min_sequence']),
            Sequence.from_dict(data['max_sequence'])
        )


class Segment:
    def __init__(self, generation, created_at, splits):
        self.generation = generation
        self.created_at = created_at
        self.splits = splits  # Dictionary of Split objects

    def to_dict(self):
        return {
            'generation': self.generation,
            'created_at': self.created_at.isoformat(),
            'splits': {k: v.to_dict() for k, v in self.splits.items()}
        }

    @staticmethod
    def from_dict(data):
        return Segment(
            data['generation'],
            datetime.fromisoformat(data['created_at']),
            {k: Split.from_dict(v) for k, v in data['splits'].items()}
        )


class Index:
    def __init__(self):
        self.segments = {}  # Dictionary of Segment objects

    def to_dict(self):
        return {'segments': {k: v.to_dict() for k, v in self.segments.items()}}

    @staticmethod
    def from_dict(data):
        idx = Index()
        idx.segments = {k: Segment.from_dict(v) for k, v in data['segments'].items()}
        return idx


class LSMTree:
    def __init__(self, directory='.data/lsm_data', memtable_threshold=5):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.memtable = []
        self.memtable_threshold = memtable_threshold
        self.sequence_counter = 0
        self.index = self.load_index()
        self.lock = threading.Lock()

    def load_index(self):
        index_file = os.path.join(self.directory, 'index.json')
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                return Index.from_dict(json.load(f))
        else:
            return Index()

    def save_index(self):
        index_file = os.path.join(self.directory, 'index.json')
        with open(index_file, 'w') as f:
            json.dump(self.index.to_dict(), f, indent=2)

    def insert(self, data):
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

        # Write records to segment file
        records_data = [record.to_dict() for record in self.memtable]
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
            created_at=datetime.now(),
            splits={segment_filename: split}
        )

        # Update index
        self.index.segments[segment_filename] = segment
        self.save_index()

        # Clear memtable
        self.memtable = []

    def search(self, sequence_value):
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
                            record = Record.from_dict(record_data)
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
                    all_records.extend([Record.from_dict(rd) for rd in records_data])
                os.remove(segment_path)  # Remove old segment file

        # Sort records by sequence value
        all_records.sort(key=lambda r: r.sequence.value)

        # Write merged segment
        generation = int(time.time() * 1000)
        segment_filename = f'segment_{generation}.json'
        segment_path = os.path.join(self.directory, segment_filename)
        records_data = [record.to_dict() for record in all_records]
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
            created_at=datetime.now(),
            splits={segment_filename: split}
        )

        # Update index
        self.index.segments[segment_filename] = segment
        self.save_index()

    def print_index(self):
        print(json.dumps(self.index.to_dict(), indent=2))


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
