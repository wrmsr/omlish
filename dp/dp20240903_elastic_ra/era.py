"""
https://www.elastic.co/search-labs/blog/local-rag-agent-elasticsearch-langgraph-llama3
"""
import os.path
import pprint
import urllib.request
import typing as ta

from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_elasticsearch import ElasticsearchStore
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END
from langgraph.graph import StateGraph
import yaml

from omlish import lang


with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
    os.environ['TAVILY_API_KEY'] = yaml.safe_load(f)['tavily_api_key']


@lang.cached_function
def web_docs() -> list[Document]:
    urls = [
        'https://lilianweng.github.io/posts/2023-06-23-agent/',
        'https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/',
        'https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/',
    ]

    return [
        doc
        for url in urls
        for doc in WebBaseLoader(url).load()
    ]


EMBEDDING_MODEL = 'nomic-embed-text-v1.5'


@lang.cached_function
def es_store() -> ElasticsearchStore:
    es_url = 'http://127.0.0.1:35229/'
    es_index = 'rag-elastic'

    #

    index_url = f'{es_url}{es_index}'
    try:
        urllib.request.urlopen(f'{index_url}/_stats')
    except urllib.request.HTTPError:
        pass
    else:
        urllib.request.urlopen(urllib.request.Request(index_url, method='DELETE'))

    #

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250,
        chunk_overlap=0,
    )

    doc_splits = text_splitter.split_documents(web_docs())

    embeddings = NomicEmbeddings(
        model=EMBEDDING_MODEL,
        inference_mode='local',
    )

    return ElasticsearchStore.from_documents(
        doc_splits,
        embeddings,
        es_url=es_url,
        index_name=es_index,
    )


@lang.cached_function
def retriever() -> VectorStoreRetriever:
    return es_store().as_retriever()


OLLAMA_MODEL = 'llama3'


def create_ollama_chat(**kwargs: ta.Any) -> ChatOllama:
    return ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
        **kwargs,
    )


