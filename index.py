"""
api.py
author: Daniel Zhang, Shangyu Zhang
"""

import json
import re
import time

from crawler.constants import *
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Keyword, Integer, Double, Date, Long
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match


# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Define analyzers appropriate for your data.
text_analyzer = analyzer(
    'custom',
    tokenizer='lowercase',
    filter=['stop', 'asciifolding', 'porter_stem']
)

name_analyzer = analyzer(
    'custom',
    tokenizer='standard',
    filter=['lowercase', 'asciifolding']
)

# Define document mapping (schema) by defining a class as a subclass of Document.
# This defines fields and their properties (type and analysis applied).
# You can use existing es analyzers or use ones you define yourself as above.


class Channel(Document):
    channel_title = Text(analyzer=name_analyzer)
    channel_desc = Text(analyzer=text_analyzer)

    all_playlists_titles = Text(analyzer=name_analyzer)
    all_playlists_desc = Text(analyzer=text_analyzer)

    all_videos_titles = Text(analyzer=name_analyzer)
    all_videos_desc = Text(analyzer=text_analyzer)

    upload_interval = Double()
    view_count = Long()
    video_count = Integer()
    subscriber_count = Long()

    channel_create_date = Date()
    latest_upload_datetime = Date()

    categories = Text(analyzer=name_analyzer)
    image_url = Keyword()
    channel_url = Keyword()

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Channel, self).save(*args, **kwargs)


# Populate the index
def buildIndex():
    """
    buildIndex creates a new channel index, deleting any existing index of
    the same name.
    It loads a json file containing the channel corpus and does bulk loading
    using a generator function.
    """
    channel_index = Index('channel_index')
    if channel_index.exists():
        channel_index.delete()  # Overwrite any previous version
    channel_index.document(Channel)
    channel_index.create()

    # Open the json channel corpus
    with open(CHANNELS_CORPUS_FIXED, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)

    # Action series for bulk loading with helpers.bulk function.
    # Implemented as a generator, to return one channel with each call.
    # Note that we include the index name here.
    # The Document type is always 'doc'.
    # Every item to be indexed must have a unique key.
    def actions():
        # cid is channel id (used as key into channels dictionary)
        for cid in channels:
            yield {
                "_index": "channel_index",
                "_type": 'doc',
                "_id": cid,
                "channel_title": channels[cid]['channel_title'],
                "channel_desc": channels[cid]['channel_desc'],
                "all_playlists_titles": channels[cid]['all_playlists_titles'],
                "all_playlists_desc": channels[cid]['all_playlists_desc'],
                "all_videos_titles": channels[cid]['all_videos_titles'],
                "all_videos_desc": channels[cid]['all_videos_desc'],
                "upload_interval": channels[cid]['upload_interval'],
                "view_count": channels[cid]['view_count'],
                "video_count": channels[cid]['video_count'],
                "subscriber_count": channels[cid]['subscriber_count'],
                "channel_create_date": channels[cid]['channel_create_date'],
                "latest_upload_datetime": channels[cid]['latest_upload_datetime'],
                "categories": get_categories(channels[cid]['categories']),
                "channel_url": channels[cid]['channel_url'],
                "image_url": channels[cid]['image_url']
            }

    helpers.bulk(es, actions())


def get_categories(categories):
    """
    Parse raw category urls and return category in string array
    """
    cates = list()
    for category in categories:
        if 'wiki/'in category:
            cates.append(category.split('wiki/')[1].replace('_', ' ', 10))
    return cates


# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()
