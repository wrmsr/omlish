import abc
import glob
import json
import logging
import os
import shutil
import zipfile

import pkg_resources

from .. import lang


lang.warn_unstable()


log = logging.getLogger(__name__)


PURGED_LIB_ITEMS = {

    'Crypto': ['SelfTest'],
    'ctypes': ['test'],
    'cytoolz': ['tests'],
    'distutils': ['tests'],
    'google.protobuf': ['**/*_test.py', '**/*unittest*.py'],
    'idlelib': ['**'],
    'lib2to3': ['tests'],
    'networkx': ['**/*/tests'],
    'numpy': ['**/tests'],
    'psutil': ['**/tests'],
    'psycopg2': ['**/tests'],
    'pyarrow': ['tests'],
    'sqlite3': ['test'],
    'test': ['**'],
    'tkinter': ['tests'],
    'toolz': ['tests'],
    'turtledemo': ['**'],
    'unittest': ['**'],

}


def purge_libs():
    abscwd = os.path.abspath(os.getcwd()) + os.sep
    for lib, items in PURGED_LIB_ITEMS.items():
        try:
            module = __import__(lib)
        except ImportError:
            continue
        for submodule in lib.split('.')[1:]:
            module = getattr(module, submodule)

        mpath = getattr(module, '__file__', None)
        if mpath is not None:
            path = os.path.dirname(mpath)
            for item in items:
                for target in glob.glob(os.path.join(path, item), recursive=True):
                    target = os.path.abspath(target)
                    if not target.startswith(abscwd):
                        # FIXME: option to force
                        raise ValueError(target)
                    if os.path.isdir(target):
                        log.info(f'Removing tree {target}')
                        shutil.rmtree(target)
                    else:
                        log.info(f'Removing file {target}')
                        os.unlink(target)


class BotoJsonPackedFileLoader(abc.ABC):

    PACKED_FILE_NAME = None

    @staticmethod
    def purge():
        boto_path = pkg_resources.resource_filename('botocore', '/')
        if not os.path.isdir(boto_path):
            raise OSError
        data_path = os.path.abspath(os.path.join(boto_path, 'data'))
        abscwd = os.path.abspath(os.getcwd()) + os.sep
        if not os.path.isdir(data_path) or not data_path.startswith(abscwd):
            raise ValueError(data_path)
        shutil.rmtree(data_path)

    @classmethod
    def install(cls):
        import botocore.loaders
        if not hasattr(botocore.loaders.Loader, 'FILE_LOADER_CLASS'):
            raise AttributeError
        botocore.loaders.Loader.FILE_LOADER_CLASS = cls

    @classmethod
    def maybe_install(cls):
        if os.path.exists(cls.get_packed_file_path()):
            cls.install()

    @classmethod
    def get_packed_file_path(cls):
        return os.path.join(pkg_resources.resource_filename('botocore', cls.PACKED_FILE_NAME))

    @classmethod
    def get_packed_member_name(cls, file_path):
        base_path = pkg_resources.resource_filename('botocore', '/')
        if not file_path.startswith(base_path):
            return None

        return file_path[len(base_path):] + '.json'

    def __init__(self):
        super().__init__()

        import botocore.loaders
        self._json_loader = botocore.loaders.JSONFileLoader()

    def exists(self, file_path):
        member_name = self.get_packed_member_name(file_path)
        if member_name is None:
            return self._json_loader.exists(file_path)
        else:
            return self.packed_member_exists(member_name)

    @abc.abstractmethod
    def packed_member_exists(self, member_name):
        raise NotImplementedError

    def load_file(self, file_path):
        member_name = self.get_packed_member_name(file_path)
        if member_name is None:
            return self._json_loader.load_file(file_path)

        from botocore.compat import OrderedDict
        try:
            payload = self.load_packed_member(member_name)
        except KeyError:
            from botocore.exceptions import DataNotFoundError
            raise DataNotFoundError(data_path=file_path)
        return json.loads(payload, object_pairs_hook=OrderedDict)

    @abc.abstractmethod
    def load_packed_member(self, member_name):
        raise NotImplementedError


class BotoJsonZipFileLoader(BotoJsonPackedFileLoader):

    PACKED_FILE_NAME = 'data.zip'

    @staticmethod
    def build():
        boto_path = pkg_resources.resource_filename('botocore', '/')
        if not os.path.isdir(boto_path):
            raise OSError
        data_path = os.path.join(boto_path, 'data')
        if not os.path.isdir(data_path):
            raise ValueError(data_path)
        abscwd = os.path.abspath(os.getcwd()) + os.sep
        if not data_path.startswith(abscwd):
            # FIXME: option to force
            raise ValueError(data_path)
        shutil.make_archive(data_path, 'zip', boto_path, 'data')
        shutil.rmtree(data_path)

    def packed_member_exists(self, member_name):
        with zipfile.ZipFile(self.get_packed_file_path()) as zf:
            try:
                zf.getinfo(member_name)
            except KeyError:
                return False
            else:
                return True

    def load_packed_member(self, member_name):
        with zipfile.ZipFile(self.get_packed_file_path()) as zf:
            return zf.read(member_name).decode('utf-8')


PACKED_FILE_LOADER_CLASS = BotoJsonZipFileLoader


def pack_boto():
    PACKED_FILE_LOADER_CLASS.build()


def purge_boto():
    PACKED_FILE_LOADER_CLASS.purge()


def test_boto():
    PACKED_FILE_LOADER_CLASS.install()

    import boto3
    pricing = boto3.client('pricing')

    from botocore.exceptions import ClientError
    try:
        pricing.describe_services(ServiceCode='AmazonEC2')
    except ClientError:
        pass
