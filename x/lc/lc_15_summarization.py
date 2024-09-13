"""
https://python.langchain.com/v0.2/docs/tutorials/summarization/
"""
import typing as ta
import operator


from langchain.chains.combine_documents.reduce import (
    acollapse_docs,
    split_list_of_docs,
)
from langchain_core.documents import Document
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langchain_text_splitters import CharacterTextSplitter
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    docs = loader.load()

    #

    llm = ChatOpenAI(model="gpt-4o-mini")

    #

    # Define prompt
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Write a concise summary of the following:\\n\\n{context}")]
    )

    # Instantiate chain
    chain = create_stuff_documents_chain(llm, prompt)

    # Invoke chain
    result = chain.invoke({"context": docs})
    print(result)

    #

    for token in chain.stream({"context": docs}):
        print(token, end="|")

    #

    map_prompt = ChatPromptTemplate.from_messages(
        [("system", "Write a concise summary of the following:\\n\\n{context}")]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    #

    map_prompt = hub.pull("rlm/map-prompt")

    #

    # Also available via the hub: `hub.pull("rlm/reduce-prompt")`
    reduce_template = """
    The following is a set of summaries:
    {docs}
    Take these and distill it into a final, consolidated summary
    of the main themes.
    """

    reduce_prompt = ChatPromptTemplate([("human", reduce_template)])

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    #

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"Generated {len(split_docs)} documents.")

    #

    token_max = 1000

    def length_function(documents: ta.List[Document]) -> int:
        """Get number of tokens for input contents."""
        return sum(llm.get_num_tokens(doc.page_content) for doc in documents)

    # This will be the overall state of the main graph.
    # It will contain the input document contents, corresponding
    # summaries, and a final summary.
    class OverallState(ta.TypedDict):
        # Notice here we use the operator.add
        # This is because we want combine all the summaries we generate
        # from individual nodes back into one list - this is essentially
        # the "reduce" part
        contents: ta.List[str]
        summaries: ta.Annotated[list, operator.add]
        collapsed_summaries: ta.List[Document]
        final_summary: str

    # This will be the state of the node that we will "map" all
    # documents to in order to generate summaries
    class SummaryState(ta.TypedDict):
        content: str

    # Here we generate a summary, given a document
    async def generate_summary(state: SummaryState):
        response = await map_chain.ainvoke(state["content"])
        return {"summaries": [response]}

    # Here we define the logic to map out over the documents
    # We will use this an edge in the graph
    def map_summaries(state: OverallState):
        # We will return a list of `Send` objects
        # Each `Send` object consists of the name of a node in the graph
        # as well as the state to send to that node
        return [
            Send("generate_summary", {"content": content}) for content in state["contents"]
        ]

    def collect_summaries(state: OverallState):
        return {
            "collapsed_summaries": [Document(summary) for summary in state["summaries"]]
        }

    # Add node to collapse summaries
    async def collapse_summaries(state: OverallState):
        doc_lists = split_list_of_docs(
            state["collapsed_summaries"], length_function, token_max
        )
        results = []
        for doc_list in doc_lists:
            results.append(await acollapse_docs(doc_list, reduce_chain.ainvoke))

        return {"collapsed_summaries": results}

    # This represents a conditional edge in the graph that determines
    # if we should collapse the summaries or not
    def should_collapse(
            state: OverallState,
    ) -> ta.Literal["collapse_summaries", "generate_final_summary"]:
        num_tokens = length_function(state["collapsed_summaries"])
        if num_tokens > token_max:
            return "collapse_summaries"
        else:
            return "generate_final_summary"

    # Here we will generate the final summary
    async def generate_final_summary(state: OverallState):
        response = await reduce_chain.ainvoke(state["collapsed_summaries"])
        return {"final_summary": response}

    # Construct the graph
    # Nodes:
    graph = StateGraph(OverallState)
    graph.add_node("generate_summary", generate_summary)  # same as before
    graph.add_node("collect_summaries", collect_summaries)
    graph.add_node("collapse_summaries", collapse_summaries)
    graph.add_node("generate_final_summary", generate_final_summary)

    # Edges:
    graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
    graph.add_edge("generate_summary", "collect_summaries")
    graph.add_conditional_edges("collect_summaries", should_collapse)
    graph.add_conditional_edges("collapse_summaries", should_collapse)
    graph.add_edge("generate_final_summary", END)

    app = graph.compile()

    #

    # Image(app.get_graph().draw_mermaid_png())

    #

    for step in app.stream(
            {"contents": [doc.page_content for doc in split_docs]},
            {"recursion_limit": 10},
    ):
        print(list(step.keys()))

    print(step)


if __name__ == '__main__':
    _main()
