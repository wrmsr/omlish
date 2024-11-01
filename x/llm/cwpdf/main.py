"""
TODO:
 - ccache
"""
import contextlib
import dataclasses as dc
import functools
import logging
import os.path
import pickle
import typing as ta
import uuid

from omlish import check
from omlish import lang
from omlish import logs
from omlish import term

from .chromadb import chroma_collection
from .chromadb import get_relevant_docs
from .docs import Doc
from .models.chat import generate_question_answer
from .models.embedding import embed
from .output import print_and_join
from .pdfs import build_pdf_docs
from .splitting import RecursiveTextSplitter
from .vars import data_dir
from .vars import exit_stack


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


##


def _pkl_cache(pkl_file: str) -> ta.Callable[[ta.Callable[[], T]], ta.Callable[[], T]]:
    def outer(fn):
        @functools.wraps(fn)
        def inner():
            if not os.path.exists(pkl_file):
                v = fn()
                with open(pkl_file, 'wb') as f:
                    pickle.dump(v, f)
                return v
            else:
                with open(pkl_file, 'rb') as f:
                    return pickle.load(f)  # noqa
        return inner
    return outer


def _main() -> None:
    pdf_file = os.path.expanduser('~/Downloads/nke-10k-2023.pdf')

    logs.configure_standard_logging('INFO')

    ##

    @_pkl_cache(os.path.join(data_dir.get(), os.path.basename(pdf_file) + '.docs.pkl'))
    def docs() -> list[Doc]:
        log.info('Building docs')
        ret = build_pdf_docs(pdf_file)
        log.info('%d docs built', len(ret))
        return ret

    @_pkl_cache(os.path.join(data_dir.get(), os.path.basename(pdf_file) + '.splits.pkl'))
    def splits() -> list[Doc]:
        log.info('Building splits')
        ret = [
            dc.replace(
                split,
                id=str(uuid.uuid4()),
            )
            for split in RecursiveTextSplitter().split_docs(docs())
        ]
        log.info('%d splits built', len(ret))
        return ret

    ##

    @_pkl_cache(os.path.join(data_dir.get(), os.path.basename(pdf_file) + '.embeddings.pkl'))
    def embeddings() -> list[list[float]]:
        log.info('Building embeddings')
        ret = []
        for split in term.progress_bar(splits()):
            ret.append(embed(split.content, 'embed'))
        log.info('%d embeddings built', len(ret))
        return ret

    ##

    @_pkl_cache(os.path.join(data_dir.get(), os.path.basename(pdf_file) + '.chroma-upserts.pkl'))
    def chroma_upserts() -> int:
        lst = splits()
        chroma_collection().upsert(
            ids=[check.not_none(d.id) for d in lst],
            embeddings=embeddings(),
            documents=[d.content for d in lst],
            metadatas=[check.not_none(d.metadata) for d in lst],
        )
        return len(lst)

    ##

    num_upserts = chroma_upserts()
    log.info('%d embeddings upserted to chroma', num_upserts)

    ##

    query = 'What is this pdf about?'
    relevant_docs = get_relevant_docs(query)
    response_chunks = generate_question_answer(query, [d.doc for d in relevant_docs])
    response = print_and_join(response_chunks)  # noqa


def main() -> None:
    with contextlib.ExitStack() as es:
        es.enter_context(lang.context_var_setting(exit_stack, es))  # noqa
        es.enter_context(lang.context_var_setting(data_dir, os.path.join(os.path.dirname(__file__), 'data')))  # noqa
        _main()


if __name__ == '__main__':
    _main()
