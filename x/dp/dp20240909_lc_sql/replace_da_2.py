"""
https://towardsdatascience.com/can-llms-replace-data-analysts-getting-answers-using-sql-8cf7da132259

list(conn.execute(sa.text("select name, sql from sqlite_master where type='column' order by name")))

list(conn.execute(sa.text("pragma table_info('users')")))
['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
"""
import datetime
import json
import os
import textwrap
import typing as ta

from langchain.agents import AgentExecutor
from langchain.agents import AgentType
from langchain.agents import Tool
from langchain.agents import create_openai_functions_agent
from langchain.agents import create_openai_tools_agent
from langchain.agents import initialize_agent
from langchain.agents import tool
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools.render import format_tool_to_openai_function
from langchain_community.chat_models import ChatOpenAI
from langchain_core.agents import AgentFinish
from langchain_experimental.plan_and_execute import PlanAndExecute
from langchain_experimental.plan_and_execute import load_agent_executor
from langchain_experimental.plan_and_execute import load_chat_planner
from pydantic import BaseModel
from pydantic import Field
import sqlalchemy as sa


##


engine = sa.create_engine(f'sqlite://', echo=True)


def exec_stmt(stmt):
    with engine.begin() as conn:
        rows = conn.execute(sa.text(stmt))
        return [{k: v for k, v in zip(rows.keys(), r)} for r in rows]


##


class SQLQuery(BaseModel):
    query: str = Field(description="SQL query to execute")


@tool(args_schema=SQLQuery)
def execute_sql(query: str) -> str:
    """Returns the result of SQLite query execution as JSON, or returns any errors as a string."""
    try:
        return json.dumps(exec_stmt(query))
    except Exception as e:
        return repr(e)


#

class SQLTable(BaseModel):
    table: str = Field(description="Table name")


@tool(args_schema=SQLTable)
def get_table_columns(table: str) -> str:
    """Returns list of SQLite table column names and types in JSON"""

    q = "pragma table_info('{table}')".format(table=table)
    rows = exec_stmt(q)
    return json.dumps([{'name': r['name'], 'type': r['type']} for r in rows])


#


class SQLTableColumn(BaseModel):
    table: str = Field(description="Table name")
    column: str = Field(description="Column name")
    n: int | None = Field(description="Number of rows, default limit 10")


@tool(args_schema=SQLTableColumn)
def get_table_column_distr(table: str, column: str, n: int = 10) -> str:
    """Returns top n values for the column in JSON"""

    q = """
    select {column}, count(1) as "count" as count
    from {table} 
    group by 1
    order by 2 desc 
    limit {n}
    """.format(table=table, column=column, n=n)

    return json.dumps([r[column] for r in exec_stmt(q)])


#


sql_functions = list(map(format_tool_to_openai_function, [execute_sql, get_table_columns, get_table_column_distr]))

sql_tools = {
    'execute_sql': execute_sql,
    'get_table_columns': get_table_columns,
    'get_table_column_distr': get_table_column_distr
}


##


def _init_database():
    create_sql = """
    CREATE TABLE users (
        user_id INTEGER,
        country TEXT,
        is_active INTEGER,
        age INTEGER
    );

    INSERT INTO users (user_id, country, is_active, age) VALUES
    (1000001, 'United Kingdom', 0, 70),
    (1000002, 'France', 1, 87),
    (1000003, 'France', 1, 88),
    (1000004, 'Germany', 1, 25),
    (1000005, 'Germany', 1, 48);

    CREATE TABLE sessions (
        user_id INTEGER,
        session_id INTEGER,
        action_date TEXT,
        session_duration INTEGER,
        os TEXT,
        browser TEXT,
        is_fraud INTEGER,
        revenue REAL
    );

    INSERT INTO sessions (user_id, session_id, action_date, session_duration, os, browser, is_fraud, revenue) VALUES
    (1000001, 1, '2021-01-02', 941, 'Windows', 'Chrome', 0, 0.0),
    (1000004, 54, '2021-01-03', 434, 'Windows', 'Safari', 0, 0.0),
    (1000005, 69, '2021-01-04', 548, 'Windows', 'Chrome', 0, 0.0),
    (1000011, 155, '2021-01-04', 642, 'Windows', 'Chrome', 0, 6372.3),
    (1000007, 97, '2021-01-04', 669, 'Windows', 'Chrome', 0, 0.0);
    """

    with engine.begin() as conn:
        for stmt in create_sql.split(';'):
            conn.execute(sa.text(stmt))


