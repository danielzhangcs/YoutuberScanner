"""
main.py
author: Daniel Zhang, He Zhang, Shangyu Zhang

This module implements a (partial, sample) query interface for elasticsearch channel search. 
You will need to rewrite and expand sections to support the types of queries over the fields in your UI.

Documentation for elasticsearch query DSL:
https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

For python version of DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/

Search DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html
"""

import re
import math
from flask import *
from index import Channel
from pprint import pprint
from constants import STOPWORDS
from elasticsearch_dsl.utils import AttrList
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)

# Initialize global variables for rendering page
orig_query = ""
orig_channel_title = ""
orig_upload_interval = ""
orig_category = ""
gresults = {}

# display query page
@app.route("/")
def search():
    return render_template('index.html')

# display results page for first set of results and "next" sets.
@app.route("/results", methods=['POST'])
def results():
    global orig_query
    global orig_channel_title
    global orig_upload_interval
    global orig_category
    global gresults

    page_id = get_page_id(request)

    porter_stemmer = PorterStemmer()

    # if the method of request is post (for initial query), store query in local global variables
    # if the method of request is get (for "next" results), extract query contents from client's global variables
    query = request.form['query']
    channel_title = request.form['channel_title']
    upload_interval = request.form['upload_interval']
    category = request.form['category']

    # update global variable template data
    orig_query = query
    orig_channel_title = channel_title
    orig_upload_interval = upload_interval
    orig_category = category

    ignored = {}

    # Create a search object to query our index
    search = Search(index='channel_index')

    # Build up your elasticsearch query in piecemeal fashion based on the user's parameters passed in.
    # The search API is "chainable".
    # Each call to search.query method adds criteria to our growing elasticsearch query.
    # You will change this section based on how you want to process the query data input into your interface.
    not_found = False
    unknown_query, unknown_channel_title, unknown_upload_interval = '', '', ''

    # search for text
    query = query.lower()
    terms = re.sub('["].*?["]', "", query).strip().split()
    ignored = {t for t in terms if t in STOPWORDS}
    terms = [t for t in terms if t not in STOPWORDS]

    # search for upload frequency
    if len(upload_interval) > 0:
        s = search.query('range', upload_interval={
            'lt': float(upload_interval)})
    else:
        s = search.query('range', upload_interval={
            'lt': 10000})
    if s.count() == 0:
        not_found = True
        unknown_upload_interval = upload_interval

    # search category
    if not_found is False and category != 'Select A Category':
        s = s.query(Q("multi_match", query=category, fields=[
                    'categories'], type='most_fields'))

    if not_found is False:
        for t in terms:
            stemmized_t = porter_stemmer.stem(t)
            s = s.query(Q("multi_match", query=t, fields=['channel_title'], type='most_fields', boost=10)
                        | Q("multi_match", query=stemmized_t, fields=['channel_desc'], type='most_fields', boost=9)
                        | Q("multi_match", query=t, fields=['all_playlists_titles'], type='most_fields', boost=6)
                        | Q("multi_match", query=stemmized_t, fields=['all_playlists_desc'], type='most_fields', boost=5)
                        | Q("multi_match", query=t, fields=['all_videos_titles'], type='most_fields', boost=2)
                        | Q("multi_match", query=stemmized_t, fields=['all_videos_desc'], type='most_fields', boost=1))
            if s.count() == 0:
                not_found = True
                unknown_query = t
                break

    # search phrases
    if not_found is False:
        phrases = re.findall(r'"(.*?)"', query)
        for p in phrases:
            stemmized_p = porter_stemmer.stem(p)
            s = s.query(Q("multi_match", query=p, fields=['channel_title'], type='phrase', boost=10)
                        | Q("multi_match", query=stemmized_p, fields=['channel_desc'], type='most_fields', boost=9)
                        | Q("multi_match", query=p, fields=['all_playlists_titles'], type='most_fields', boost=6)
                        | Q("multi_match", query=stemmized_p, fields=['all_playlists_desc'], type='most_fields', boost=5)
                        | Q("multi_match", query=p, fields=['all_videos_titles'], type='most_fields', boost=2)
                        | Q("multi_match", query=stemmized_p, fields=['all_videos_desc'], type='most_fields', boost=1))
            if s.count() == 0:
                not_found = True
                unknown_query = p
                break

    # search for youtuber's name
    if not_found is False:
        if len(channel_title) > 0:
            for t in channel_title.split():
                term = '*' + t.lower() + '*'
                s = s.query('wildcard', channel_title=term)
                if s.count() == 0:
                    not_found = True
                    unknown_channel_title = t
                    break

    # determine the subset of results to display (based on current <page_id> value)
    start = 0 + (page_id - 1) * 10
    end = 10 + (page_id - 1) * 10

    # execute search and return results in specified range.
    response = s[0:1800].execute()

    # insert data into response
    result_list = {}

    for hit in response.hits:
        result = {}
        if hit.video_count == 0 or hit.subscriber_count == 0 or hit.view_count == 0:
            normalized_subscriber_over_video = 0
        else:
            normalized_subscriber_over_video = math.log(
                hit.subscriber_count * 1.0 / hit.video_count, 2) * 10

        normalized_upload_freq = 1 / (hit.upload_interval + 1) * 10

        result['score'] = hit.meta.score + \
            normalized_subscriber_over_video + normalized_upload_freq
        result['channel_title'] = hit.channel_title
        result['channel_desc'] = hit.channel_desc
        result['view_count'] = hit.view_count
        result['video_count'] = hit.video_count
        result['subscriber_count'] = hit.subscriber_count
        result['channel_create_date'] = hit.channel_create_date
        result['latest_upload_datetime'] = hit.latest_upload_datetime
        result['categories'] = hit.categories
        result['channel_url'] = hit.channel_url
        result['image_url'] = hit.image_url
        result['upload_interval'] = round(hit.upload_interval, 1)
        result_list[hit.meta.id] = result

    result_list = OrderedDict(
        sorted(result_list.items(), key=lambda item: item[1]['score'], reverse=True))

    slice_id, results = 0, {}
    end = end if end < len(result_list) else len(result_list)
    for result in result_list:
        if slice_id >= start and slice_id < end:
            results[result] = result_list[result]
        slice_id += 1

    # make the result list available globally
    gresults = results

    # get the total number of matching results
    result_num = response.hits.total

    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template(
            'index.html', is_result=True, results=results, res_num=result_num,
            pages_num=int(result_num / 10 + 1), page_id=page_id, orig_query=orig_query, category=category,
            orig_channel_title=channel_title, orig_upload_interval=upload_interval, ignored=ignored)
    else:
        return render_template(
            'index.html', is_result=True, res_num=0, pages_num=0, page_id_id=0, category=category,
            orig_query=orig_query, orig_channel_title=channel_title, orig_upload_interval=upload_interval,
            ignored=ignored, unknown_query=unknown_query, unknown_channel_title=unknown_channel_title,
            unknown_upload_interval=unknown_upload_interval)


# display a particular document given a result number
@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    channel = gresults[res]
    return render_template('detail.html', channel=channel)


def get_page_id(request):
    """
    Return the current selected page id.
    """
    if 'page_id' in request.form:
        return int(request.form['page_id'])
    return request.args.get('page_id', default=1, type=int)


if __name__ == "__main__":
    app.run()
