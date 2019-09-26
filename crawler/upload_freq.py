"""
upload_freq.py
author: He Zhang, Shangyu Zhang
"""

from constants import *
import datetime
import json


def get_upload_freq():
    """
    Get upload freq
    """
    with open(CHANNELS_CORPUS, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)
        for id in channels:
            if channels[id]['video_count'] == 0:
                channels[id]['upload_interval'] = 10000
            else:
                delta = datetime.datetime.now() - datetime.datetime.strptime(channels[id]['channel_create_date'], "%Y-%m-%d")
                channels[id]['upload_interval'] = delta.days * 1.0 / channels[id]['video_count']
        
        write_to_file(channels)


def write_to_file(data):
    """
    Write the json data to a file.
    """
    output = json.dumps(data, indent=4)
    file = open(CHANNELS_CORPUS_FIXED, 'w')
    file.write(output)
    file.close()


if __name__ == '__main__':
    get_upload_freq()
