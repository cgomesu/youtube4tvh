#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to an M3U playlist
# Author:       cgomesu
# Date:         September 11th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota.
#               The author does not provide any sort warranty whatsoever.

import re
import requests
import json


class YoutubeHandlerNoAPI:
    """
    A class for extracting info from Youtube using it's internal API.
    No valid API key is required and there are no usage limits.
    """
    # a regex dictionary for parsing content from various GET requests
    regex_dict = {
        'json_content': re.compile(r'(?P<json_data>\{\"responseContext\".+\})\;\n', re.IGNORECASE | re.MULTILINE),
    }

    def __init__(self, channelid, channelname, channellogo):
        self.channelname = channelname
        self.channelid = channelid
        self.channellogo = channellogo
        self.req_headers = {
            "User-Agent": 'Mozilla/5.0 (Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Accept-Language': 'en',
        }
        self.req_url = {
            'protocol': 'https',
            'subdomain': 'www',
            'domain': 'youtube.com',
            'subfolder_search': '/',
            'subfolder_channel': '/channel/',
            'resource_search': 'results',
            'resource_videos': 'videos',
        }
        # https://requests.readthedocs.io/en/latest/user/advanced/#session-objects
        self.session = requests.Session()

    def find_chinfo(self):
        """
        Returns the ID of the channel that best matches the NAME provided and its LOGO
        :return: channelid and channellogo
        """
        parameters = {
            'search_query': self.channelname,
            # list channels by relevance (default)
            'sp': 'EgIQAg==',
        }
        print('requesting search results for \'{}\'...'.format(self.channelname))
        try:
            req = self.session.get(url='{}://{}.{}{}{}'.format(self.req_url['protocol'],
                                                                self.req_url['subdomain'],
                                                                self.req_url['domain'],
                                                                self.req_url['subfolder_search'],
                                                                self.req_url['resource_search']),
                                   headers=self.req_headers,
                                   params=parameters)
            print('url: {}'.format(req.url))
            print('status code: {}'.format(req.status_code))
            if req.status_code is not 200:
                raise requests.HTTPError
            if req.encoding:
                print('encoding request to utf-8...')
                req.encoding = 'utf-8'
        except requests.ConnectionError as err:
            print('there was a network problem: {}'.format(err))
            return None, None
        except requests.Timeout:
            print('the connection timed-out.')
            return None, None
        except requests.HTTPError:
            print('the url returned a bad HTTP code (not 200). check the url.')
            return None, None
        print('parsing request...')
        try:
            find_data = re.findall(self.regex_dict['json_content'], req.text)
            # TODO: improve find_data validation before json.loads()
            if not find_data[0]:
                raise Exception
            data = json.loads(find_data[0])
            data_list = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']
            data_item = data_list['contents'][0]['itemSectionRenderer']
            # TODO: loop items to make sure the data are from the correct channel
            # extract info from the FIRST search result
            # channelname = data_item['contents'][00]['channelRenderer']['title']['simpleText']
            self.channelid = data_item['contents'][00]['channelRenderer']['channelId']
            self.channellogo = 'https:' + \
                               data_item['contents'][00]['channelRenderer']['thumbnail']['thumbnails'][0]['url']
            return self.channelid, self.channellogo
        except Exception as err:
            print('there was an error while parsing the request: {}'.format(err))
            return None, None

    def find_stream(self):
        parameters = {
            # show live streams now
            'view': 2,
            'live_view': 501,
        }
        print('requesting live streams from channel \'{}\' with id {}...'.format(self.channelname, self.channelid))
        try:
            req = self.session.get(url='{}://{}.{}{}{}{}'.format(self.req_url['protocol'],
                                                                 self.req_url['subdomain'],
                                                                 self.req_url['domain'],
                                                                 self.req_url['subfolder_channel'],
                                                                 self.channelid + '/',
                                                                 self.req_url['resource_videos']),
                                   headers=self.req_headers,
                                   params=parameters)
            print('url: {}'.format(req.url))
            print('status code: {}'.format(req.status_code))
            if req.status_code is not 200:
                raise requests.HTTPError
            if req.encoding:
                print('encoding request to utf-8...')
                req.encoding = 'utf-8'
        except requests.ConnectionError as err:
            print('there was a network problem: {}'.format(err))
            return None, None
        except requests.Timeout:
            print('the connection timed-out.')
            return None, None
        except requests.HTTPError:
            print('the url returned a bad HTTP code (not 200). check the url.')
            return None, None
        print('parsing request...')
        # TODO: add proper exceptions
        try:
            find_data = re.findall(self.regex_dict['json_content'], req.text)
            if not find_data[0]:
                raise Exception
            data = json.loads(find_data[0])
            data_tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            for i, tab in enumerate(data_tabs):
                if 'Videos' in tab['tabRenderer']['title']:
                    data_videos = data_tabs[i]
                    break
                data_videos = None
            if not data_videos:
                print('videos section not found in get request.')
                raise Exception
            data_videos_list = data_videos['tabRenderer']['content']['sectionListRenderer']
            data_videos_item = data_videos_list['contents'][0]['itemSectionRenderer']
            data_videos_item_video = data_videos_item['contents'][0]['gridRenderer']['items'][0]['gridVideoRenderer']
            # extract livestream URL from the first list item
            video = {
                'title': data_videos_item_video['title']['runs'][0]['text'].encode('utf-8'),
                'description': 'NA',
                'id': data_videos_item_video['videoId'],
                'url': "https://www.youtube.com/watch?v=" + data_videos_item_video['videoId'],
                'date': 'NA',
                'region': 'NA',
            }
            print('Done extracting info from the live-stream!')
            print('Test it out: {}'.format(video['url']))
            return video
        except Exception as err:
            print("There was an error while trying to retrieve the videoId from the live-stream: {}".format(err))
            return None


class YoutubeHandlerAPI:
    """
    A class for extracting info from Youtube using its official API v3.
    A valid API key is required and there are quota limits.
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
        """
        Returns the ID of the channel that best matches the NAME provided and its LOGO
        :return: channelid, channellogo OR None, None
        """
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
        """
        Retrieves info from the live-stream of a specified channelId
        :return: video as a dictionary OR None
        """
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
