__version__ = '0.0.0.dev242'
__revision__ = None


#


class ProjectBase:
    name: str | None = None
    authors = [{'name': 'wrmsr'}]
    urls = {'source': 'https://github.com/wrmsr/omlish'}
    license = {'text': 'BSD-3-Clause'}
    requires_python = '>=3.12'

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

    #

    optional_dependencies = {
        'async': [
            'anyio ~= 4.8',
            'sniffio ~= 1.3',

            'greenlet ~= 3.1',

            'trio ~= 0.29',
            'trio-asyncio ~= 0.15',
        ],

        'compress': [
            'lz4 ~= 4.4',
            # 'lz4 @ git+https://github.com/wrmsr/python-lz4@wrmsr_20240830_GIL_NOT_USED'

            'python-snappy ~= 0.7',

            'zstandard ~= 0.23',

            'brotli ~= 1.1',
        ],

        'diag': [
            'asttokens ~= 3.0',
            'executing ~= 2.2',

            'psutil ~= 7.0',
        ],

        'formats': [
            'orjson ~= 3.10',
            'ujson ~= 5.10',

            'pyyaml ~= 6.0',

            'cbor2 ~= 5.6',

            'cloudpickle ~= 3.1',
        ],

        'http': [
            'httpx[http2] ~= 0.28',
        ],

        'misc': [
            'wrapt ~= 1.17',
        ],

        'secrets': [
            'cryptography ~= 44.0',
        ],

        'sqlalchemy': [
            'sqlalchemy[asyncio] ~= 2.0',
        ],

        'sqldrivers': [
            'pg8000 ~= 1.31',
            # 'psycopg2 ~= 2.9',
            # 'psycopg ~= 3.2',

            'pymysql ~= 1.1',
            # 'mysql-connector-python ~= 9.1',
            # 'mysqlclient ~= 2.2',

            'aiomysql ~= 0.2',
            'aiosqlite ~= 0.21',
            'asyncpg ~= 0.30',

            'apsw ~= 3.47',

            'sqlean.py ~= 3.45',

            'duckdb ~= 1.2',
        ],

        'testing': [
            'pytest ~= 8.0',
        ],
    }

    #

    _plus_dependencies = [
        'anyio',
        'sniffio',

        'asttokens',
        'executing',

        'orjson',
        'pyyaml',

        'wrapt',
    ]

    _dependency_specs_by_name = (lambda od: {  # noqa
        s.split()[0]: s
        for l in od.values() for s in l
    })(optional_dependencies)

    optional_dependencies['plus'] = (lambda ds, pd: [  # noqa
        ds[n] for n in pd
    ])(_dependency_specs_by_name, _plus_dependencies)

    #

    entry_points = {
        'omlish.manifests': {name: name},
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
            '*.g4',
            '*.h',

            '.manifests.json',

            'LICENSE',
            'LICENSE.txt',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
