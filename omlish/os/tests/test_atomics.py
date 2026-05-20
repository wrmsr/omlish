import os
import tempfile
import unittest

from ..atomics import TempDirAtomicPathSwapping


class TestAtomics(unittest.TestCase):
    def test_abort_file_removes_temp_file(self):
        with tempfile.TemporaryDirectory() as td:
            dst_path = os.path.join(td, 'dst')
            swap = TempDirAtomicPathSwapping(temp_dir=td).begin_atomic_path_swap('file', dst_path)
            tmp_path = swap.tmp_path

            self.assertTrue(os.path.isfile(tmp_path))

            swap.abort()

            self.assertFalse(os.path.exists(tmp_path))
            self.assertFalse(os.path.exists(dst_path))

    def test_abort_file_removes_temp_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            dst_path = os.path.join(td, 'dst')
            target_path = os.path.join(td, 'target')
            swap = TempDirAtomicPathSwapping(temp_dir=td).begin_atomic_path_swap('file', dst_path)
            tmp_path = swap.tmp_path

            os.unlink(tmp_path)
            os.symlink(target_path, tmp_path)

            swap.abort()

            self.assertFalse(os.path.lexists(tmp_path))
            self.assertFalse(os.path.exists(dst_path))

    def test_context_manager_keeps_manually_committed_state(self):
        with tempfile.TemporaryDirectory() as td:
            dst_path = os.path.join(td, 'dst')
            with TempDirAtomicPathSwapping(temp_dir=td).begin_atomic_path_swap('file', dst_path) as swap:
                tmp_path = swap.tmp_path
                with open(tmp_path, 'w') as f:
                    f.write('payload')
                swap.commit()

            self.assertEqual(swap.state, 'committed')
            self.assertFalse(os.path.exists(tmp_path))
            with open(dst_path) as f:
                self.assertEqual(f.read(), 'payload')

    def test_abort_committed_raises_and_keeps_state(self):
        with tempfile.TemporaryDirectory() as td:
            dst_path = os.path.join(td, 'dst')
            swap = TempDirAtomicPathSwapping(temp_dir=td).begin_atomic_path_swap('file', dst_path)
            tmp_path = swap.tmp_path
            with open(tmp_path, 'w') as f:
                f.write('payload')

            swap.commit()

            with self.assertRaises(RuntimeError):
                swap.abort()

            self.assertEqual(swap.state, 'committed')
            with open(dst_path) as f:
                self.assertEqual(f.read(), 'payload')

    def test_root_dir_check_rejects_sibling_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            root_dir = os.path.join(td, 'root')
            sibling_dir = os.path.join(td, 'root-sibling')
            os.mkdir(root_dir)
            os.mkdir(sibling_dir)

            swapping = TempDirAtomicPathSwapping(temp_dir=root_dir, root_dir=root_dir)

            with self.assertRaises(RuntimeError):
                swapping.begin_atomic_path_swap('file', os.path.join(sibling_dir, 'dst'))

    def test_root_dir_check_allows_child(self):
        with tempfile.TemporaryDirectory() as td:
            root_dir = os.path.join(td, 'root')
            child_dir = os.path.join(root_dir, 'child')
            os.makedirs(child_dir)

            swap = TempDirAtomicPathSwapping(temp_dir=root_dir, root_dir=root_dir).begin_atomic_path_swap(
                'file',
                os.path.join(child_dir, 'dst'),
            )

            swap.abort()

    def test_write_file_helper(self):
        with tempfile.TemporaryDirectory() as td:
            dst_path = os.path.join(td, 'dst')
            with open(dst_path, 'w') as f:
                f.write('foo')

            swap = TempDirAtomicPathSwapping(
                temp_dir=td,
            ).write_file(
                dst_path,
                'bar',
            )

            self.assertEqual(swap.state, 'committed')
            self.assertFalse(os.path.exists(swap.tmp_path))
            with open(dst_path) as f:
                self.assertEqual(f.read(), 'bar')


if __name__ == '__main__':
    unittest.main()
