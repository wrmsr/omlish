"""
https://huggingface.co/docs/datasets/en/load_hub
https://huggingface.co/docs/datasets/en/how_to
https://huggingface.co/docs/datasets/en/about_arrow
https://huggingface.co/docs/datasets/en/package_reference/main_classes
"""
import typing as ta

import pytest

from omlish import lang
from omlish.testing import pytest as ptu


if ta.TYPE_CHECKING:
    import datasets as hfds
    import transformers

else:
    hfds = lang.proxy_import('datasets')
    transformers = lang.proxy_import('transformers')


@ptu.skip.if_cant_import('datasets')
@pytest.mark.slow
def test_hfds():
    ds_builder = hfds.load_dataset_builder('rotten_tomatoes')
    print(ds_builder.info.description)
    print(ds_builder.info.features)

    dataset = hfds.load_dataset('rotten_tomatoes', split='train')
    print(dataset)
    print(dataset[0])

    print(hfds.get_dataset_split_names('rotten_tomatoes'))

    iterable_dataset = hfds.load_dataset('food101', split='train', streaming=True)
    for example in iterable_dataset:
        print(example)
        break


@ptu.skip.if_cant_import('datasets')
@ptu.skip.if_cant_import('transformers')
@pytest.mark.slow
def test_tokenize():
    dataset = hfds.load_dataset('rotten_tomatoes', split='train')

    tokenizer = transformers.AutoTokenizer.from_pretrained('bert-base-uncased')
    print(tokenizer(dataset[0]['text']))

    def tokenization(example):
        return tokenizer(example['text'])

    tok_dataset = dataset.map(tokenization, batched=True)
    print(dataset[0]['text'])

    tok_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask', 'label'])
    print(dataset[0]['text'])


@ptu.skip.if_cant_import('datasets')
@ptu.skip.if_cant_import('transformers')
@pytest.mark.slow
def test_audio():
    feature_extractor = transformers.AutoFeatureExtractor.from_pretrained('facebook/wav2vec2-base-960h')
    dataset = hfds.load_dataset('PolyAI/minds14', 'en-US', split='train', trust_remote_code=True)

    dataset = dataset.cast_column('audio', hfds.Audio(sampling_rate=16_000))
    print(dataset[0]['audio'])

    def preprocess_function(examples):
        audio_arrays = [x['array'] for x in examples['audio']]
        inputs = feature_extractor(
            audio_arrays,
            sampling_rate=feature_extractor.sampling_rate,
            max_length=16000,
            truncation=True,
        )
        return inputs

    dataset = dataset.map(preprocess_function, batched=True)
    print(dataset[0]['audio'])


@ptu.skip.if_cant_import('datasets')
@pytest.mark.slow
def test_aug():
    # feature_extractor = transformers.AutoFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")

    dataset = hfds.load_dataset('beans', split='train')
    print(dataset[0]['image'])

    from torchvision.transforms import RandomRotation

    rotate = RandomRotation(degrees=(0, 90))

    def transforms(examples):
        examples['pixel_values'] = [rotate(image.convert('RGB')) for image in examples['image']]
        return examples

    dataset.set_transform(transforms)
    print(dataset[0]['pixel_values'])
