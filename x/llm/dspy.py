import os.path

# jfc
os.environ['DSP_CACHEDIR'] = os.path.join(os.path.dirname(__file__), 'cache')
# os.environ.get('DSP_NOTEBOOK_CACHEDIR')

import dspy
import dspy.datasets


def _main():
    with open(os.path.expanduser('~/.omlish-llm/.env')) as f:
        os.environ.update({
            k: v[1:-1] if v.startswith('"') else v
            for l in f
            if (s := l.strip())
            for k, v in [s.split('=')]
        })
    s = None

    #

    turbo = dspy.OpenAI(model='gpt-3.5-turbo')
    colbertv2_wiki17_abstracts = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')

    #

    dspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)

    dataset = dspy.datasets.HotPotQA(
        train_seed=1,
        train_size=20,
        eval_seed=2023,
        dev_size=50,
        test_size=0,
    )

    trainset = [x.with_inputs('question') for x in dataset.train]
    devset = [x.with_inputs('question') for x in dataset.dev]

    train_example = trainset[0]
    dev_example = devset[18]

    #

    class BasicQA(dspy.Signature):
        question = dspy.InputField()
        answer = dspy.OutputField(desc='often between 1 and 5 words')

    #

    generate_answer = dspy.Predict(BasicQA)

    pred = generate_answer(question=dev_example.question)

    print(f'Question: {dev_example.question}')
    print(f'Predicted Answer: {pred.answer}')

    turbo.inspect_history(n=1)

    #

    generate_answer_with_chain_of_thought = dspy.ChainOfThought(BasicQA)

    pred = generate_answer_with_chain_of_thought(question=dev_example.question)

    print(f'Question: {dev_example.question}')
    print(f'Thought: {pred.rationale.split('.', 1)[1].strip()}')
    print(f'Predicted Answer: {pred.answer}')


if __name__ == '__main__':
    _main()
