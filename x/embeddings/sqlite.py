import glob
import io
import os.path
import sqlite3

import PIL.Image
import sentence_transformers
import sqlite_vec

from omlish import check
from ommlx.minichain import vectors


class SqliteVecVectorStore(vectors.VectorStore):
    def __init__(
            self,
            db: sqlite3.Connection,
            tn: str,
            d: int,
    ) -> None:
        super().__init__()

        self._db = db
        self._tn = tn
        self._d = d

        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)

        db.execute(''.join([
            f'create table {self._tn} (',
            ', ' .join([
                'id integer primary key autoincrement',
                'v string',
                f'vec float[{d}]',
            ]),
            ')',
        ]))

    def index(self, doc: vectors.Indexed) -> None:
        self._db.execute(
            f'insert into {self._tn} (v, vec) values (?, ?)',
            (doc.v, sqlite_vec.serialize_float32(doc.vec.v)),
        )

    def search(self, search: vectors.Search) -> vectors.Hits:
        rows = self._db.execute(
            f'with t as (select v, vec_distance_cosine(?, vec) as distance from {self._tn}) '
            f'select v, distance from t order by distance limit {search.k}',
            (sqlite_vec.serialize_float32(search.vec.v),),
        )
        raise NotImplementedError


def _main():
    db = sqlite3.connect(':memory:')
    vs = SqliteVecVectorStore(db, 't', 3)
    vs.index(vectors.Indexed(vectors.Vector([1., 2., 3.]), 'foo'))
    vs.index(vectors.Indexed(vectors.Vector([-1., 2., 3.]), 'bar'))
    vs.index(vectors.Indexed(vectors.Vector([-1., -2., 3.]), 'baz'))
    hits = vs.search(vectors.Search(vectors.Vector([0., 2., 1.])))
    print(hits)

    ##

    db = sqlite3.connect(':memory:')
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    vec_version, = db.execute('select vec_version()').fetchone()
    print(f'vec_version={vec_version}')

    #

    embedding = [0.1, 0.2, 0.3, 0.4]
    result = db.execute('select vec_length(?)', [sqlite_vec.serialize_float32(embedding)])

    print(result.fetchone()[0])  # 4

    ##

    model = sentence_transformers.SentenceTransformer('clip-ViT-B-32')

    ##

    file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ommlx/tests'))
    file_glob = '*.jpg'

    for fn in glob.glob(os.path.join(file_dir, file_glob)):
        print(fn)

        with open(fn, 'rb') as f:
            img = PIL.Image.open(io.BytesIO(f.read()))
        print(img)

        [emb] = model.encode([img])  # noqa
        print(emb)


if __name__ == '__main__':
    _main()
