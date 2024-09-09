import json
import random
import time
import os.path

import openai
import requests

from . import wikienv
from . import wrappers


def _load_secrets():
    import os.path
    import yaml

    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']


def _main():
    _load_secrets()

    openai.api_key = os.environ["OPENAI_API_KEY"]

    ##

    def llm(prompt, stop=["\n"]):
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=stop
        )
        return response.choices[0].text

    ##

    env = wikienv.WikiEnv()
    env = wrappers.HotPotQAWrapper(env, split="dev")
    env = wrappers.LoggingWrapper(env)

    def step(env, action):
        attempts = 0
        while attempts < 10:
            try:
                return env.step(action)
            except requests.exceptions.Timeout:
                attempts += 1

    ##

    folder = os.path.join(os.path.dirname(__file__), './prompts/')
    prompt_file = 'prompts_naive.json'
    with open(folder + prompt_file, 'r') as f:
        prompt_dict = json.load(f)

    webthink_examples = prompt_dict['webthink_simple6']
    instruction = """Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation, and Action can be three types: 
    (1) Search[entity], which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search.
    (2) Lookup[keyword], which returns the next sentence containing keyword in the current passage.
    (3) Finish[answer], which returns the answer and finishes the task.
    Here are some examples.
    """
    webthink_prompt = instruction + webthink_examples

    def webthink(idx=None, prompt=webthink_prompt, to_print=True):
        question = env.reset(idx=idx)
        if to_print:
            print(idx, question)
        prompt += question + "\n"
        n_calls, n_badcalls = 0, 0
        for i in range(1, 8):
            n_calls += 1
            thought_action = llm(prompt + f"Thought {i}:", stop=[f"\nObservation {i}:"])
            try:
                thought, action = thought_action.strip().split(f"\nAction {i}: ")
            except:
                print('ohh...', thought_action)
                n_badcalls += 1
                n_calls += 1
                thought = thought_action.strip().split('\n')[0]
                action = llm(prompt + f"Thought {i}: {thought}\nAction {i}:", stop=[f"\n"]).strip()
            obs, r, done, info = step(env, action[0].lower() + action[1:])
            obs = obs.replace('\\n', '')
            step_str = f"Thought {i}: {thought}\nAction {i}: {action}\nObservation {i}: {obs}\n"
            prompt += step_str
            if to_print:
                print(step_str)
            if done:
                break
        if not done:
            obs, r, done, info = step(env, "finish[]")
        if to_print:
            print(info, '\n')
        info.update({'n_calls': n_calls, 'n_badcalls': n_badcalls, 'traj': prompt})
        return r, info

    ##

    idxs = list(range(7405))
    random.Random(233).shuffle(idxs)

    rs = []
    infos = []
    old_time = time.time()
    for i in idxs[:500]:
        r, info = webthink(i, to_print=True)
        rs.append(info['em'])
        infos.append(info)
        print(sum(rs), len(rs), sum(rs) / len(rs), (time.time() - old_time) / len(rs))
        print('-----------')
        print()


if __name__ == '__main__':
    _main()
