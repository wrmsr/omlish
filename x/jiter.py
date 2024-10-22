"""
https://github.com/pydantic/jiter/tree/main/crates/jiter-python
"""
import jiter


json_data = b'{"name": "John", "age": 30}'
parsed_data = jiter.from_json(json_data)
print(parsed_data)  # Output: {'name': 'John', 'age': 30}

partial_json = b'{"name": "John", "age": 30, "city": "New Yor'

# Raise error on incomplete JSON
try:
    jiter.from_json(partial_json, partial_mode=False)
except ValueError as e:
    print(f"Error: {e}")

# Parse incomplete JSON, discarding incomplete last field
result = jiter.from_json(partial_json, partial_mode=True)
print(result)  # Output: {'name': 'John', 'age': 30}

# Parse incomplete JSON, including incomplete last field
result = jiter.from_json(partial_json, partial_mode='trailing-strings')
print(result)  # Output: {'name': 'John', 'age': 30, 'city': 'New Yor'}

json_with_dupes = b'{"foo": 1, "foo": 2}'

# Default behavior (last value wins)
result = jiter.from_json(json_with_dupes)
print(result)  # Output: {'foo': 2}

# Catch duplicate keys
try:
    jiter.from_json(json_with_dupes, catch_duplicate_keys=True)
except ValueError as e:
    print(f"Error: {e}")
