from malaya.function import check_file, load_graph, generate_session
from malaya.text.bpe import (
    sentencepiece_tokenizer_bert,
    sentencepiece_tokenizer_xlnet,
)
from malaya.text.trees import tree_from_str
from malaya.path import PATH_CONSTITUENCY, S3_PATH_CONSTITUENCY
import json
from herpetologist import check_type

_transformer_availability = {
    'bert': {
        'Size (MB)': 470.0,
        'Recall': 78.96,
        'Precision': 81.78,
        'FScore': 80.35,
        'CompleteMatch': 10.37,
        'TaggingAccuracy': 91.59,
    },
    'tiny-bert': {
        'Size (MB)': 125.0,
        'Recall': 74.89,
        'Precision': 78.79,
        'FScore': 76.79,
        'CompleteMatch': 9.01,
        'TaggingAccuracy': 91.17,
    },
    'albert': {
        'Size (MB)': 180.0,
        'Recall': 77.57,
        'Precision': 80.50,
        'FScore': 79.01,
        'CompleteMatch': 5.77,
        'TaggingAccuracy': 90.30,
    },
    'tiny-albert': {
        'Size (MB)': 56.7,
        'Recall': 67.21,
        'Precision': 74.89,
        'FScore': 70.84,
        'CompleteMatch': 2.11,
        'TaggingAccuracy': 87.75,
    },
    'xlnet': {
        'Size (MB)': 498.0,
        'Recall': 80.65,
        'Precision': 82.22,
        'FScore': 81.43,
        'CompleteMatch': 11.08,
        'TaggingAccuracy': 92.12,
    },
}


def available_transformer():
    """
    List available transformer models.
    """
    from malaya.function import describe_availability

    return describe_availability(
        _transformer_availability, text = 'tested on 20% test set.'
    )


@check_type
def transformer(model: str = 'xlnet', **kwargs):
    """
    Load Transformer Constituency Parsing model, transfer learning Transformer + self attentive parsing.

    Parameters
    ----------
    model : str, optional (default='bert')
        Model architecture supported. Allowed values:

        * ``'bert'`` - Google BERT BASE parameters.
        * ``'tiny-bert'`` - Google BERT TINY parameters.
        * ``'albert'`` - Google ALBERT BASE parameters.
        * ``'tiny-albert'`` - Google ALBERT TINY parameters.
        * ``'xlnet'`` - Google XLNET BASE parameters.

    Returns
    -------
    result : malaya.model.tf.CONSTITUENCY class
    """

    model = model.lower()
    if model not in _transformer_availability:
        raise ValueError(
            'model not supported, please check supported models from malaya.constituency.available_transformer()'
        )

    check_file(PATH_CONSTITUENCY[model], S3_PATH_CONSTITUENCY[model], **kwargs)
    g = load_graph(PATH_CONSTITUENCY[model]['model'], **kwargs)

    with open(PATH_CONSTITUENCY[model]['dictionary']) as fopen:
        dictionary = json.load(fopen)

    if model in ['bert', 'tiny-bert', 'albert', 'tiny-albert']:

        tokenizer = sentencepiece_tokenizer_bert(
            PATH_CONSTITUENCY[model]['tokenizer'],
            PATH_CONSTITUENCY[model]['vocab'],
        )
        mode = 'bert'

    if model in ['xlnet']:
        tokenizer = sentencepiece_tokenizer_xlnet(
            PATH_CONSTITUENCY[model]['tokenizer']
        )
        mode = 'xlnet'

    from malaya.model.tf import CONSTITUENCY

    return CONSTITUENCY(
        input_ids = g.get_tensor_by_name('import/input_ids:0'),
        word_end_mask = g.get_tensor_by_name('import/word_end_mask:0'),
        charts = g.get_tensor_by_name('import/charts:0'),
        tags = g.get_tensor_by_name('import/tags:0'),
        sess = generate_session(graph = g, **kwargs),
        tokenizer = tokenizer,
        dictionary = dictionary,
        mode = mode,
    )