@lang.cached_function
def retrieval_grader() -> Runnable:
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing relevance 
            of a retrieved document to a user question. If the document contains keywords related to the user question, 
            grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
             <|eot_id|><|start_header_id|>user<|end_header_id|>
            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """,
        input_variables=['question', 'document'],
    )

    return prompt | create_ollama_chat(format='json') | JsonOutputParser()


def format_docs(docs: ta.Sequence[Document]) -> str:
    return '\n\n'.join(doc.page_content for doc in docs)


@lang.cached_function
def rag_chain() -> Runnable:
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
        Question: {question}
        Context: {context}
        Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=['question', 'document'],
    )

    return prompt | create_ollama_chat() | StrOutputParser()


@lang.cached_function
def hallucination_grader() -> Runnable:
    prompt = PromptTemplate(
        template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether 
        an answer is grounded in / supported by a set of facts. Give a binary 'yes' or 'no' score to indicate 
        whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a 
        single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
        Here are the facts:
        \n ------- \n
        {documents} 
        \n ------- \n
        Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=['generation', 'documents'],
    )

    return prompt | create_ollama_chat(format='json') | JsonOutputParser()


@lang.cached_function
def answer_grader() -> Runnable:
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an 
        answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is 
        useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
         <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
        \n ------- \n
        {generation} 
        \n ------- \n
        Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=['generation', 'question'],
    )

    return prompt | create_ollama_chat(format='json') | JsonOutputParser()


@lang.cached_function
def question_router() -> Runnable:
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an expert at routing a 
        user question to a vectorstore or web search. Use the vectorstore for questions on LLM  agents, 
        prompt engineering, and adversarial attacks. You do not need to be stringent with the keywords 
        in the question related to these topics. Otherwise, use web-search. Give a binary choice 'web_search' 
        or 'vectorstore' based on the question. Return the a JSON with a single key 'datasource' and 
        no preamble or explanation. Question to route: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=['question'],
    )

    return prompt | create_ollama_chat(format='json') | JsonOutputParser()


@lang.cached_function
def web_search_tool() -> TavilySearchResults:
    return TavilySearchResults(k=3)


def _main() -> None:
    class GraphState(ta.TypedDict):
        question: str
        generation: str
        web_search: str
        documents: list[str]

    ### Nodes

    def retrieve(state):
        """Retrieve documents from vectorstore"""

        print("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        documents = retriever().invoke(question)
        return {"documents": documents, "question": question}

    def generate(state):
        """Generate answer using RAG on retrieved documents"""

        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = rag_chain().invoke({"context": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}

    def grade_documents(state):
        """
        Determines whether the retrieved documents are relevant to the question If any document is not relevant, we will
        set a flag to run web search
        """

        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        web_search = "No"
        for d in documents:
            score = retrieval_grader().invoke({"question": question, "document": d.page_content})
            grade = score["score"]
            # Document relevant
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            # Document not relevant
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = "Yes"
                continue
        return {"documents": filtered_docs, "question": question, "web_search": web_search}

    def web_search(state):
        """Web search based based on the question"""

        print("---WEB SEARCH---")
        question = state["question"]
        documents = state.get("documents")

        # Web search
        docs = web_search_tool().invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
        web_results = Document(page_content=web_results)
        if documents is not None:
            documents.append(web_results)
        else:
            documents = [web_results]
        return {"documents": documents, "question": question}

    ### Conditional edge

    def route_question(state):
        """Route question to web search or RAG."""

        print("---ROUTE QUESTION---")
        question = state["question"]
        print(question)
        source = question_router().invoke({"question": question})
        print(source)
        print(source["datasource"])
        if source["datasource"] == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "websearch"
        elif source["datasource"] == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
            return "vectorstore"

    def decide_to_generate(state):
        """Determines whether to generate an answer, or add web search"""

        print("---ASSESS GRADED DOCUMENTS---")
        print(state["question"])
        web_search = state["web_search"]
        print(state["documents"])

        if web_search == "Yes":
            # All documents have been filtered check_relevance. We will re-generate a new query
            print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---")
            return "websearch"
        else:
            # We have relevant documents, so generate answer
            print("---DECISION: GENERATE---")
            return "generate"

    ### Conditional edge

    def grade_generation_v_documents_and_question(state):
        """Determines whether the generation is grounded in the document and answers question."""

        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = hallucination_grader().invoke({"documents": documents, "generation": generation})

        pprint.pprint(score)

        # Check if 'score' key exists in the score dictionary
        if "score" not in score:
            print("Error: 'score' key not found in the result")
            return "error"  # Or handle the error appropriately

        grade = score["score"]

        # Check hallucination
        if grade == "yes":
            print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            print("---GRADE GENERATION vs QUESTION---")
            score = answer_grader().invoke({"question": question, "generation": generation})

            # Debug print to see what `score` contains
            pprint.pprint(score)

            if "score" not in score:
                print("Error: 'score' key not found in the result")
                return "error"  # Or handle the error appropriately

            grade = score["score"]
            if grade == "yes":
                print("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"

        else:
            pprint.pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"

    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("websearch", web_search)  # web search
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("generate", generate)  # generatae

    ##

    # Build graph
    workflow.set_conditional_entry_point(
        route_question,
        {
            "websearch": "websearch",
            "vectorstore": "retrieve",
        },
    )

    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "websearch": "websearch",
            "generate": "generate",
        },
    )
    workflow.add_edge("websearch", "generate")
    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": END,
            "not useful": "websearch",
        },
    )

    ##

    app = workflow.compile()

    inputs = {"question": "What is agent memory?"}
    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Finished running: {key}:")
    pprint.pprint(value["generation"])

    inputs = {"question": "Who are the LA Lakers expected to draft first in the NBA draft?"}
    for output in app.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"Finished running: {key}:")
    pprint.pprint(value["generation"])


if __name__ == '__main__':
    _main()
