"""
api.py
author: Daneil Zhang, He Zhang, Shangyu Zhang
"""

from constants import *

import googleapiclient.discovery
import requests
import datetime
import json
import os
import re


def get_channels():
    """
    Get channel json data through Youtube APIs
    """
    id, resume_id = 0, 1676

    with open(CHANNELS_CORPUS, 'r') as handle:
        channels = json.load(handle)

    f = open(CHANNELS_PATH, "r")
    for line in f:
        id += 1
        if id > resume_id:
            if '/channel/' in line:
                channel_id = line.split('/channel/')[1]
                channel_id, channel = get_channels_by_id(channel_id)
            elif '/user/' in line:
                user = line.split('/user/')[1]
                channel_id, channel = get_channels_by_user(user)
            else:
                channel_id, channel = get_channels_by_id(line)
            if channel is not None:
                channels[channel_id] = channel
            write_to_file(channels)
            print('Corpus Extraction Done -', line + ' ' + str(id))
    f.close()


def get_channels_by_user(user):
    """
    Return channel data through Youtube APIs by user name
    """
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics,id,topicDetails",
        forUsername=user
    )
    return generate_json_data(request.execute())


def get_channels_by_id(channel_id):
    """
    Return channel data through Youtube APIs by channel id
    """
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics,id,topicDetails",
        id=channel_id
    )
    return generate_json_data(request.execute())