def _main():
    _init_database()

    model = 'gpt-4o'
    # model = 'gpt-4-1106-preview'

    with open(os.path.expanduser('~/Dropbox/.dotfiles/.openai')) as f:
        openai_api_key = f.read().strip()
    os.environ['OPENAI_API_KEY'] = openai_api_key

    llm = ChatOpenAI(temperature=0.1, model=model).bind(functions=sql_functions)

    #

    system_message = """
    You are working as a product analyst for the e-commerce company. 
    
    Your work is very important, since your product team makes decisions based on the data you provide. So, you are
    extremely accurate with the numbers you are provided. 
    
    If you're not sure about the details of the request, you don't provide the answer and ask follow-up questions to
    have a clear understanding.

    You are very helpful and try your best to answer the questions.

    All the data is stored in SQLite Database. Here is the list of tables with
    descriptions:
    - users - information about the customers, one row - one customer
    - sessions - information about the sessions customers made on our web site, one row - one session
    """

    question = "How many active customers from France do we have?"

    #

    analyst_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    analyst_agent = (
        {
            "question": lambda x: x["question"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        }
        | analyst_prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )

    #

    # resp = analyst_agent.invoke({
    #     "question": question,
    #     "intermediate_steps": [],
    # })

    ##

    # intermediate_steps = []
    # num_iters = 0
    #
    # while True:
    #     # breaking if there were more than 10 iterations
    #     if num_iters >= 10:
    #         break
    #
    #     # invoking the agent chain
    #     output = analyst_agent.invoke(
    #         {
    #             "question": question,
    #             "intermediate_steps": intermediate_steps,
    #         }
    #     )
    #     num_iters += 1
    #
    #     # returning the final result if we got the AgentFinish object
    #     if isinstance(output, AgentFinish):
    #         model_output = output.return_values["output"]
    #         break
    #     # calling tool and adding observation to the scratchpad otherwise
    #     else:
    #         print(f'Executing tool: {output.tool}, arguments: {output.tool_input}')
    #         observation = sql_tools[output.tool](output.tool_input)
    #         print(f'Observation: {observation}')
    #         print()
    #         intermediate_steps.append((output, observation))

    ##

    # analyst_agent_executor = AgentExecutor(
    #     agent=analyst_agent,
    #     tools=[execute_sql, get_table_columns, get_table_column_distr],
    #     verbose=True,
    #     max_iterations=10,  # early stopping criteria
    #     early_stopping_method='generate',
    #     # to ask model to generate the final answer after stopping
    # )
    #
    # model_output = analyst_agent_executor.invoke(
    #     {"question": question}
    # )

    ##

    # agent_kwargs = {
    #     "system_message": SystemMessage(content=system_message)
    # }
    #
    # analyst_agent_openai = initialize_agent(
    #     llm=ChatOpenAI(temperature=0.1, model=model),
    #     agent=AgentType.OPENAI_FUNCTIONS,
    #     tools=[execute_sql, get_table_columns, get_table_column_distr],
    #     agent_kwargs=agent_kwargs,
    #     verbose=True,
    #     max_iterations=10,
    #     early_stopping_method='generate'
    # )
    #
    # model_output = analyst_agent_openai.invoke(
    #     {"input": {"user": {"question": question}}}
    # )

    ##

    # agent_kwargs = {
    #     "prefix": system_message
    # }
    #
    # analyst_agent_react = initialize_agent(
    #     llm=ChatOpenAI(temperature=0.1, model=model),
    #     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #     tools=[execute_sql, get_table_columns, get_table_column_distr],
    #     agent_kwargs=agent_kwargs,
    #     verbose=True,
    #     max_iterations=10,
    #     early_stopping_method='generate'
    # )
    #
    # # model_output = analyst_agent_react.invoke(
    # #     {"input": {"user": {"question": question}}}
    # # )
    #
    # model_output = analyst_agent_react.run(question)

    ##

    model = ChatOpenAI(temperature=0.1, model=model)
    planner = load_chat_planner(model)
    executor = load_agent_executor(
        model,
        tools=[execute_sql, get_table_columns, get_table_column_distr],
        verbose=True,
    )

    executor.chain.agent.llm_chain.prompt.messages[0].prompt.template = \
        system_message + '\n' + executor.chain.agent.llm_chain.prompt.messages[0].prompt.template

    analyst_agent_plan_and_execute = PlanAndExecute(
        planner=planner,
        executor=executor
    )

    model_output = analyst_agent_plan_and_execute.run(question)

    ##

    print('Model output:', model_output)


if __name__ == '__main__':
    _main()
