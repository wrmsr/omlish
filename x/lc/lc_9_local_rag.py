"""
https://python.langchain.com/v0.2/docs/tutorials/local_rag/
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
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

    #

    prompt = ChatPromptTemplate.from_template(
        "Summarize the main themes in these retrieved docs: {docs}"
    )

    # Convert loaded documents into strings by concatenating their content
    # and ignoring metadata
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = {"docs": format_docs} | prompt | model | StrOutputParser()

    question = "What are the approaches to Task Decomposition?"

    docs = vectorstore.similarity_search(question)

    response = chain.invoke(docs)
    print(response)

    #

    RAG_TEMPLATE = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    <context>
    {context}
    </context>

    Answer the following question:

    {question}"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    chain = (
            RunnablePassthrough.assign(context=lambda input: format_docs(input["context"]))
            | rag_prompt
            | model
            | StrOutputParser()
    )

    question = "What are the approaches to Task Decomposition?"

    docs = vectorstore.similarity_search(question)

    # Run
    response = chain.invoke({"context": docs, "question": question})
    print(response)

    #

    retriever = vectorstore.as_retriever()

    qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | rag_prompt
            | model
            | StrOutputParser()
    )

    question = "What are the approaches to Task Decomposition?"

    response = qa_chain.invoke(question)
    print(response)


if __name__ == '__main__':
    _main()