def generate_json_data(response):
    """
    Return channel json data by channel response
    """
    if 'items' not in response or len(response['items']) == 0:
        return None, None

    channel_id = response['items'][0]['id'].strip()
    all_upload_datetimes, all_playlists_titles, all_playlists_desc, all_videos_titles, all_videos_desc = get_data_by_channel_id(
        channel_id)

    all_upload_datetimes.sort()
    latest_upload_datetime, upload_interval = None, 10000
    if len(all_upload_datetimes) > 0:
        latest_upload_datetime = all_upload_datetimes[-1]
        upload_interval = get_upload_interval(all_upload_datetimes)
    channel_create_date = datetime.datetime.strptime(
        response['items'][0]['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
    if latest_upload_datetime is None:
        latest_upload_datetime = channel_create_date
    channel_create_date = channel_create_date.strftime("%Y-%m-%d")

    categories = []
    if 'topicDetails' in response['items'][0] and 'topicCategories' in response['items'][0]['topicDetails']:
        categories = response['items'][0]['topicDetails']['topicCategories']

    channel = {
        "channel_id": channel_id,
        "channel_title": response['items'][0]['snippet']['title'],
        "channel_desc": response['items'][0]['snippet']['description'],
        "channel_create_date": channel_create_date,
        "channel_url": CHANNEL_URL_PREFIX + response['items'][0]['id'],
        "view_count": int(response['items'][0]['statistics']['viewCount']),
        "video_count": int(response['items'][0]['statistics']['videoCount']),
        "subscriber_count": int(response['items'][0]['statistics']['subscriberCount']),
        "image_url": response['items'][0]['snippet']['thumbnails']['default']['url'],
        "categories": categories,
        "all_playlists_titles": all_playlists_titles,
        "all_playlists_desc": all_playlists_desc,
        "all_videos_titles": all_videos_titles,
        "all_videos_desc": all_videos_desc,
        "upload_interval": upload_interval,
        "latest_upload_datetime": latest_upload_datetime.strftime("%Y-%m-%d")
    }
    return channel_id, channel


def get_upload_interval(upload_datetimes):
    """
    Return average upload interval in days 
    """
    delta = upload_datetimes[-1] - upload_datetimes[0]
    if len(upload_datetimes) <= 1:
        return 10000
    return delta.days * 1.0 / (len(upload_datetimes) - 1)


def get_data_by_channel_id(channel_id):
    """
    Return channel data by channel id
    """
    if channel_id is None:
        return None, None

    all_upload_datetimes, all_playlists_titles, all_playlists_desc, all_videos_titles, all_videos_desc = [], '', '', '', ''

    all_playlists_titles, all_playlists_desc, playlist_ids = get_playlists_by_channel_id(
        channel_id)

    for id in playlist_ids:
        videos_titles, videos_desc, upload_datetimes = get_videos_corpus_by_playlist_id(
            id)
        all_videos_titles += videos_titles + ' '
        all_videos_desc += videos_desc + ' '
        all_upload_datetimes.extend(upload_datetimes)

    return all_upload_datetimes, all_playlists_titles, all_playlists_desc, all_videos_titles, all_videos_desc


def get_playlists_by_channel_id(channel_id):
    """
    Return playlists by channel id
    """
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId=channel_id,
        maxResults=50
    )
    response = request.execute()
    all_playlists_titles, all_playlists_desc, playlist_ids = '', '', []
    for playlist in response['items']:
        all_playlists_titles += playlist['snippet']['title'] + ' '
        all_playlists_desc += re.sub(r'http\S+', '',
                                     playlist['snippet']['description']) + ' '
        playlist_ids.append(playlist['id'])
    return all_playlists_titles, all_playlists_desc, playlist_ids


def get_videos_corpus_by_playlist_id(playlist_id):
    """
    Return videos corpus by playlist id
    """
    request = youtube.playlistItems().list(
        part="id,snippet,contentDetails",
        playlistId=playlist_id
    )
    response = request.execute()

    videos_titles, videos_desc, upload_datetimes = '', '', []
    for video in response['items']:
        videos_titles += video['snippet']['title'] + ' '
        videos_desc += re.sub(r'http\S+', '',
                              video['snippet']['description']) + ' '
        upload_time = datetime.datetime.strptime(
            video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        upload_datetimes.append(upload_time)

    return videos_titles, videos_desc, upload_datetimes


def write_to_file(data):
    """
    Write the json data to a file.
    """
    output = json.dumps(data, indent=4)
    file = open(CHANNELS_CORPUS, 'w')
    file.write(output)
    file.close()


if __name__ == '__main__':

    # API Setup
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"

    # DEVELOPER_KEY = "AIzaSyAjMXLQV2VFoAiwxYtVrRCkT404E4_lx_I"
    # DEVELOPER_KEY = "AIzaSyDX5B2JVhyABl1CpfJ-oqgAvcVANiDhNsA"
    # DEVELOPER_KEY = "AIzaSyDmEB6yU7S28pDubsn_4bj3VfYB87XzZoo"
    DEVELOPER_KEY = "AIzaSyCX9xAa6ppjgMn0L1bWFZxr3lhD2CE4UgA"
    # DEVELOPER_KEY = "AIzaSyDkgfr9hTbT8Jn4SLZ20NAHy1njVeNtkFc"
    # DEVELOPER_KEY = "AIzaSyBngvBbaJxoZbNI5BvhzhlJh1XWYIEJ24w"
    # DEVELOPER_KEY = "AIzaSyCizsSlO69yTVuJpTefFLbs5U2AN0E4ce8"
    # DEVELOPER_KEY = "AIzaSyDt2pjMNKO_GpgTNISfZq7HwYVCkbpKrzc"
    # DEVELOPER_KEY = "AIzaSyBKr7reeGOMUWXywTM_ki9CWMb_mkLC9Vk"
    # DEVELOPER_KEY = "AIzaSyC3zuhJNNKqUPlprOqj_2nSPOrHmBVfnnM"
    # DEVELOPER_KEY = "AIzaSyA4H0lGCpoD2WDL6-UfXM1rmt9ivArCj9E"
    # DEVELOPER_KEY = "AIzaSyBbcmi9ftOhj4N9HZT5MjfuvflDeqE8TfI"
    # DEVELOPER_KEY = "AIzaSyDgK3K6zbgqw3p5r3haMURIQ-6EDlggjOY"
    # DEVELOPER_KEY = "AIzaSyA3FIbhh4XEiZ9HqI8a1XmbT7ZnYM8CcSs"
    # DEVELOPER_KEY = "AIzaSyBu7Cf4voyk9lgqcNTS37_rIL1lyNjLfrI"
    # DEVELOPER_KEY = "AIzaSyBthPmaUiGA8ESB1MnpR1DWlgKu3-OHozk"
    # DEVELOPER_KEY = "AIzaSyAJd4JMCw0F_6AYeXQkAaHdgJlp4CWJAT4"
    # DEVELOPER_KEY = "AIzaSyB2ZRSInsRFg8GukZwy9UDUwsyr3x_Zpfg"
    # DEVELOPER_KEY = "AIzaSyDleNX060ViHKLua518Nn0BW4pLxuCaM5E"
    

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Get channels data
    get_channels()
