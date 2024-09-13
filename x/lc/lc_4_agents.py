"""
https://python.langchain.com/v0.2/docs/tutorials/agents/
"""
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    search = TavilySearchResults(max_results=2)
    search_results = search.invoke("what is the weather in SF")
    print(search_results)

    # If we want, we can create other tools.
    # Once we have all the tools we want, we can put them in a list that we will reference later.
    tools = [search]
    print(tools)

    #

    model = ChatOpenAI(model="gpt-4")

    response = model.invoke([HumanMessage(content="hi!")])
    print(response)

    #

    model_with_tools = model.bind_tools(tools)

    response = model_with_tools.invoke([HumanMessage(content="Hi!")])

    print(f"ContentString: {response.content}")
    print(f"ToolCalls: {response.tool_calls}")

    #

    response = model_with_tools.invoke([HumanMessage(content="What's the weather in SF?")])

    print(f"ContentString: {response.content}")
    print(f"ToolCalls: {response.tool_calls}")

    #

    agent_executor = create_react_agent(model, tools)

    #

    response = agent_executor.invoke({"messages": [HumanMessage(content="hi!")]})
    print(response["messages"])

    #

    response = agent_executor.invoke({
        "messages": [HumanMessage(content="whats the weather in sf?")]
    })
    print(response["messages"])

    #

    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="whats the weather in sf?")]
    }):
        print(chunk)
        print("----")

    #

    memory = MemorySaver()

    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    config = {"configurable": {"thread_id": "abc123"}}

    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="hi im bob!")]
    }, config):
        print(chunk)
        print("----")

    #

    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="whats my name?")]
    }, config):
        print(chunk)
        print("----")

    #

    config = {"configurable": {"thread_id": "xyz123"}}
    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="whats my name?")]
    }, config):
        print(chunk)
        print("----")

    #

    # Create the agent
    memory = MemorySaver()
    model = ChatOpenAI(model="gpt-4")
    search = TavilySearchResults(max_results=2)
    tools = [search]
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    # Use the agent
    config = {"configurable": {"thread_id": "abc123"}}
    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="hi im bob! and i live in sf")]
    }, config):
        print(chunk)
        print("----")

    for chunk in agent_executor.stream({
        "messages": [HumanMessage(content="whats the weather where I live?")]
    }, config):
        print(chunk)
        print("----")


if __name__ == '__main__':
    _main()
