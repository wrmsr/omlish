__version__ = '0.0.0.dev30'
__revision__ = None


#


class ProjectBase:
    name: str | None = None
    authors = [{'name': 'wrmsr'}]
    urls = {'source': 'https://github.com/wrmsr/omlish'}
    license = {'text': 'BSD-3-Clause'}
    requires_python = '~=3.12'

    version = __version__

    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
    ]


class Project(ProjectBase):
    name = 'omlish'
    description = 'omlish'

    optional_dependencies = {
        'async': [
            'anyio ~= 4.5',
            'sniffio ~= 1.3',

            'greenlet ~= 3.1',

            'trio ~= 0.26',
            'trio-asyncio ~= 0.15',
        ],

        'compress': [
            'lz4 ~= 4.0',

            'python-snappy ~= 0.7; python_version < "3.13"',

            'zstd ~= 1.5',
        ],

        'diag': [
            'asttokens ~= 2.4',
            'executing ~= 2.1',

            'psutil ~= 6.0',
        ],

        'formats': [
            'orjson ~= 3.10',
            'ujson ~= 5.10',

            'json5 ~= 0.9',

            'pyyaml ~= 5.0',

            'cloudpickle ~= 3.0',
        ],

        'http': [
            'httpx[http2] ~= 0.27',
        ],

        'misc': [
            'wrapt ~= 1.14',
        ],

        'secrets': [
            'cryptography ~= 43.0',
        ],

        'sql': [
            'sqlalchemy[asyncio] ~= 2.0',
        ],

        'sql-drivers': [
            'pg8000 ~= 1.31',
            # 'psycopg2 ~= 2.9',
            # 'psycopg ~= 3.2',

            'pymysql ~= 1.1',
            # 'mysql-connector-python ~= 9.0',
            # 'mysqlclient ~= 2.2',

            'aiomysql ~= 0.2',
            'aiosqlite ~= 0.20',
            'asyncpg ~= 0.29; python_version < "3.13"',

            'sqlean.py ~= 3.45; python_version < "3.13"',

            'duckdb ~= 1.1',
        ],

        'testing': [
            'pytest ~= 8.0',
        ],
    }


#


class SetuptoolsBase:
    manifest_in = [
        'global-exclude **/conftest.py',
    ]

    find_packages = {
        'exclude': [
            '*.tests',
            '*.tests.*',
        ],
    }

    package_data = {
        '*': [
            '*.c',
            '*.cc',
            '*.cu',
            '*.h',

            '.manifests.json',

            'LICENSE',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
