import json

from x.llm.swarm.examples.airline.configs.agents import *
from x.llm.swarm.examples.airline.evals.eval_utils import run_function_evals


triage_test_cases = 'eval_cases/triage_cases.json'
flight_modification_cases = 'eval_cases/flight_modification_cases.json'

n = 5

if __name__ == '__main__':
    # Run triage_agent evals
    with open(triage_test_cases) as file:
        triage_test_cases = json.load(file)
    run_function_evals(
        triage_agent,
        triage_test_cases,
        n,
        eval_path='eval_results/triage_evals.json',
    )

    # Run flight modification evals
    with open(flight_modification_cases) as file:
        flight_modification_cases = json.load(file)
    run_function_evals(
        flight_modification,
        flight_modification_cases,
        n,
        eval_path='eval_results/flight_modification_evals.json',
    )
