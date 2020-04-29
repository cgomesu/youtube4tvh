#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to a M3U playlist
# Author:       cgomesu
# Date:         April 29th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota. You'll reach it pretty quickly if the
#               channel ID and logo URL are not provided.
#               The author does not provide any sort warranty whatsoever.

import requests


class YoutubeHandler:
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
        # Finds the ID of the channel that best matches the NAME provided
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
            status = response.status_code
            # Parse JSON for key status
            if status != 200:
                reason = response.json()["error"]["errors"][0]["reason"]
                if reason == "keyInvalid":
                    print("The Youtube API key is not valid. "
                          "Review your credentials. Key provided: {}".format(self.apikey))
                print("Unable to use the Youtube API key. Reason: {}".format(reason))
                raise Exception
            # Get channelId from json
            self.channelid = response.json()["items"][0]["snippet"]["channelId"]
            self.channellogo = response.json()["items"][0]["snippet"]["thumbnails"]["default"]["url"]
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
            items = response.json()["items"]
            status = response.status_code
            # Parse JSON for key status
            if status != 200:
                reason = response.json()["error"]["errors"][0]["reason"]
                if reason == "keyInvalid":
                    print("The Youtube API key is invalid. "
                          "Review your credentials. Key provided: {}".format(self.apikey))
                    # Exit program if the API key is invalid because it's pointless to continue
                    exit()
                print("Unable to use the Youtube API key. Reason: {}".format(reason))
                raise Exception
            # Check if there's a live-stream available. Raise exception otherwise.
            if not items:
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
