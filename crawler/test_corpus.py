"""
test_corpus.py
author: He Zhang, Shangyu Zhang
"""
from constants import *
import json


def get_test_corpus():
    """
    Get test corpus
    """
    test_raw_corpus = {}
    with open(CHANNELS_CORPUS, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)
        i = 0
        for id in channels:
            test_raw_corpus[id] = channels[id]
            i += 1
            if i >= 20:
                break

    output = json.dumps(test_raw_corpus, indent=4)
    file = open("data/test_corpus_raw.json", 'w')
    file.write(output)
    file.close()

    test_corpus = {}
    with open(CHANNELS_CORPUS_FIXED, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)
        i = 0
        for id in channels:
            test_corpus[id] = channels[id]
            i += 1
            if i >= 20:
                break

    output = json.dumps(test_raw_corpus, indent=4)
    file = open("data/test_corpus.json", 'w')
    file.write(output)
    file.close()


if __name__ == '__main__':
    # Get channels data
    get_test_corpus()
