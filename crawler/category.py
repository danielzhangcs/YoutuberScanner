"""
category.py
author: He Zhang, Shangyu Zhang
"""

from constants import *

import json


def get_categories():
    """
    Get categories
    """
    categories = set()
    with open(CHANNELS_CORPUS, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)
        for id in channels:
            categories = categories.union(
                parse_categories(channels[id]['categories']))

    f = open("categories.txt", "w+")
    for cate in categories:
        f.write(cate + '\n')
    f.close()


def parse_categories(categories):
    """
    Parse raw category urls and return category in string array
    """
    cates = set()
    for category in categories:
        if 'wiki/'in category:
            cates.add(category.split('wiki/')[1].replace('_', ' ', 10))
    return cates


if __name__ == '__main__':
    # Get channels data
    get_categories()
