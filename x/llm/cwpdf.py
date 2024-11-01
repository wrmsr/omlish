"""
TODO:
 - ccache
"""
# MIT License
#
# Copyright (c) LangChain, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import abc
import contextlib
import dataclasses as dc
import functools
import os.path
import pickle
import re
import shutil
import typing as ta
import uuid

from omlish import check
from omlish import lang
from omlish import term


if ta.TYPE_CHECKING:
    import chromadb
    import llama_cpp
    import numpy as np
    import pypdf

else:
    chromadb = lang.proxy_import('chromadb')
    llama_cpp = lang.proxy_import('llama_cpp')
    np = lang.proxy_import('numpy')
    pypdf = lang.proxy_import('pypdf')


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Doc:
    content: str
    metadata: ta.Mapping[str, ta.Any] | None = None
    id: str | None = None


##


def extract_text_from_page(page: 'pypdf.PageObject') -> str:
    return page.extract_text(
        extraction_mode='plain',
    )


##


PDF_FILTER_WITH_LOSS = {
    'DCTDecode',
    'DCT',
    'JPXDecode',
}

PDF_FILTER_WITHOUT_LOSS = {
    'LZWDecode',
    'LZW',
    'FlateDecode',
    'Fl',
    'ASCII85Decode',
    'A85',
    'ASCIIHexDecode',
    'AHx',
    'RunLengthDecode',
    'RL',
    'CCITTFaxDecode',
    'CCF',
    'JBIG2Decode',
}


def extract_from_images_with_rapidocr(
        images: ta.Sequence[ta.Iterable['np.ndarray'] | bytes],
) -> str:
    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()
    text = ''
    for img in images:
        result, _ = ocr(img)
        if result:
            result = [text[1] for text in result]
            text += '\n'.join(result)

    return text


def extract_images_from_page(page: 'pypdf.PageObject') -> str:
    if '/XObject' not in page['/Resources'].keys():  # type: ignore  # noqa
        return ''

    xobj = page['/Resources']['/XObject'].get_object()  # type: ignore
    images = []
    for obj in xobj:
        if xobj[obj]['/Subtype'] == '/Image':
            if xobj[obj]['/Filter'][1:] in PDF_FILTER_WITHOUT_LOSS:
                height, width = xobj[obj]['/Height'], xobj[obj]['/Width']

                images.append(
                    np.frombuffer(
                        xobj[obj].get_data(),
                        dtype=np.uint8,
                    ).reshape(
                        height,
                        width,
                        -1,
                    ),
                )

            elif xobj[obj]['/Filter'][1:] in PDF_FILTER_WITH_LOSS:
                images.append(xobj[obj].get_data())

            else:
                raise Exception('Unknown PDF Filter!')

    return extract_from_images_with_rapidocr(images)


##


def split_text_with_regex(
        text: str,
        separator: str,
        *,
        keep_separator: bool | ta.Literal['start', 'end'],
) -> list[str]:
    if not separator:
        return [s for s in text if s]

    if not keep_separator:
        return [s for s in re.split(separator, text) if s]

    lst = re.split(f'({separator})', text)
    splits = (
        ([lst[i] + lst[i + 1] for i in range(0, len(lst) - 1, 2)])
        if keep_separator == 'end'
        else ([lst[i] + lst[i + 1] for i in range(1, len(lst), 2)])
    )

    if len(lst) % 2 == 0:
        splits += lst[-1:]

    if keep_separator == 'end':
        splits = [*splits, lst[-1]]
    else:
        splits = [lst[0], *splits]

    return [s for s in splits if s]


def join_docs(
        docs: ta.Sequence[str],
        separator: str,
        *,
        strip_whitespace: bool = True,
) -> str | None:
    text = separator.join(docs)
    if strip_whitespace:
        text = text.strip()
    if text == '':
        return None
    else:
        return text


