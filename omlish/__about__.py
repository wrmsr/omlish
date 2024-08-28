__version__ = '0.0.0.dev11'


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

    optional_dependencies = {
        'async': [
            'anyio >= 4.4',
            'sniffio >= 1.3',

            'greenlet >= 3; python_version < "3.13"',

            'trio >= 0.26',
            'trio-asyncio >= 0.15; python_version < "3.13"',
        ],

        'compression': [
            'lz4 >= 4',
            'python-snappy >= 0.7; python_version < "3.13"',
            'zstd >= 1.5',
        ],

        'formats': [
            'orjson > 3.10',
            'cloudpickle >= 3',
            'pyyaml >= 5',
        ],

        'http': [
            'httpx[http2] >= 0.27',
        ],

        'misc': [
            'jinja2 >= 3.1',
            'psutil >= 6',
            'wrapt >= 1.14',
        ],

        'secrets': [
            'cryptography >= 43',
        ],

        'sql': [
            'sqlalchemy >= 2; python_version >= "3.13"',
            'sqlalchemy[asyncio] >= 2; python_version < "3.13"',

            'pg8000 >= 1.31',
            'pymysql >= 1.1',

            'aiomysql >= 0.2',
            'aiosqlite >= 0.20',
            'asyncpg >= 0.29; python_version < "3.13"',
        ],

        'sqlx': [
            'sqlean.py >= 3.45; python_version < "3.13"',

            'duckdb >= 1',
        ],

        'testing': [
            'pytest >= 8',
        ],
    }


#


class SetuptoolsBase:
    manifest_in = [
        'global-exclude **/conftest.py',
    ]

    include_package_data = False

    find_packages = {
        'exclude': ['*.tests', '*.tests.*'],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
