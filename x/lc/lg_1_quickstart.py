"""
https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
import typing as ta

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    class State(ta.TypedDict):
        # Messages have the type "list". The `add_messages` function in the annotation defines how this state key should
        # be updated (in this case, it appends messages to the list, rather than overwriting them)
        messages: ta.Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    #

    llm = ChatAnthropic(model="claude-3-haiku-20240307")

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever the node is used.
    graph_builder.add_node("chatbot", chatbot)

    #

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile()

    # display(Image(graph.get_graph().draw_mermaid_png()))

    #

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        for event in graph.stream({"messages": ("user", user_input)}):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)


if __name__ == '__main__':
    _main()