class TextSplitter:
    def __init__(
            self,
            *,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            length_function: ta.Callable[[str], int] = len,
            strip_whitespace: bool = True,
    ) -> None:
        super().__init__()

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function
        self._strip_whitespace = strip_whitespace

    def merge_splits(
            self,
            splits: ta.Iterable[str],
            separator: str,
    ) -> list[str]:
        separator_len = self._length_function(separator)

        docs = []
        current_doc: list[str] = []
        total = 0
        for d in splits:
            l = self._length_function(d)
            if total + l + (separator_len if len(current_doc) > 0 else 0) > self._chunk_size:
                if total > self._chunk_size:
                    raise Exception(f'Created a chunk of size {total}, which is longer than the specified {self._chunk_size}')  # noqa

                if len(current_doc) > 0:
                    doc = join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)

                    while (
                            total > self._chunk_overlap or
                            (total + l + (separator_len if len(current_doc) > 0 else 0) > self._chunk_size and total > 0)  # noqa
                    ):
                        total -= self._length_function(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                        current_doc = current_doc[1:]

            current_doc.append(d)
            total += l + (separator_len if len(current_doc) > 1 else 0)

        doc = join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)

        return docs

    @abc.abstractmethod
    def split_text(
            self,
            text: str,
            *,
            separators: ta.Sequence[str] | None = None,
    ) -> list[str]:
        raise NotImplementedError

    def split_docs(
            self,
            docs: ta.Iterable[Doc],
            *,
            add_start_index: bool = False,
    ) -> list[Doc]:
        texts, metadatas = [], []
        for doc in docs:
            texts.append(doc.content)
            metadatas.append(doc.metadata)

        out = []
        for i, text in enumerate(texts):
            index = 0
            previous_chunk_len = 0
            for chunk in self.split_text(text):
                metadata: dict = dict(metadatas[i] or {})

                if add_start_index:
                    offset = index + previous_chunk_len - self._chunk_overlap
                    index = text.find(chunk, max(0, offset))
                    metadata['start_index'] = index
                    previous_chunk_len = len(chunk)

                out.append(Doc(
                    content=chunk,
                    metadata=metadata,
                ))

        return out


