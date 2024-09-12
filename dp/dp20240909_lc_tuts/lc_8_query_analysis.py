"""
https://python.langchain.com/v0.2/docs/tutorials/query_analysis/
"""
import datetime
import typing as ta

from langchain_chroma import Chroma
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.pydantic_v1 import Field
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    urls = [
        "https://www.youtube.com/watch?v=HAn9vnJy6S4",
        "https://www.youtube.com/watch?v=dA1cHGACXCo",
        "https://www.youtube.com/watch?v=ZcEMLz27sL4",
        "https://www.youtube.com/watch?v=hvAPnpSfSGo",
        "https://www.youtube.com/watch?v=EhlPDL4QrWY",
        "https://www.youtube.com/watch?v=mmBo8nlu2j0",
        "https://www.youtube.com/watch?v=rQdibOsL1ps",
        "https://www.youtube.com/watch?v=28lC4fqukoc",
        "https://www.youtube.com/watch?v=es-9MgxB-uc",
        "https://www.youtube.com/watch?v=wLRHwKuKvOE",
        "https://www.youtube.com/watch?v=ObIltMaRJvY",
        "https://www.youtube.com/watch?v=DjuXACWYkkU",
        "https://www.youtube.com/watch?v=o7C9ld6Ln-M",
    ]
    docs = []
    for url in urls:
        docs.extend(YoutubeLoader.from_youtube_url(url, add_video_info=True).load())

    #

    # Add some additional metadata: what year the video was published
    for doc in docs:
        doc.metadata["publish_year"] = int(
            datetime.datetime.strptime(
                doc.metadata["publish_date"], "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y")
        )

    #

    print([doc.metadata["title"] for doc in docs])
    print(docs[0].metadata)
    print(docs[0].page_content[:500])

    #

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    chunked_docs = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        chunked_docs,
        embeddings,
    )

    #

    search_results = vectorstore.similarity_search("how do I build a RAG agent")
    print(search_results[0].metadata["title"])
    print(search_results[0].page_content[:500])

    #

    search_results = vectorstore.similarity_search("videos on RAG published in 2023")
    print(search_results[0].metadata["title"])
    print(search_results[0].metadata["publish_date"])
    print(search_results[0].page_content[:500])

    #

    class Search(BaseModel):
        """Search over a database of tutorial videos about a software library."""

        query: str = Field(
            ...,
            description="Similarity search query applied to video transcripts.",
        )
        publish_year: ta.Optional[int] = Field(None, description="Year video was published")

    #

    system = """You are an expert at converting user questions into database queries. \
    You have access to a database of tutorial videos about a software library for building LLM-powered applications. \
    Given a question, return a list of database queries optimized to retrieve the most relevant results.

    If there are acronyms or words you are not familiar with, do not try to rephrase them."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    structured_llm = llm.with_structured_output(Search)
    query_analyzer = {"question": RunnablePassthrough()} | prompt | structured_llm

    #

    print(query_analyzer.invoke("how do I build a RAG agent"))
    print(query_analyzer.invoke("videos on RAG published in 2023"))

    #

    def retrieval(search: Search) -> ta.List[Document]:
        if search.publish_year is not None:
            # This is syntax specific to Chroma,
            # the vector database we are using.
            _filter = {"publish_year": {"$eq": search.publish_year}}
        else:
            _filter = None
        return vectorstore.similarity_search(search.query, filter=_filter)

    retrieval_chain = query_analyzer | retrieval

    #

    results = retrieval_chain.invoke("RAG tutorial published in 2023")
    print([(doc.metadata["title"], doc.metadata["publish_date"]) for doc in results])


if __name__ == '__main__':
    _main()
