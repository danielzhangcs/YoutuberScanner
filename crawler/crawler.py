"""
crawler.py
author: He Zhang, Shangyu Zhang
"""

from urllib.request import urlopen
import json
from bs4 import BeautifulSoup

import requests
import re
import os
import googleapiclient.discovery
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyDv0goC4h_p8hG8WKacN5i5TwykXrg7lO4"
f = open('../data/url_from_ten_differet_categories.txt', "w")
top_ten_categories = ['Educational', 'Cooking', 'Fitness','Sport', 'History', 'Science', 'News', 'Music','Movie', 'Travel','Photography', 'Video_Game', 'Vlog']

"""Here is the 10 categories which contain some sub key words we used to search channel ID using youtube API"""

category_to_keyword = {}
category_to_keyword['Educational'] = ['algebra', 'geometry', 'machine learning', 'programming', 'math class', 'physics class', 'history class','statistics', 'probability','negotiation skills']
category_to_keyword['Cooking'] = ['cooking basics', 'how to cook steak', 'how to cook western food', 'how to cook asian food', 'how to cook mediterranean food']
category_to_keyword['Fitness'] = ['Fitness', 'workout', 'workout for beginners', 'workout mistakes you should avoid', 'cardio workout']
category_to_keyword['Sport'] = ['NBA', 'NFL','european league', 'Premier League', 'La Liga', 'snowboarding', 'ski', 'tennis','sport news']
category_to_keyword['History'] = ['world history', 'history of asia', 'history of europe', 'history of africa', 'history of science']
category_to_keyword['Science'] = ['geography', 'history of physics', 'history of math','history of chemistry']
category_to_keyword['News'] = ['cnn', 'bbc', ]
category_to_keyword['Music'] = ['taylor swift', 'Eminem', 'Katy Perry', 'Ed Sheeran', 'One Direction', 'Ariana Grande', 'Spinnin’ Records', 'Trap Nation', 'Bruno Mars']
category_to_keyword['Travel'] = ['travel guide', 'travel vlog', 'travel adventure']
category_to_keyword['Movie'] = ['movie']
category_to_keyword['Photography'] = ['photography', 'camera', 'photoshop', 'nature photography']
category_to_keyword['Video_Game'] =['ps4','xbox', 'switch','pc games']
category_to_keyword['Vlog'] = ['vlog']


urlSet = set([])
urlRes = []


"""Get channel ID and write to txt file"""
for category in top_ten_categories:
        for keyword in category_to_keyword[category]:
                youTubeApi = googleapiclient.discovery.build(
                        api_service_name, api_version, developerKey=DEVELOPER_KEY)

                request = youTubeApi.search().list(
                        part="snippet",
                        maxResults=50,
                        q=keyword
                )
                response = request.execute()
                for r in response['items']:
                        curUrl = r['snippet']['channelId']
                        if curUrl in urlSet:
                                continue
                        else:
                                urlRes.append(curUrl)
                                urlSet.add(curUrl)
                                f.write(curUrl)
                                f.write('\n')


'''

resSet = set([])

def getHtml(url):

    with urlopen(url) as page:
        html = requests.get(url)
        html.encoding = 'utf-8'
    return html.text

def parse(raw_text):
    pattern = re.compile(r"channelId")
    res = pattern.findall(raw_text)
    return res

def dfs(url, depth):
    if(depth == 0):
        return
    raw = getHtml(url)


raw = getHtml("https://www.youtube.com/channel/UCX9chJwW7gL93LIcC3xP2uQ")
print (raw)
print('\n')
print((parse(raw)))

'''