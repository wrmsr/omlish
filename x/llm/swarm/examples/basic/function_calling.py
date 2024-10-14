from x.llm.swarm import Agent
from x.llm.swarm import Swarm

from x.dp.utils import load_secrets


load_secrets()


client = Swarm()


def get_weather(location) -> str:
    return "{'temp':67, 'unit':'F'}"


agent = Agent(
    name='Agent',
    instructions='You are a helpful agent.',
    functions=[get_weather],
)

messages = [{'role': 'user', 'content': "What's the weather in NYC?"}]

response = client.run(agent=agent, messages=messages)
print(response.messages[-1]['content'])
