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
    generation = rag_chain.invoke({'context': docs, 'question': question})
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
    generation = hallucination_grader.invoke({'documents': docs, 'generation': generation})
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


if __name__ == '__main__':
    _main()
