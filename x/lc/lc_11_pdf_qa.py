"""
https://python.langchain.com/v0.2/docs/tutorials/pdf_qa/
"""
import os.path
import pickle
import urllib.parse
import urllib.request

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dp.utils import load_secrets


PDF_URL = 'https://raw.githubusercontent.com/langchain-ai/langchain/0f2b32ffa96358192e011ee2f8db579a323ed0ce/docs/docs/example_data/nke-10k-2023.pdf'  # noqa


def _main() -> None:
    load_secrets()

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    pdf_name = urllib.parse.urlparse(PDF_URL).path.split('/')[-1]
    pdf_file = os.path.join(data_dir, pdf_name)
    if not os.path.isfile(pdf_file):
        urllib.request.urlretrieve(PDF_URL, pdf_file)

    #

    pdf_pkl_file = pdf_file + '.pkl'
    if os.path.isfile(pdf_pkl_file):
        with open(pdf_pkl_file, 'rb') as f:
            docs = pickle.load(f)
    else:
        pdf_loader = PyPDFLoader(pdf_file)
        docs = pdf_loader.load()
        with open(pdf_pkl_file, 'wb') as f:
            pickle.dump(docs, f)

    #

    print(len(docs))

    #

    print(docs[0].page_content[0:100])
    print(docs[0].metadata)

    #

    llm = ChatOpenAI(model="gpt-4o")

    #

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    retriever = vectorstore.as_retriever()

    #

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    results = rag_chain.invoke({"input": "What was Nike's revenue in 2023?"})
    print(results)

    #

    print(results["context"][0].page_content)
    print(results["context"][0].metadata)


if __name__ == '__main__':
    _main()
