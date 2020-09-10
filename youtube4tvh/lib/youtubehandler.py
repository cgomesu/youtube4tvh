#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to an M3U playlist
# Author:       cgomesu
# Date:         September 10th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota.
#               The author does not provide any sort warranty whatsoever.

import re
import requests
import json
from fake_useragent import UserAgent


class YoutubeHandlerNoAPI:
    """
    A class for extracting info from Youtube using it's internal API.
    No valid API key is required.
    """
    # a regex dictionary for parsing content from various GET requests
    regex_dict = {
        'search_content': re.compile(
            r'\{\"responseContext\"[^;]+',
            re.IGNORECASE | re.MULTILINE),
    }

    def __init__(self, channelid, channelname, channellogo):
        self.channelid = channelid
        self.channelname = channelname
        self.channellogo = channellogo
        print('fetching user-agent for headers (it may take a few seconds)...')
        self.req_headers = {
            # fetch ua from current real-world usage stats
            "User-Agent": UserAgent().random,
            'Accept-Language': 'en'
        }
        self.req_url = {
            'protocol': 'https://',
            'subdomain': 'www.',
            'domain': 'youtube.com/',
            'resource_search': 'results',
            'resource_videos': 'videos',
        }
        # https://requests.readthedocs.io/en/latest/user/advanced/#session-objects
        self.session = requests.Session()

    def search_channel(self, query):
        """
        Search Youtube for channels and returns full json from ytInitialData
        :param query: a string with the name of a channel (e.g., france 24)
        :return: json or empty dictionary
        """
        parameters = {
            'search_query': query,
            # list channels by relevance (default)
            'sp': 'EgIQAg==',
        }
        print('requesting search results for \'{}\'...'.format(query))
        try:
            req = self.session.get(url=self.req_url['protocol'] +
                                   self.req_url['subdomain'] +
                                   self.req_url['domain'] +
                                   self.req_url['resource_search'],
                                   headers=self.req_headers,
                                   params=parameters)
            print('url: {}'.format(req.url))
            print('status code: {}'.format(req.status_code))
            if req.status_code is not 200:
                raise requests.HTTPError
            if req.encoding:
                print('encoding request to utf-8...')
                req.encoding = 'utf-8'
        except requests.ConnectionError:
            print('there was a network problem. are you connected to the Internet?')
            return {}
        except requests.Timeout:
            print('connection timed-out.')
            return {}
        except requests.HTTPError:
            print('the url returned a bad HTTP code (not 200). check the url.')
            return {}
        print('parsing request...')
        try:
            return json.loads(re.findall(self.regex_dict['search_content'], req.text)[0])
        except Exception as err:
            print('error parsing the requested text: {}'.format(err))
            # capture request that produced an error to debug it
            print('writing the request to a file...')
            self.write_request(filename=query.replace(' ', '_'), text=req.text)
            return {}

    @staticmethod
    def parse_channel_json(data):
        # TODO: validate data first
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        for content in contents:
            channelname = content['channelRenderer']['title']['simpleText']
            channelid = content['channelRenderer']['channelId']
            channellogo = 'https:' + content['channelRenderer']['thumbnail']['thumbnails'][0]['url']
            print(channelname, channelid, channellogo)

    @staticmethod
    def write_request(filename='last_request', text='empty'):
        try:
            with open(filename + '.txt', 'w') as f:
                f.write(text)
        except Exception as err:
            print('there was an error writing the text to the file \'{}\'.txt: {}'.format(filename, err))


class YoutubeHandlerAPI:
    """
    A class for extracting info from Youtube using its official API v3.
    A valid API key is required.
    """
    def __init__(self,
                 apiurl,
                 apikey,
                 channelid,
                 channelname,
                 channellogo):
        self.apiurl = apiurl
        self.apikey = apikey
        self.channelid = channelid
        self.channelname = channelname
        self.channellogo = channellogo

    def find_chinfo(self):
        # Returns the ID of the channel that best matches the NAME provided and its LOGO
        try:
            # Check https://developers.google.com/youtube/v3/docs
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "snippet",
                "type": "channel",
                "maxResults": 1,
                "q": self.channelname
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Parse JSON for key status
            if response.status_code != 200:
                if response.json()["error"]["errors"][0]["reason"] == "keyInvalid":
                    print("The Youtube API key is not valid. "
                          "Review your credentials. Key provided: {}".format(self.apikey))
                    # Exit program if the API key is invalid because it's pointless to continue
                    exit()
                print("Unable to use the Youtube API key. Reason: {}".
                      format(response.json()["error"]["errors"][0]["reason"]))
                raise Exception
            # Get channelId from json
            self.channelid = response.json()["items"][0]["snippet"]["channelId"]
            self.channellogo = response.json()["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            print("The channel ID is: {}".format(self.channelid))
            print("The URL of the channel's logo is: {}".format(self.channellogo))
            return self.channelid, self.channellogo
        except Exception as err:
            print("There was an error while retrieving the channel info: {}".format(err))
            return None, None

    def find_stream(self):
        # Retrieves info from the live-stream of a specified channelId
        try:
            # Check https://developers.google.com/youtube/v3/docs
            # If multiple streams, prioritize highest view count
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "id,snippet",
                "channelId": self.channelid,
                "type": "video",
                "eventType": "live",
                "order": "viewCount"
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Parse JSON for key status
            if response.status_code != 200:
                if response.json()["error"]["errors"][0]["reason"] == "keyInvalid":
                    print("The Youtube API key is invalid. "
                          "Review your credentials. Key provided: {}".format(self.apikey))
                    # Exit program if the API key is invalid because it's pointless to continue
                    exit()
                print("Unable to use the Youtube API key. Reason: {}".
                      format(response.json()["error"]["errors"][0]["reason"]))
                raise Exception
            # Check if there's a live-stream available. Raise exception otherwise.
            if not response.json()["items"]:
                print("Unable to find a live-stream on channel ID {}".format(self.channelid))
                raise Exception
            print("A live-stream was found!  Extracting info from it...")
            # Parse video info from json
            # Make sure to encode(utf-8 or -16) because otherwise, we'll get some unicode error,
            # owing to the presence of special characters in title, description, etc.
            video = {
                "title": response.json()["items"][0]["snippet"]["title"].encode("utf-8"),
                "description": response.json()["items"][0]["snippet"]["description"].encode("utf-8"),
                "id": response.json()["items"][0]["id"]["videoId"],
                "url": "https://www.youtube.com/watch?v=" + response.json()["items"][0]["id"]["videoId"],
                "date": response.json()["items"][0]["snippet"]["publishedAt"].encode("utf-8"),
                "region": response.json()["regionCode"].encode("utf-8")
            }
            print("Done extracting info from the live-stream!")
            return video
        except Exception as err:
            print("There was an error while trying to retrieve the videoId from the live-stream: {}".format(err))
            return None
