__version__ = '0.0.31'
__revision__ = None


#


class ProjectBase:
    name: str | None = None
    authors = [{'name': 'wrmsr'}]
    urls = {'source': 'https://github.com/wrmsr/om'}
    license = 'BSD-3-Clause'
    readme = 'README.md'
    requires_python = '>=3.14'

    version = __version__

    classifiers = [
        'Intended Audience :: Developers',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.14',
    ]


class Project(ProjectBase):
    name = 'omcore'
    description = 'omcore'

    #

    optional_dependencies = {
        'async': [
            'anyio ~= 4.14',
            'sniffio ~= 1.3',

            'trio ~= 0.33',
            'trio-asyncio ~= 0.15',
        ],

        'compress': [
            'lz4 ~= 4.4',

            'python-snappy ~= 0.7',

            'brotli ~= 1.2',
        ],

        'diag': [
            'asttokens ~= 3.0',
            'executing ~= 2.2',

            'psutil ~= 7.2',

            'memray ~= 1.19',
        ],

        'formats': [
            'orjson ~= 3.11',
            'ujson ~= 5.13',

            'pyyaml ~= 6.0',

            'cbor2 ~= 6.1',

            'cloudpickle ~= 3.1',
        ],

        'http': [
            'httpx[http2] ~= 0.28',
        ],

        'secrets': [
            'cryptography ~= 49.0',
        ],

        'sqlalchemy': [
            'sqlalchemy[asyncio] ~= 2.0',
        ],

        'sqldrivers': [
            'pg8000 ~= 1.31',
            'psycopg2 ~= 2.9',
            'psycopg ~= 3.3',

            'pymysql ~= 1.2',
            'mysql-connector-python ~= 9.7',
            'mysqlclient ~= 2.2',

            'snowflake-connector-python ~= 4.7',

            'aiomysql ~= 0.3',
            'aiosqlite ~= 0.22',
            'asyncpg ~= 0.31',

            'apsw ~= 3.53',

            'sqlean.py ~= 3.50',

            'duckdb ~= 1.5',
        ],

        'templates': [
            'markupsafe ~= 3.0',

            'jinja2 ~= 3.1',
        ],

        'testing': [
            'pytest ~= 9.1',
        ],
    }

    #

    _plus_dependencies = [
        'asttokens',
        'executing',

        'orjson',
        'pyyaml',
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
        'omcore.manifests': {name: name},
    }


#


class SetuptoolsBase:
    cext = False
    mypyc = False
    rs = False

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
            '*.hh',

            '*.abnf',
            '*.g4',

            '.om-manifests.json',

            'py.typed',

            '*.md',

            'README',
            'README.rst',

            'LICENSE',
            'LICENSE.txt',

            'AUTHORS',
        ],
    }


class Setuptools(SetuptoolsBase):
    cext = True
    mypyc = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
