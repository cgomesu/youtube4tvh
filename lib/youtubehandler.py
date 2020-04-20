import requests


class YoutubeHandler:
    def __init__(self,
                 apiurl,
                 apikey,
                 channelid,
                 channelurl,
                 channelname,
                 channellogo):
        self.apiurl = apiurl
        self.apikey = apikey
        self.channelid = channelid
        self.channelurl = channelurl
        self.channelname = channelname
        self.channellogo = channellogo

    def api_validation(self):
        # Checks whether the Youtube API key is valid or not
        try:
            # Check https://developers.google.com/youtube/v3/docs
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "id"
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            status = response.status_code
            # Parse JSON for key status
            if status != 200:
                reason = response.json()["error"]["errors"][0]["reason"]
                if reason == "keyInvalid":
                    print("The Youtube API key is not valid. "
                          "Review your credentials. Key provided: {}".format(self.apikey))
                    return False
                print("Unable to validate the Youtube API key. Key: {}".format(reason))
                return False
            print("The Youtube API key is valid!")
            return True
        except Exception as err:
            print("There was an error while trying to validate the Youtube API key: {}".format(err))
            exit()

    def find_stream(self):
        # Retrieves info from the live-stream of a specified channelId
        try:
            # Check https://developers.google.com/youtube/v3/docs
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "id,snippet",
                "channelId": self.channelid,
                "type": "video",
                "eventType": "live",
                "order": "date"
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            items = response.json()["items"]
            # Check if there's a live-stream available at all. Exit without changing anything otherwise.
            if not items:
                print("Unable to find a live-stream on channel ID {}".format(self.channelid))
                print("The script will exit without updating the youtubelive.m3u file. Bye!")
                exit()
            print("A live-stream was found.  Extracting info...")
            # Parse video info from json
            # Make sure to encode(utf-8) because otherwise we'll get some unicode error,
            # owing to the presence of special characters in title, description, etc., and that's no bueno.
            video = {
                "title": response.json()["items"][0]["snippet"]["title"].encode("utf-8"),
                "description": response.json()["items"][0]["snippet"]["description"].encode("utf-8"),
                "id": response.json()["items"][0]["id"]["videoId"],
                "url": "https://www.youtube.com/watch?v=" + response.json()["items"][0]["id"]["videoId"],
                "date": response.json()["items"][0]["snippet"]["publishedAt"].encode("utf-8"),
                "region": response.json()["regionCode"].encode("utf-8")
            }
            print("Done extracting info from the live-stream!")
            print("- Title: {} \n"
                  "- Description: {} \n"
                  "- URL: {} \n"
                  "- Region: {} \n"
                  "- Published at: {}".format(video["title"],
                                              video["description"],
                                              video["url"],
                                              video["region"],
                                              video["date"]))
            return video
        except Exception as err:
            print("There was an error while trying to retrieve the videoId from the live-stream: {}".format(err))
            exit()

    def find_id(self):
        # Adds the first channelId from the channel that best matches the query to the channelid variable
        try:
            # Check https://developers.google.com/youtube/v3/docs
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "snippet",
                "type": "channel",
                "maxResults": 1,
                "fields": "items/snippet/channelId",
                "q": self.channelname
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Get channelId from json
            self.channelid = response.json()["items"][0]["snippet"]["channelId"]
            print("The channel ID is: {}".format(self.channelid))
            return self.channelid
        except Exception as err:
            print("There was an error while trying to retrieve the channel ID: {}".format(err))
            exit()

    def find_logo(self):
        # Retrieves the default logo URL of the channel with the selected channelId
        try:
            # Check https://developers.google.com/youtube/v3/docs
            resource = "search"
            parameters = {
                "key": self.apikey,
                "part": "snippet",
                "type": "channel",
                "channelId": self.channelid,
                "fields": "items/snippet/thumbnails/default/url"
            }
            response = requests.get(self.apiurl + resource, params=parameters)
            # Get channelId from json
            self.channellogo = response.json()["items"][0]["snippet"]["thumbnails"]["default"]["url"]
            print("The URL of the channel's logo is: {}".format(self.channellogo))
            return self.channellogo
        except Exception as err:
            print("There was an error while trying to retrieve the channel's logo: {}".format(err))
            exit()