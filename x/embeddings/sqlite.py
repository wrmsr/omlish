import sqlite3

import sqlite_vec


def _main():
    db = sqlite3.connect(':memory:')
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    vec_version, = db.execute('select vec_version()').fetchone()
    print(f'vec_version={vec_version}')

    #

    from sqlite_vec import serialize_float32

    embedding = [0.1, 0.2, 0.3, 0.4]
    result = db.execute('select vec_length(?)', [serialize_float32(embedding)])

    print(result.fetchone()[0])  # 4


if __name__ == '__main__':
    _main()
