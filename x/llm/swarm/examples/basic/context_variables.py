from x.llm.swarm import Agent
from x.llm.swarm import Swarm

from x.dp.utils import load_secrets


load_secrets()


client = Swarm()


def instructions(context_variables):
    name = context_variables.get('name', 'User')
    return f'You are a helpful agent. Greet the user by name ({name}).'


def print_account_details(context_variables: dict):
    user_id = context_variables.get('user_id')
    name = context_variables.get('name')
    print(f'Account Details: {name} {user_id}')
    return 'Success'


agent = Agent(
    name='Agent',
    instructions=instructions,
    functions=[print_account_details],
)

context_variables = {'name': 'James', 'user_id': 123}

response = client.run(
    messages=[{'role': 'user', 'content': 'Hi!'}],
    agent=agent,
    context_variables=context_variables,
)
print(response.messages[-1]['content'])

response = client.run(
    messages=[{'role': 'user', 'content': 'Print my account details!'}],
    agent=agent,
    context_variables=context_variables,
)
print(response.messages[-1]['content'])
