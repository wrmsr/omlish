"""
vec_distance_l2
vec_distance_l1
vec_distance_hamming
vec_distance_cosine
vec_length
vec_type
vec_to_json
vec_add
vec_sub
vec_slice
vec_normalize
vec_f32
vec_bit
vec_int8
vec_quantize_int8
vec_quantize_binary
"""
import glob
import io
import os.path
import sqlite3
import typing as ta

import sqlite_vec

from omlish import check
from omlish import lang
from ommlx.minichain import vectors


if ta.TYPE_CHECKING:
    import PIL.Image as pil_img  # noqa
    import sentence_transformers as sen_tfm
else:
    pil_img = lang.proxy_import('PIL.Image')
    sen_tfm = lang.proxy_import('sentence_transformers')


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
            f'create virtual table {self._tn} using vec0 (',
            ', ' .join([
                'v integer primary key',
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
            f'select v, distance from {self._tn} where vec match ? order by distance limit {search.k}',
            (sqlite_vec.serialize_float32(search.vec.v),),
        )
        ret = []
        for row in rows:
            ret.append(vectors.Hit(row[1], row[0]))
        return ret


def _main():
    db = sqlite3.connect(':memory:')
    vs = SqliteVecVectorStore(db, 't', 3)
    vs.index(vectors.Indexed(vectors.Vector([1., 2., 3.]), 0))
    vs.index(vectors.Indexed(vectors.Vector([-1., 2., 3.]), 1))
    vs.index(vectors.Indexed(vectors.Vector([-1., -2., 3.]), 2))
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

    model = sen_tfm.SentenceTransformer('clip-ViT-B-32')

    ##

    file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ommlx/tests'))
    file_glob = '*.jpg'

    for fn in glob.glob(os.path.join(file_dir, file_glob)):
        print(fn)

        with open(fn, 'rb') as f:
            img = pil_img.open(io.BytesIO(f.read()))
        print(img)

        [emb] = model.encode([img])  # noqa
        print(emb)


if __name__ == '__main__':
    _main()
