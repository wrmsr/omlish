"""
https://python.langchain.com/v0.2/docs/tutorials/sql_qa/
"""
import ast
import operator
import os.path
import re
import subprocess
import urllib.parse
import urllib.request

from langchain.chains import create_sql_query_chain
from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.prebuilt import create_react_agent

from dp.utils import load_secrets


SQL_FILE_URL = 'https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql'  # noqa


def _main() -> None:
    load_secrets()

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    sql_file = os.path.join(data_dir, urllib.parse.urlparse(SQL_FILE_URL).path.split('/')[-1])
    if not os.path.isfile(sql_file):
        urllib.request.urlretrieve(SQL_FILE_URL, sql_file)

    db_file = os.path.join(data_dir, 'Chinook.db')
    if os.path.isfile(db_file):
        os.unlink(db_file)
    with open(sql_file, 'rb') as f:
        sql_src = f.read()
    subprocess.run([
        'sqlite3',
        db_file,
    ], input=sql_src, check=True)

    #

    db = SQLDatabase.from_uri(f"sqlite:///{db_file}")
    print(db.dialect)
    print(db.get_usable_table_names())
    print(db.run("SELECT * FROM Artist LIMIT 10;"))

    #

    llm = ChatOpenAI(model="gpt-4o-mini")

    chain = create_sql_query_chain(llm, db)
    response = chain.invoke({"question": "How many employees are there"})
    print(response)

    print(db.run(response))

    #

    chain.get_prompts()[0].pretty_print()

    #

    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    chain = write_query | execute_query
    response = chain.invoke({"question": "How many employees are there"})
    print(response)

    #

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

    chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=operator.itemgetter("query") | execute_query
            )
            | answer_prompt
            | llm
            | StrOutputParser()
    )

    response = chain.invoke({"question": "How many employees are there"})
    print(response)

    #

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()
    print(tools)

    #

    SQL_PREFIX = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at the tables in the database to see what you can query.
    Do NOT skip this step.
    Then you should query the schema of the most relevant tables."""

    system_message = SystemMessage(content=SQL_PREFIX)

    #

    agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

    #

    for s in agent_executor.stream(
            {"messages": [HumanMessage(content="Which country's customers spent the most?")]}
    ):
        print(s)
        print("----")

    #

    for s in agent_executor.stream(
            {"messages": [HumanMessage(content="Describe the playlisttrack table")]}
    ):
        print(s)
        print("----")

    #

    def query_as_list(db, query):
        res = db.run(query)
        res = [el for sub in ast.literal_eval(res) for el in sub if el]
        res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
        return list(set(res))

    artists = query_as_list(db, "SELECT Name FROM Artist")
    print(artists)

    albums = query_as_list(db, "SELECT Title FROM Album")
    print(albums[:5])

    #

    vector_db = FAISS.from_texts(artists + albums, OpenAIEmbeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
    valid proper nouns. Use the noun most similar to the search."""
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )

    #

    print(retriever_tool.invoke("Alice Chains"))

    #

    system = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    You have access to the following tables: {table_names}

    If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool!
    Do not try to guess at the proper name - use this function to find similar ones.""".format(
        table_names=db.get_usable_table_names()
    )

    system_message = SystemMessage(content=system)

    tools.append(retriever_tool)

    agent = create_react_agent(llm, tools, messages_modifier=system_message)

    #

    for s in agent.stream(
            {"messages": [HumanMessage(content="How many albums does alis in chain have?")]}
    ):
        print(s)
        print("----")


if __name__ == '__main__':
    _main()
