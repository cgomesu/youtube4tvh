#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to an M3U playlist
# Author:       cgomesu
# Date:         September 14th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota.
#               The author does not provide any sort warranty whatsoever.

import json
import re
import requests


class YoutubeHandlerNoAPI:
    """
    A class for extracting info from Youtube using its frontend.
    No valid API key is required and there are no usage limits.
    """
    # a regex dictionary for parsing content from various GET requests
    regex_dict = {
        'json_content': re.compile(r'(?P<json_data>\{\"responseContext\".+\})\;', re.IGNORECASE | re.MULTILINE),
        'viewer_digits': re.compile(r'\d*'),
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
        print('Requesting search results for \'{}\'...'.format(self.channelname))
        try:
            req = self.session.get(url='{}://{}.{}{}{}'.format(self.req_url['protocol'],
                                                                self.req_url['subdomain'],
                                                                self.req_url['domain'],
                                                                self.req_url['subfolder_search'],
                                                                self.req_url['resource_search']),
                                   headers=self.req_headers,
                                   params=parameters)
            print('URL: {}'.format(req.url))
            print('Status code: {}'.format(req.status_code))
            if req.status_code is not 200:
                raise requests.HTTPError
        except requests.ConnectionError as err:
            print('There was a network problem: {}'.format(err))
            return None, None
        except requests.Timeout:
            print('The connection timed-out.')
            return None, None
        except requests.HTTPError:
            print('The URL returned a bad HTTP code (not 200). Check the URL.')
            return None, None
        print('Parsing request...')
        try:
            find_data = re.findall(self.regex_dict['json_content'], req.text)
            if not find_data:
                raise Exception('Unable to find the json content')
            data = json.loads(find_data[0])
            data_list = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']
            # skip non-channel content, like ads
            section_index, item_index = 'NA', 'NA'
            for i, section in enumerate(data_list['contents']):
                if 'itemSectionRenderer' in section.keys():
                    for j, item in enumerate(section['itemSectionRenderer']['contents']):
                        if 'channelRenderer' in item.keys():
                            section_index, item_index = i, j
                            break
            if section_index is 'NA' or item_index is 'NA':
                raise Exception('Unable to find content from the results of the search query.')
            # extract info from the FIRST search result
            data_item = data_list['contents'][section_index]['itemSectionRenderer']
            self.channelid = data_item['contents'][item_index]['channelRenderer']['channelId']
            # get thumbnail with highest quality
            thumb_index = 0
            if 'thumbnails' in data_item['contents'][item_index]['channelRenderer']['thumbnail'].keys():
                highest_width = -1
                for k, thumb in enumerate(data_item['contents'][item_index]['channelRenderer']['thumbnail']['thumbnails']):
                    current_width = thumb['width']
                    if current_width > highest_width:
                        highest_width = current_width
                        thumb_index = k
            data_item_thumb = data_item['contents'][item_index]['channelRenderer']['thumbnail']['thumbnails'][thumb_index]
            self.channellogo = data_item_thumb['url'] if 'https' in data_item_thumb['url'] else 'https:{}'.format(
                data_item_thumb['url']
            )
            return self.channelid, self.channellogo
        except Exception as err:
            print('There was an error while parsing the request: {}'.format(err))
            return None, None

    def find_stream(self):
        parameters = {
            # show livestreams now
            'view': 2,
            'live_view': 501,
        }
        print('Requesting livestreams from channel \'{}\' with id \'{}\'...'.format(self.channelname,
                                                                                    self.channelid))
        try:
            req = self.session.get(url='{}://{}.{}{}{}{}'.format(self.req_url['protocol'],
                                                                 self.req_url['subdomain'],
                                                                 self.req_url['domain'],
                                                                 self.req_url['subfolder_channel'],
                                                                 self.channelid + '/',
                                                                 self.req_url['resource_videos']),
                                   headers=self.req_headers,
                                   params=parameters)
            print('URL: {}'.format(req.url))
            print('Status code: {}'.format(req.status_code))
            if req.status_code is not 200:
                raise requests.HTTPError
        except requests.ConnectionError as err:
            print('There was a network problem: {}'.format(err))
            return None, None
        except requests.Timeout:
            print('The connection timed-out.')
            return None, None
        except requests.HTTPError:
            print('The URL returned a bad HTTP code (not 200). Check the URL.')
            return None, None
        print('Parsing request...')
        try:
            find_data = re.findall(self.regex_dict['json_content'], req.text)
            if not find_data:
                raise Exception('Unable to find json content from the results of the search query.')
            data = json.loads(find_data[0])
            data_tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            data_videos = {}
            for i, tab in enumerate(data_tabs):
                if 'tabRenderer' in tab.keys():
                    tab_title = tab['tabRenderer']['title']
                    if 'Videos' in tab_title:
                        data_videos = data_tabs[i]
                        break
            if not data_videos:
                raise Exception('Videos section not found in get request.')
            data_videos_list = data_videos['tabRenderer']['content']['sectionListRenderer']
            data_videos_item = data_videos_list['contents'][0]['itemSectionRenderer']
            data_videos_item_video = data_videos_item['contents'][0]['gridRenderer']['items']
            # selection method for channels with multiple livestreams
            # select livestream with the highest number of viewers
            highest_viewers, highest_index = -1, 0
            found_live = False
            for index, item in enumerate(data_videos_item_video):
                # video has a view counter and is not a VOD
                if 'viewCountText' in item['gridVideoRenderer'].keys() \
                        and 'publishedTimeText' not in item['gridVideoRenderer'].keys():
                    found_live = True
                    # extract only digits from viewers count
                    current_index = index
                    viewer_digits = re.match(
                        self.regex_dict['viewer_digits'],
                        item['gridVideoRenderer']['viewCountText']['runs'][0]['text'].replace(',', '')
                    ) if 'runs' in item['gridVideoRenderer']['viewCountText'].keys() else re.match(
                        self.regex_dict['viewer_digits'],
                        item['gridVideoRenderer']['viewCountText']['simpleText'].replace(',', '')
                    )
                    # assume 0 viewer if unable to find digits
                    current_viewers = int(viewer_digits.group()) if viewer_digits.group() else 0
                    if current_viewers > highest_viewers:
                        highest_viewers, highest_index = current_viewers, current_index
            if not found_live:
                raise Exception('Unable to find a livestream for this channel right now.')
            data_videos_item_video = data_videos_item_video[highest_index]['gridVideoRenderer']
            # extract livestream URL from the video with the highest number of viewers or the first found (default)
            video = {
                'title': data_videos_item_video['title']['accessibility']['accessibilityData']['label'].encode('utf-8'),
                'description': 'NA',
                'id': data_videos_item_video['videoId'],
                'url': 'https://www.youtube.com/watch?v={}'.format(data_videos_item_video['videoId']),
                'date': 'NA',
                'region': 'NA',
            }
            print('Done extracting info from the live-stream!')
            print('Test it out: {}'.format(video['url']))
            print('Livestream viewers: {}'.format(highest_viewers))
            return video
        except Exception as err:
            print('There was an error while trying to retrieve the videoId from the live-stream: {}'.format(err))
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
            resource = 'search'
            parameters = {
                'key': self.apikey,
                'part': 'snippet',
                'type': 'channel',
                'maxResults': 1,
                'q': self.channelname
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Parse JSON for key status
            if response.status_code != 200:
                if response.json()['error']['errors'][0]['reason'] == 'keyInvalid':
                    print('The Youtube API key is not valid. '
                          'Review your credentials. Key provided: {}'.format(self.apikey))
                    # Exit program if the API key is invalid because it's pointless to continue
                    exit()
                print('Unable to use the Youtube API key.')
                raise Exception(response.json()['error']['errors'][0]['reason'])
            # Get channelId from json
            self.channelid = response.json()['items'][0]['snippet']['channelId']
            self.channellogo = response.json()['items'][0]['snippet']['thumbnails']['high']['url']
            print('The channel ID is: {}'.format(self.channelid))
            print('The URL of the channel\'s logo is: {}'.format(self.channellogo))
            return self.channelid, self.channellogo
        except Exception as err:
            print('There was an error while retrieving the channel info: {}'.format(err))
            return None, None

    def find_stream(self):
        """
        Retrieves info from the live-stream of a specified channelId
        :return: video as a dictionary OR None
        """
        try:
            # Check https://developers.google.com/youtube/v3/docs
            # If multiple streams, prioritize highest view count
            resource = 'search'
            parameters = {
                'key': self.apikey,
                'part': 'id,snippet',
                'channelId': self.channelid,
                'type': 'video',
                'eventType': 'live',
                'order': 'viewCount'
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Parse JSON for key status
            if response.status_code != 200:
                if response.json()['error']['errors'][0]['reason'] == 'keyInvalid':
                    print('The Youtube API key is invalid. '
                          'Review your credentials. Key provided: {}'.format(self.apikey))
                    # Exit program if the API key is invalid because it's pointless to continue
                    exit()
                print('Unable to use the Youtube API key.')
                raise Exception(response.json()['error']['errors'][0]['reason'])
            # Check if there's a live-stream available. Raise exception otherwise.
            if not response.json()['items']:
                print('Unable to find a live-stream on channel ID {}'.format(self.channelid))
                raise Exception('missing items in response')
            print('A live-stream was found! Extracting info from it...')
            # Parse video info from json
            # Make sure to encode(utf-8 or -16) because otherwise, we'll get some unicode error,
            # owing to the presence of special characters in title, description, etc.
            video = {
                'title': response.json()['items'][0]['snippet']['title'].encode('utf-8'),
                'description': response.json()['items'][0]['snippet']['description'].encode('utf-8'),
                'id': response.json()['items'][0]['id']['videoId'],
                'url': 'https://www.youtube.com/watch?v=' + response.json()['items'][0]['id']['videoId'],
                'date': response.json()['items'][0]['snippet']['publishedAt'].encode('utf-8'),
                'region': response.json()['regionCode'].encode('utf-8')
            }
            print('Done extracting info from the live-stream!')
            return video
        except Exception as err:
            print('There was an error while trying to retrieve the videoId from the live-stream: {}'.format(err))
            return None
