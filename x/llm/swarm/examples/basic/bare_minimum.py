from x.llm.swarm import Agent
from x.llm.swarm import Swarm

from x.dp.utils import load_secrets

load_secrets()


client = Swarm()

agent = Agent(
    name='Agent',
    instructions='You are a helpful agent.',
)

messages = [{'role': 'user', 'content': 'Hi!'}]
response = client.run(agent=agent, messages=messages)

print(response.messages[-1]['content'])
