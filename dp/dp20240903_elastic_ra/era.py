"""
https://www.elastic.co/search-labs/blog/local-rag-agent-elasticsearch-langgraph-llama3
"""
import os.path
import urllib.request
import yaml

from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_elasticsearch import ElasticsearchStore
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pprint import pprint
from typing import List

import time

from langchain_core.documents import Document
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph


with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
    os.environ['TAVILY_API_KEY'] = yaml.safe_load(f)['tavily_api_key']


def _main():
    es_url = 'http://127.0.0.1:35229/'
    es_index = 'rag-elastic'

    index_url = f'{es_url}{es_index}'
    try:
        urllib.request.urlopen(f'{index_url}/_stats')
    except urllib.request.HTTPError:
        pass
    else:
        urllib.request.urlopen(urllib.request.Request(index_url, method='DELETE'))

    ##
    # 1. Indexing

    local_llm = 'llama3'

    urls = [
        'https://lilianweng.github.io/posts/2023-06-23-agent/',
        'https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/',
        'https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/',
    ]

    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250,
        chunk_overlap=0,
    )
    doc_splits = text_splitter.split_documents(docs_list)
    documents = doc_splits

    embeddings = NomicEmbeddings(
        model='nomic-embed-text-v1.5',
        inference_mode='local',
    )

    db = ElasticsearchStore.from_documents(
        documents,
        embeddings,
        es_url=es_url,
        index_name=es_index,
    )
    retriever = db.as_retriever()

    ##
    # 2. Retrieval Grader

    llm = ChatOllama(model=local_llm, format='json', temperature=0)

    prompt = PromptTemplate(
        template="""
        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are a grader assessing relevance of a retrieved document to a user question. If the document contains
        keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal
        is to filter out erroneous retrievals.

        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.

        Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>
        Here is the retrieved document:
        {document}
        
        Here is the user question:
        {question}
        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>
        """,
        input_variables=['question', 'document'],
    )

    retrieval_grader = prompt | llm | JsonOutputParser()
    question = 'agent memory'
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content
    generation = retrieval_grader.invoke({'question': question, 'document': doc_txt})
    print(generation)

    ##
    # 3. Generator

    # Prompt

    # The context discusses agent memory, specifically mentioning the design of generative agents that combines LLM with
    # memory, planning, and reflection mechanisms. It also mentions short-term and long-term memory modules, including a
    # retrieval model that surfaces context to inform the agent's behavior. The external vector store is used for fast
    # retrieval and maximum inner-product search (MIPS) algorithms are employed to optimize retrieval speed.
    # prompt = PromptTemplate(
    #     template="""
    #     <|begin_of_text|>
    #
    #     <|start_header_id|>system<|end_header_id|>
    #     You are an assistant for question-answering tasks.
    #
    #     Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say
    #     that you don't know. Use three sentences maximum and keep the answer concise
    #     <|eot_id|>
    #
    #     <|start_header_id|>user<|end_header_id|>
    #     Question: {question}
    #
    #     Context: {context}
    #
    #     Answer:
    #     <|eot_id|>
    #
    #     <|start_header_id|>assistant<|end_header_id|>
    #     """,
    #     input_variables=['question', 'document'],
    # )

    # The context discusses agent memory, specifically mentioning the design of generative agents that combines LLM with
    # memory, planning, and reflection mechanisms. It also mentions short-term and long-term memory modules, including a
    # retrieval model that surfaces context to inform the agent's behavior. The external vector store is used for fast
    # retrieval and maximum inner-product search (MIPS) algorithms are employed to optimize retrieval speed.
    # prompt = PromptTemplate(
    #     template="""
    #     <|begin_of_text|>
    #
    #     <|start_header_id|>system<|end_header_id|>
    #     You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the
    #     question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the
    #     answer concise
    #     <|eot_id|>
    #
    #     <|start_header_id|>user<|end_header_id|>
    #     Question: {question}
    #     Context: {context}
    #     Answer:
    #     <|eot_id|>
    #
    #     <|start_header_id|>assistant<|end_header_id|>
    #     """,
    #     input_variables=['question', 'document'],
    # )

    # Agent memory in LLM-powered autonomous agents is composed of three components: short-term memory, long-term
    # memory, and sensory memory. Short-term memory refers to the model's ability to learn in-context through prompt
    # engineering. Long-term memory is an external database that stores information and allows for fast retrieval via
    # maximum inner-product search (MIPS) or approximate nearest neighbors (ANN) algorithms.
    # prompt = PromptTemplate(
    #     template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.
    #     Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    #     Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    #     Question: {question}
    #     Context: {context}
    #     Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    #     input_variables=['question', 'document'],
    # )

    # Agent memory refers to the long-term memory module that records a comprehensive list of agents' experience in
    # natural language. This allows the agent to behave conditioned on past experience and interact with other agents.
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
        Question: {question}
        Context: {context}
        Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        input_variables=['question', 'document'],
    )

    # https://github.com/meta-llama/llama3/issues/185

    # Agent memory refers to the long-term memory module that records a comprehensive list of agents' experience in
    # natural language. This allows the agent to retain and recall information over extended periods, leveraging an
    # external vector store and fast retrieval.
    # prompt = PromptTemplate(
    #     template="""
    #     <|begin_of_text|>
    #     <|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.
    #     Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    #     Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    #     Question: {question}
    #     Context: {context}
    #     Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    #     """,
    #     input_variables=['question', 'document'],
    # )

    # Agent memory refers to the long-term memory module that records a comprehensive list of agents' experience in
    # natural language. This allows the agent to retain and recall information over extended periods, leveraging an
    # external vector store and fast retrieval.
    # prompt = PromptTemplate(
    #     template="""
    #     <|begin_of_text|>
    #     <|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks. Use the following
    #     pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    #     Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    #     Question: {question}
    #     Context: {context}
    #     Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    #     """,
    #     input_variables=['question', 'document'],
    # )

    llm = ChatOllama(model=local_llm, temperature=0)

    # Post-processing
    def format_docs(docs):
        return '\n\n'.join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    question = 'agent memory'
    docs = retriever.invoke(question)
    generation = rag_chain.invoke({'context': format_docs(docs), 'question': question})
    print(generation)

    ##
    # 4. Hallucination Grader and Answer Grader

    # Hallucination Grader

    # LLM
    llm = ChatOllama(model=local_llm, format='json', temperature=0)

    # Prompt
    prompt = PromptTemplate(
        template="""
        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are a grader assessing whether an answer is grounded in / supported by a set of facts. Give a binary 'yes'
        or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. Provide the binary
        score as a JSON with a single key 'score' and no preamble or explanation.
        <|eot_id|>
        
        <|start_header_id|>user<|end_header_id|>
        Here are the facts:
        -------
        
        {documents} 
        
        -------
        Here is the answer: {generation}
        <|eot_id|>
        
        <|start_header_id|>assistant<|end_header_id|>
        """,
        input_variables=["generation", "documents"],
    )

    hallucination_grader = prompt | llm | JsonOutputParser()
    generation = hallucination_grader.invoke({'documents': format_docs(docs), 'generation': generation})
    print(generation)

    # Answer Grader

    # LLM
    llm = ChatOllama(model=local_llm, format='json', temperature=0)

    # Prompt
    prompt = PromptTemplate(
        template="""
        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are a grader assessing whether an answer is useful to resolve a question. Give a binary score 'yes' or 'no'
        to indicate whether the answer is useful to resolve a question. Provide the binary score as a JSON with a single
        key 'score' and no preamble or explanation.
        <|eot_id|>
        
        <|start_header_id|>user<|end_header_id|>
        Here is the answer:
        -------
         
        {generation} 
        
        -------
        Here is the question: {question}
        <|eot_id|>
        
        <|start_header_id|>assistant<|end_header_id|>
        """,
        input_variables=['generation', 'question'],
    )

    answer_grader = prompt | llm | JsonOutputParser()
    generation = answer_grader.invoke({'question': question, 'generation': generation})
    print(generation)

    ##
    # 5. Router

    # LLM
    llm = ChatOllama(model=local_llm, format='json', temperature=0)

    prompt = PromptTemplate(
        template="""
        <|begin_of_text|>
        
        <|start_header_id|>system<|end_header_id|>
        You are an expert at routing a user question to a vectorstore or web search. Use the vectorstore for questions
        on LLM  agents, prompt engineering, and adversarial attacks. You do not need to be stringent with the keywords
        in the question related to these topics. Otherwise, use web-search. Give a binary choice 'web_search' or
        'vectorstore' based on the question. Return the a JSON with a single key 'datasource' and no premable or
        explanation.
        
        Question to route: {question}
        <|eot_id|>
        
        <|start_header_id|>assistant<|end_header_id|>
        """,
        input_variables=['question'],
    )

    question_router = prompt | llm | JsonOutputParser()
    question = 'llm agent memory'
    docs = retriever.get_relevant_documents(question)
    doc_txt = docs[1].page_content
    generation = question_router.invoke({'question': question})
    print(generation)

    ##
    # 6. Web Search

    web_search_tool = TavilySearchResults(k=3)

    ##

    class GraphState(TypedDict):
        """
        Represents the state of our graph.

        Attributes:
            question: question
            generation: LLM generation
            web_search: whether to add search
            documents: list of documents
        """

        question: str
        generation: str
        web_search: str
        documents: List[str]

    ### Nodes

    def retrieve(state):
        """
        Retrieve documents from vectorstore

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        documents = retriever.invoke(question)
        return {"documents": documents, "question": question}

    def generate(state):
        """
        Generate answer using RAG on retrieved documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = rag_chain.invoke({"context": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}

    def grade_documents(state):
        """
        Determines whether the retrieved documents are relevant to the question
        If any document is not relevant, we will set a flag to run web search

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Filtered out irrelevant documents and updated web_search state
        """

        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        web_search = "No"
        for d in documents:
            score = retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score["score"]
            # Document relevant
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            # Document not relevant
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                # We do not include the document in filtered_docs
                # We set a flag to indicate that we want to run web search
                web_search = "Yes"
                continue
        return {"documents": filtered_docs, "question": question, "web_search": web_search}

    def web_search(state):
        """
        Web search based based on the question

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Appended web results to documents
        """

        print("---WEB SEARCH---")
        question = state["question"]
        documents = state["documents"]

        # Web search
        docs = web_search_tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
        web_results = Document(page_content=web_results)
        if documents is not None:
            documents.append(web_results)
        else:
            documents = [web_results]
        return {"documents": documents, "question": question}

    ### Conditional edge

    def route_question(state):
        """
        Route question to web search or RAG.

        Args:
            state (dict): The current graph state

        Returns:
            str: Next node to call
        """

        print("---ROUTE QUESTION---")
        question = state["question"]
        print(question)
        source = question_router.invoke({"question": question})
        print(source)
        print(source["datasource"])
        if source["datasource"] == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "websearch"
        elif source["datasource"] == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
            return "vectorstore"

    def decide_to_generate(state):
        """
        Determines whether to generate an answer, or add web search

        Args:
            state (dict): The current graph state

        Returns:
            str: Binary decision for next node to call
        """

        print("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        web_search = state["web_search"]
        state["documents"]

        if web_search == "Yes":
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
            )
            return "websearch"
        else:
            # We have relevant documents, so generate answer
            print("---DECISION: GENERATE---")
            return "generate"

    ### Conditional edge

    def grade_generation_v_documents_and_question(state):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Decision for next node to call
        """

        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = hallucination_grader.invoke(
            {"documents": documents, "generation": generation}
        )

        # Debug print to see what `score` contains
        #    pprint(score)

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
            score = answer_grader.invoke({"question": question, "generation": generation})

            # Debug print to see what `score` contains
            pprint(score)

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
            pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
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

    # Compile
    app = workflow.compile()

    def run_app(inputs):
        for output in app.stream(inputs):
            for key, value in output.items():
                pprint(f"Finished running: {key}:")
        return value

    value = run_app({"question": "What is agent memory?"})
    pprint(value["generation"])


if __name__ == '__main__':
    _main()
