"""
https://towardsdatascience.com/can-llms-replace-data-analysts-learning-to-collaborate-9d42488dc327
"""
import datetime
import os
import textwrap
import typing as ta

from langchain.agents import AgentExecutor
from langchain.agents import create_openai_functions_agent
from langchain.agents import create_openai_tools_agent
from langchain.agents import tool
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI
from pydantic import BaseModel
from pydantic import Field



# define tools

class Filters(BaseModel):
    month: str = Field(
        description="Month of the customer's activity in the format %Y-%m-%d",
    )
    city: ta.Optional[str] = Field(
        description="The city of residence for customers (by default no filter)",
        enum=["London", "Berlin", "Amsterdam", "Paris"],
    )


@tool(args_schema=Filters)
def get_monthly_active_users(month: str, city: str = None) -> int:
    """Returns the number of active customers for the specified month.
    Pass month in format %Y-%m-01.
    """

    coefs = {
        'London': 2,
        'Berlin': 1,
        'Amsterdam': 0.5,
        'Paris': 0.25
    }

    dt = datetime.datetime.strptime(month, '%Y-%m-%d')
    total = dt.year + 10 * dt.month

    if city is None:
        return total
    else:
        return int(round(coefs[city] * total))


class Metrics(BaseModel):
    metric1: float = Field(description="Base metric value to calculate the difference")
    metric2: float = Field(description="New metric value that we compare with the baseline")


@tool(args_schema=Metrics)
def percentage_difference(metric1: float, metric2: float) -> float:
    """Calculates the percentage difference between metrics"""
    return (metric2 - metric1) / metric1 * 100


# save them into a list for future use

tools = [get_monthly_active_users, percentage_difference]


def _main():
    with open(os.path.expanduser('~/Dropbox/.dotfiles/.openai')) as f:
        openai_api_key = f.read().strip()
    os.environ['OPENAI_API_KEY'] = openai_api_key

    print(get_monthly_active_users.run({"month": "2023-12-01", "city": "London"}))

    print(get_monthly_active_users.run({"month": "2023-12-01", "city": "Berlin"}))

    ##

    system_message = textwrap.dedent("""
    You are working as a product analyst for a e-commerce company. 
    
    Your work is very important, since your product team makes decisions based on the data you provide. So, you are
    extremely accurate with the numbers you provided. 
    
    If you're not sure about the details of the request, you don't provide the answer and ask follow-up questions to
    have a clear understanding.

    You are very helpful and try your best to answer the questions.
    """)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    ##

    # OpenAI tools agent
    agent_tools = create_openai_tools_agent(
        llm=ChatOpenAI(
            temperature=0.1,
            model='gpt-4-1106-preview',
        ),
        tools=tools,
        prompt=prompt,
    )

    agent_tools_executor = AgentExecutor(
        agent=agent_tools,
        tools=tools,
        verbose=True,
        max_iterations=10,
        early_stopping_method='generate',
    )

    # OpenAI functions agent
    agent_funcs = create_openai_functions_agent(
        llm=ChatOpenAI(
            temperature=0.1,
            model='gpt-4-1106-preview',
        ),
        tools=tools,
        prompt=prompt,
    )

    agent_funcs_executor = AgentExecutor(
        agent=agent_funcs,
        tools=tools,
        verbose=True,
        max_iterations=10,
        early_stopping_method='generate',
    )

    ##

    user_question = (
        'What are the absolute numbers and the percentage difference between '
        'the number of customers in London and Berlin in December 2023?'
    )

    print(agent_funcs_executor.invoke({
        'input': user_question,
         'agent_scratchpad': [],
    }))

    print(agent_tools_executor.invoke({
        'input': user_question,
        'agent_scratchpad': [],
    }))


if __name__ == '__main__':
    _main()
