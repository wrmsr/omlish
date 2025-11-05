__version__ = '0.0.0.dev475'
__revision__ = None


#


class ProjectBase:
    name: str | None = None
    authors = [{'name': 'wrmsr'}]
    urls = {'source': 'https://github.com/wrmsr/omlish'}
    license = 'BSD-3-Clause'
    readme = 'README.md'
    requires_python = '>=3.13'

    version = __version__

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
    ]


class Project(ProjectBase):
    name = 'omlish'
    description = 'omlish'

    #

    optional_dependencies = {
        'async': [
            'anyio ~= 4.11',
            'sniffio ~= 1.3',

            'greenlet ~= 3.2',

            'trio ~= 0.32',
            'trio-asyncio ~= 0.15',
        ],

        'compress': [
            'lz4 ~= 4.4',
            # 'lz4 @ git+https://github.com/wrmsr/python-lz4@wrmsr_20240830_GIL_NOT_USED'

            'python-snappy ~= 0.7',

            'zstandard ~= 0.25; python_version < "3.14"',

            'brotli ~= 1.1',
        ],

        'diag': [
            'asttokens ~= 3.0',
            'executing ~= 2.2',

            'psutil ~= 7.1',
        ],

        'formats': [
            'orjson ~= 3.11',
            'ujson ~= 5.11',

            'pyyaml ~= 6.0',

            'cbor2 ~= 5.7',

            'cloudpickle ~= 3.1',
        ],

        'http': [
            'httpx[http2] ~= 0.28',
        ],

        'misc': [
            'wrapt ~= 2.0',
        ],

        'secrets': [
            'cryptography ~= 46.0',
        ],

        'sqlalchemy': [
            'sqlalchemy[asyncio] ~= 2.0',
        ],

        'sqldrivers': [
            'pg8000 ~= 1.31',
            # 'psycopg2 ~= 2.9',
            # 'psycopg ~= 3.2',

            'pymysql ~= 1.1',
            # 'mysql-connector-python ~= 9.5',
            # 'mysqlclient ~= 2.2',

            'aiomysql ~= 0.3',
            'aiosqlite ~= 0.21',
            'asyncpg ~= 0.30',

            'apsw ~= 3.51',

            'sqlean.py ~= 3.50',

            'duckdb ~= 1.4',
        ],

        'templates': [
            'markupsafe ~= 3.0',

            'jinja2 ~= 3.1',
        ],

        'testing': [
            'pytest ~= 8.4',
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
            '*.hh',

            '.omlish-manifests.json',

            'LICENSE',
            'LICENSE.txt',
        ],
    }


class Setuptools(SetuptoolsBase):
    cext = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
