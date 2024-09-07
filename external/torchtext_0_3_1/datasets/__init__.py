from .babi import BABI20
from .imdb import IMDB
from .language_modeling import LanguageModelingDataset
from .language_modeling import PennTreebank
from .language_modeling import WikiText103
from .language_modeling import WikiText2
from .nli import MultiNLI
from .nli import SNLI
from .sequence_tagging import CoNLL2000Chunking
from .sequence_tagging import SequenceTaggingDataset
from .sequence_tagging import UDPOS
from .sst import SST
from .translation import IWSLT
from .translation import Multi30k
from .translation import TranslationDataset
from .translation import WMT14
from .trec import TREC


__all__ = [
    'LanguageModelingDataset',
    'SNLI',
    'MultiNLI',
    'SST',
    'TranslationDataset',
    'Multi30k',
    'IWSLT',
    'WMT14',
    'WikiText2',
    'WikiText103',
    'PennTreebank',
    'TREC',
    'IMDB',
    'SequenceTaggingDataset',
    'UDPOS',
    'CoNLL2000Chunking',
    'BABI20',
]
