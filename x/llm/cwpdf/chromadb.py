import os.path
import typing as ta

from omlish import lang

from .docs import Doc


if ta.TYPE_CHECKING:
    import chromadb
else:
    chromadb = lang.proxy_import('chromadb')


##


@lang.cached_function
def chroma_client() -> 'chromadb.ClientAPI':
    log.info('Creating chroma client')
    chroma_settings = chromadb.config.Settings(is_persistent=True)
    chroma_settings.anonymized_telemetry = False
    chroma_settings.persist_directory = os.path.join(data_dir.get(), 'chroma_db')
    ret = chromadb.Client(chroma_settings)
    log.info('Chroma client created')
    return ret


@lang.cached_function
def chroma_collection() -> 'chromadb.Collection':
    return chroma_client().get_or_create_collection(  # noqa
        name='cwpdf',
        embedding_function=None,
    )


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

