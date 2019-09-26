"""
count_videos.py
author: Daniel Zhang, Shangyu Zhang
"""

from constants import *
import json


def get_video_count():
    """
    Get video count
    """
    count = 0
    with open(CHANNELS_CORPUS, 'r', encoding='utf-8') as data_file:
        # load channels from json file into dictionary
        channels = json.load(data_file)
        for id in channels:
            count += channels[id]['video_count']
        
        print(count)

if __name__ == '__main__':
    # Get channels data
    get_video_count()
