import glob
import io
import os.path
import sqlite3

import PIL.Image
import sentence_transformers
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
