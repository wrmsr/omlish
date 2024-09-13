"""
https://python.langchain.com/v0.2/docs/tutorials/local_rag/
"""
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)

    #

    local_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)

    #

    question = "What are the approaches to Task Decomposition?"
    docs = vectorstore.similarity_search(question)
    print(len(docs))
    print(docs[0])

    #

    model = ChatOllama(
        model="llama3.1:8b",
    )

    #

    response_message = model.invoke(
        "Simulate a rap battle between Stephen Colbert and John Oliver"
    )

    print(response_message.content)


if __name__ == '__main__':
    _main()
