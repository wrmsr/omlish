"""
https://python.langchain.com/v0.1/docs/modules/agents/agent_types/react/
"""
import os

from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAI
import yaml


def _load_secrets():
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        sec = yaml.safe_load(f)
    for l, r in [
        ('TAVILY_API_KEY', 'tavily_api_key'),
        ('OPENAI_API_KEY', 'openai_api_key'),
    ]:
        os.environ[l] = sec[r]


def _main():
    _load_secrets()

    ##

    tools = [TavilySearchResults(max_results=1)]

    ##

    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/react")

    # Choose the LLM to use
    llm = OpenAI()

    # Construct the ReAct agent
    agent = create_react_agent(llm, tools, prompt)

    ##

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke({"input": "what is LangChain?"})

    ##

    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/react-chat")

    # Construct the ReAct agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke({
        "input": "what's my name? Only use a tool if needed, otherwise respond with Final Answer",
        # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
        "chat_history": "Human: Hi! My name is Bob\nAI: Hello Bob! Nice to meet you",
    })


if __name__ == '__main__':
    _main()
