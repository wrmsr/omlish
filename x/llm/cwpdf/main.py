"""
TODO:
 - ccache
"""
import contextlib
import contextvars
import dataclasses as dc
import logging
import os.path
import sys
import typing as ta
import uuid

from omlish import check
from omlish import lang
from omlish import logs
from omlish import term

from .caching import pkl_cache
from .chromadb import chroma_collection
from .chromadb import get_relevant_docs
from .docs import Doc
from .models.chat import generate_question_answer
from .models.decision import classify_user_intent
from .models.embedding import embed
from .models.embedding import embedding_model
from .output import print_and_join
from .pdfs import build_pdf_docs
from .splitting import RecursiveTextSplitter
from .vars import data_dir
from .vars import exit_stack


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


pdf_file: contextvars.ContextVar[str] = contextvars.ContextVar('pdf_file')


##


@pkl_cache(lambda: os.path.join(data_dir.get(), os.path.basename(pdf_file.get()) + '.docs.pkl'))
def docs() -> list[Doc]:
    log.info('Building docs')
    ret = build_pdf_docs(pdf_file.get())
    log.info('%d docs built', len(ret))
    return ret


@pkl_cache(lambda: os.path.join(data_dir.get(), os.path.basename(pdf_file.get()) + '.splits.pkl'))
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


@pkl_cache(lambda: os.path.join(data_dir.get(), os.path.basename(pdf_file.get()) + '.embeddings.pkl'))
def embeddings() -> list[list[float]]:
    lst = splits()
    embedding_model()

    log.info('Building embeddings')
    ret = []
    for split in term.progress_bar(lst, out=sys.stderr):
        ret.append(embed(split.content, 'embed'))
    log.info('%d embeddings built', len(ret))
    return ret


##


@pkl_cache(lambda: os.path.join(data_dir.get(), os.path.basename(pdf_file.get() + '.chroma-upserts.pkl')))
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


def _main() -> None:
    # pf = os.path.expanduser('~/Downloads/nke-10k-2023.pdf')
    pf = os.path.expanduser('~/Downloads/NVIDIAAn.pdf')

    exit_stack.get().enter_context(lang.context_var_setting(pdf_file, pf))  # noqa

    logs.configure_standard_logging('INFO')

    if not os.path.exists(dd := data_dir.get()):
        os.makedirs(dd)

    ##

    num_upserts = chroma_upserts()
    log.info('%d embeddings upserted to chroma', num_upserts)

    ##

    query = (
        "<pdf> Please provide NVIDIA's Q2 Fiscal 2025 financial metrics for:\n"
        '1. Total quarterly revenue\n'
        '2. Data Center segment revenue'
    )

    print(classify_user_intent(query))

    relevant_docs = get_relevant_docs(query)
    response_chunks = generate_question_answer(query, [d.doc for d in relevant_docs])
    response = print_and_join(response_chunks)  # noqa

    ##

    query = 'Generate a pie chart of that data.'
    print(classify_user_intent(query))


def main() -> None:
    with contextlib.ExitStack() as es:
        es.enter_context(lang.context_var_setting(exit_stack, es))  # noqa
        es.enter_context(lang.context_var_setting(data_dir, os.path.join(os.path.dirname(__file__), 'data')))  # noqa
        _main()


if __name__ == '__main__':
    main()
