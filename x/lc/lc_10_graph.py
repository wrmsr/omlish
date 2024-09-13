"""
https://python.langchain.com/v0.2/docs/tutorials/graph/
"""
import os

from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USERNAME"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "password"  # noqa

    #

    graph = Neo4jGraph()

    # Import movie information

    movies_query = """
    LOAD CSV WITH HEADERS FROM 
    'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv'
    AS row
    MERGE (m:Movie {id:row.movieId})
    SET m.released = date(row.released),
        m.title = row.title,
        m.imdbRating = toFloat(row.imdbRating)
    FOREACH (director in split(row.director, '|') | 
        MERGE (p:Person {name:trim(director)})
        MERGE (p)-[:DIRECTED]->(m))
    FOREACH (actor in split(row.actors, '|') | 
        MERGE (p:Person {name:trim(actor)})
        MERGE (p)-[:ACTED_IN]->(m))
    FOREACH (genre in split(row.genres, '|') | 
        MERGE (g:Genre {name:trim(genre)})
        MERGE (m)-[:IN_GENRE]->(g))
    """

    response = graph.query(movies_query)
    print(response)

    #

    graph.refresh_schema()
    print(graph.schema)

    #

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, verbose=True)
    response = chain.invoke({"query": "What was the cast of the Casino?"})
    print(response)

    #

    chain = GraphCypherQAChain.from_llm(
        graph=graph, llm=llm, verbose=True, validate_cypher=True
    )
    response = chain.invoke({"query": "What was the cast of the Casino?"})
    print(response)


if __name__ == '__main__':
    _main()