class RecursiveTextSplitter(TextSplitter):
    def __init__(
            self,
            *,
            separators: ta.Sequence[str] = ('\n\n', '\n', ' ', ''),
            is_separator_regex: bool = False,
            keep_separator: bool = True,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._separators = separators
        self._is_separator_regex = is_separator_regex
        self._keep_separator = keep_separator

    def split_text(
            self,
            text: str,
            *,
            separators: ta.Sequence[str] | None = None,
    ) -> list[str]:
        if separators is None:
            separators = self._separators

        final_chunks = []

        separator = separators[-1]
        new_separators: ta.Sequence[str] = []
        for i, _s in enumerate(separators):
            sep = _s if self._is_separator_regex else re.escape(_s)
            if not _s:
                separator = _s
                break
            if re.search(sep, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        sep = separator if self._is_separator_regex else re.escape(separator)
        splits = split_text_with_regex(
            text,
            sep,
            keep_separator=self._keep_separator,
        )

        good_splits = []
        sep = '' if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                good_splits.append(s)
                continue

            if good_splits:
                merged_text = self.merge_splits(good_splits, sep)
                final_chunks.extend(merged_text)
                good_splits = []

            if not new_separators:
                final_chunks.append(s)

            else:
                other_info = self.split_text(s, separators=new_separators)
                final_chunks.extend(other_info)

        if good_splits:
            merged_text = self.merge_splits(good_splits, sep)
            final_chunks.extend(merged_text)

        return final_chunks


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


class DocAndScore(ta.NamedTuple):
    doc: Doc
    score: float


def print_and_join(
        it: ta.Iterable[str],
        *,
        line_len: int | None = None,
        default_line_len: int = 100,
) -> str:
    if line_len is None:
        if default_line_len is None:
            # default_line_len = shutil.get_terminal_size().columns
            raise NotImplementedError
        line_len = default_line_len
    x = 0
    lst = []
    for s in it:
        lst.append(s)
        for ln, l in enumerate(s.split('\n')):
            if ln:
                print()
                x = 0
            for wn, w in enumerate(l.split(' ')):
                if (len(w) + (1 if wn else 0) + x) > line_len:
                    print()
                    x = 0
                elif wn:
                    print(' ', end='')
                print(w, end='')
                x += len(w) + 1
    print()
    return ''.join(lst)


def _main(es: contextlib.ExitStack) -> None:
    pdf_file = os.path.expanduser('~/Downloads/nke-10k-2023.pdf')

    extract_images = False

    self_dir = os.path.dirname(__file__)

    ##

    @_pkl_cache(os.path.join(self_dir, os.path.basename(pdf_file) + '.docs.pkl'))
    def docs() -> list[Doc]:
        print('Loading docs')
        with contextlib.closing(pypdf.PdfReader(pdf_file)) as pdf_reader:
            ret = [
                Doc(
                    content=' '.join([
                        extract_text_from_page(page),
                        *([extract_images_from_page(page)] if extract_images else []),
                    ]),
                    metadata={
                        'source': pdf_file,
                        'page': page_number,
                    },
                )
                for page_number, page in enumerate(pdf_reader.pages)
            ]
        print(f'{len(ret)} docs loaded')
        return ret

    @_pkl_cache(os.path.join(self_dir, os.path.basename(pdf_file) + '.splits.pkl'))
    def splits() -> list[Doc]:
        print('Building splits')
        ret = [
            dc.replace(
                split,
                id=str(uuid.uuid4()),
            )
            for split in RecursiveTextSplitter().split_docs(docs())
        ]
        print(f'{len(ret)} splits built')
        return ret

    ##

    @lang.cached_function
    def embedding_model() -> 'llama_cpp.Llama':
        print('Loading embedding model')
        ret = es.enter_context(contextlib.closing(llama_cpp.Llama(
            model_path=os.path.expanduser('~/.cache/nexa/hub/official/nomic-embed-text-v1.5/fp16.gguf'),
            embedding=True,
            n_ctx=2048,
            verbose=False,
        )))
        print('Embedding model loaded')
        return ret

    def embed(
            s: str,
            mode: ta.Literal['embed', 'query'],
            *,
            embed_instruction: str = 'passage: ',
            query_instruction: str = 'query: ',
            normalize: bool = False,
            truncate: bool = True,
    ) -> list[float]:
        inst = {
            'embed': embed_instruction,
            'query': query_instruction,
        }[mode]

        return embedding_model().embed(
            f'{inst}{s}',
            normalize,
            truncate,
        )

    @_pkl_cache(os.path.join(self_dir, os.path.basename(pdf_file) + '.embeddings.pkl'))
    def embeddings() -> list[list[float]]:
        print(f'Building embeddings')
        ret = []
        for split in term.progress_bar(splits()):
            ret.append(embed(split.content, 'embed'))
        print(f'{len(ret)} embeddings built')
        return ret

    ##

    @lang.cached_function
    def chroma_client() -> 'chromadb.ClientAPI':
        print('Creating chroma client')
        chroma_settings = chromadb.config.Settings(is_persistent=True)
        chroma_settings.persist_directory = os.path.join(self_dir, 'chroma_db')
        ret = chromadb.Client(chroma_settings)
        print('Chroma client created')
        return ret

    @lang.cached_function
    def chroma_collection() -> 'chromadb.Collection':
        return chroma_client().get_or_create_collection(  # noqa
            name='cwpdf',
            embedding_function=None,
        )

    @_pkl_cache(os.path.join(self_dir, os.path.basename(pdf_file) + '.chroma-upserts.pkl'))
    def chroma_upserts() -> int:
        lst = splits()
        chroma_collection.upsert(
            ids=[check.not_none(d.id) for d in lst],
            embeddings=embeddings(),
            documents=[d.content for d in lst],
            metadatas=[check.not_none(d.metadata) for d in lst],
        )
        return len(lst)

    ##

    def get_relevant_documents(
            query: str,
            k: int = 4,
    ) -> list[DocAndScore]:
        query_embedding = embed(query, 'query')

        results = chroma_collection().query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        return [
            DocAndScore(
                Doc(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i] or {},
                    id=results['ids'][0][i],
                ),
                results['distances'][0][i],
            )
            for i in range(len(results['documents'][0]))
        ]

    ##

    def chat_model() -> 'llama_cpp.Llama':
        print('Loading chat model')
        ret = es.enter_context(contextlib.closing(llama_cpp.Llama(
            model_path=os.path.expanduser('~/.cache/nexa/hub/official/Llama3.2-3B-Instruct/q4_0.gguf'),
            chat_format='llama-3',
            n_ctx=2048,
            verbose=False,
        )))
        print('Chat model loaded')
        return ret

    def query_information(query: str) -> str:
        retrieved_docs = get_relevant_documents(query)

        context = '\n\n'.join(d.doc.content for d in retrieved_docs)

        system_prompt = (
            'You are a QA assistant. Based on the following context, answer the question using bullet points and '
            'include necessary data.\n\n'
            f'Context:\n{context}'
        )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query},
        ]

        response_stream = chat_model().create_chat_completion(
            messages,  # type: ignore
            max_tokens=2048,
            temperature=0.7,
            top_k=50,
            top_p=1.0,
            stream=True,
        )
        response_chunks = (
            check.isinstance(p['choices'][0]['delta'].get('content', ''), str)  # type: ignore
            for p in response_stream
        )

        response = print_and_join(response_chunks)  # noqa
        return response

    ##

    def decision_model() -> 'llama_cpp.Llama':
        print('Loading decision model')
        ret = es.enter_context(contextlib.closing(llama_cpp.Llama(
            model_path=os.path.expanduser('~/.cache/nexa/hub/DavidHandsome/Octopus-v2-PDF/gguf-q4_K_M/q4_K_M.gguf'),
            chat_format=None,
            n_ctx=2048,
            verbose=False,
        )))
        print('Decision model loaded')
        return ret

    ##

    print(f'{chroma_upserts()} embeddings upserted to chroma')

    query_information('What is this pdf about?')


if __name__ == '__main__':
    with contextlib.ExitStack() as es:
        _main(es)
