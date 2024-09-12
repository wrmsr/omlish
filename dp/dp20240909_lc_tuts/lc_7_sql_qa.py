"""
https://python.langchain.com/v0.2/docs/tutorials/sql_qa/
"""
import os.path
import urllib.parse
import urllib.request

from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import bs4

from ..utils import load_secrets


SQL_FILE_URL = 'https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql'  # noqa


def _main() -> None:
    load_secrets()

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    sql_file = os.path.join(data_dir, urllib.parse.urlparse(SQL_FILE_URL).path.split('/')[-1])
    if not os.path.isfile(sql_file):
        urllib.request.urlretrieve(SQL_FILE_URL, sql_file)


    #


if __name__ == '__main__':
    _main()
