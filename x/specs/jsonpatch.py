"""
See:
 - https://jsonpatch.com/
 - https://datatracker.ietf.org/doc/html/rfc6902/

TODO:
 - https://zuplo.com/blog/2024/10/11/what-is-json-merge-patch
"""
import copy


class JsonPatch:
    def __init__(self, patch_operations):
        self.patch_operations = patch_operations

    def apply_patch(self, doc):
        # Create a deep copy to avoid modifying the original document
        doc_copy = copy.deepcopy(doc)

        for op in self.patch_operations:
            operation = op.get('op')
            path = op.get('path')
            value = op.get('value', None)

            if operation == 'add':
                self.add_operation(doc_copy, path, value)
            elif operation == 'remove':
                self.remove_operation(doc_copy, path)
            elif operation == 'replace':
                self.replace_operation(doc_copy, path, value)
            elif operation == 'move':
                from_path = op.get('from')
                self.move_operation(doc_copy, from_path, path)
            elif operation == 'copy':
                from_path = op.get('from')
                self.copy_operation(doc_copy, from_path, path)
            elif operation == 'test':
                if not self.test_operation(doc_copy, path, value):
                    raise ValueError(f"Test operation failed at path: {path}")
        return doc_copy

    def add_operation(self, doc, path, value):
        keys = path.strip('/').split('/')
        for key in keys[:-1]:
            doc = doc.setdefault(key, {})
        doc[keys[-1]] = value

    def remove_operation(self, doc, path):
        keys = path.strip('/').split('/')
        for key in keys[:-1]:
            doc = doc[key]
        del doc[keys[-1]]

    def replace_operation(self, doc, path, value):
        self.add_operation(doc, path, value)

    def move_operation(self, doc, from_path, path):
        value = self.get_value(doc, from_path)
        self.remove_operation(doc, from_path)
        self.add_operation(doc, path, value)

    def copy_operation(self, doc, from_path, path):
        value = self.get_value(doc, from_path)
        self.add_operation(doc, path, value)

    def test_operation(self, doc, path, value):
        return self.get_value(doc, path) == value

    def get_value(self, doc, path):
        keys = path.strip('/').split('/')
        for key in keys:
            doc = doc[key]
        return doc


##


# Example usage
document = {
    "foo": "bar",
    "baz": {
        "qux": "quux"
    }
}

patch_operations = [
    {"op": "add", "path": "/baz/new_key", "value": "new_value"},
    {"op": "replace", "path": "/foo", "value": "new_bar"},
    {"op": "remove", "path": "/baz/qux"}
]

patch = JsonPatch(patch_operations)
updated_document = patch.apply_patch(document)

print("Updated Document:", updated_document)


##


import pytest

class TestJsonPatch:
    @pytest.fixture
    def initial_document(self):
        return {
            "foo": "bar",
            "baz": {
                "qux": "quux"
            }
        }

    def test_add_operation(self, initial_document):
        patch_operations = [
            {"op": "add", "path": "/baz/new_key", "value": "new_value"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["baz"]["new_key"] == "new_value"
        assert updated_document["foo"] == "bar"

    def test_remove_operation(self, initial_document):
        patch_operations = [
            {"op": "remove", "path": "/baz/qux"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert "qux" not in updated_document["baz"]
        assert updated_document["foo"] == "bar"

    def test_replace_operation(self, initial_document):
        patch_operations = [
            {"op": "replace", "path": "/foo", "value": "new_bar"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["foo"] == "new_bar"
        assert updated_document["baz"]["qux"] == "quux"

    def test_move_operation(self, initial_document):
        patch_operations = [
            {"op": "move", "from": "/baz/qux", "path": "/foo"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["foo"] == "quux"
        assert "qux" not in updated_document["baz"]

    def test_copy_operation(self, initial_document):
        patch_operations = [
            {"op": "copy", "from": "/baz/qux", "path": "/foo_copy"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["foo_copy"] == "quux"
        assert updated_document["baz"]["qux"] == "quux"

    def test_test_operation_success(self, initial_document):
        patch_operations = [
            {"op": "test", "path": "/foo", "value": "bar"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["foo"] == "bar"
        assert updated_document["baz"]["qux"] == "quux"

    def test_test_operation_failure(self, initial_document):
        patch_operations = [
            {"op": "test", "path": "/foo", "value": "not_bar"}
        ]
        patch = JsonPatch(patch_operations)

        with pytest.raises(ValueError):
            patch.apply_patch(initial_document)

    def test_add_nested_operation(self, initial_document):
        patch_operations = [
            {"op": "add", "path": "/baz/deep/nested", "value": "nested_value"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["baz"]["deep"]["nested"] == "nested_value"

    def test_remove_non_existent_key(self, initial_document):
        patch_operations = [
            {"op": "remove", "path": "/baz/non_existent_key"}
        ]
        patch = JsonPatch(patch_operations)

        with pytest.raises(KeyError):
            patch.apply_patch(initial_document)

    def test_move_to_non_existent_key(self, initial_document):
        patch_operations = [
            {"op": "move", "from": "/baz/qux", "path": "/non_existent/new_key"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["non_existent"]["new_key"] == "quux"
        assert "qux" not in updated_document["baz"]

    def test_copy_to_non_existent_key(self, initial_document):
        patch_operations = [
            {"op": "copy", "from": "/baz/qux", "path": "/non_existent/new_key"}
        ]
        patch = JsonPatch(patch_operations)
        updated_document = patch.apply_patch(initial_document)

        assert updated_document["non_existent"]["new_key"] == "quux"
        assert updated_document["baz"]["qux"] == "quux"
