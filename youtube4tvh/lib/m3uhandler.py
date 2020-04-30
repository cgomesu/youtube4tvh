#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to an M3U playlist
# Author:       cgomesu
# Date:         April 30th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota.
#               The author does not provide any sort warranty whatsoever.

import re
import pandas


class M3uHandler:
    def __init__(self, inputm3u, outputm3u):
        self.inputm3u = inputm3u
        self.outputm3u = outputm3u

    def append(self,
               dataframe,
               channelid,
               channelname,
               channelcountry,
               channellogo,
               pipecmd,
               url):
        # Append stream data to the data frame
        channelcontent = "#EXTINF:-1 " \
                         "tvg-id=\"{}\" " \
                         "tvg-name=\"{}\" " \
                         "tvg-language=\"\" " \
                         "tvg-country=\"{}\" " \
                         "tvg-logo=\"{}\" " \
                         "tvg-url=\"\" " \
                         "group-title=\"\"," \
                         "{}\n" \
                         "{} {}".format(channelid,
                                                  channelname,
                                                  channelcountry,
                                                  channellogo,
                                                  channelname,
                                                  pipecmd,
                                                  url)
        data = {
            "channel-content": channelcontent,
            "channel-name": channelname,
            "channel-duration": "-1",
            "tvg-id": channelid,
            "tvg-name": channelname,
            "tvg-language": "",
            "tvg-country": channelcountry,
            "tvg-logo": channellogo,
            "tvg-url": "",
            "group-title": "",
            "stream-url": "{} {}".format(pipecmd, url)
        }
        try:
            df = dataframe.append(data, ignore_index=True)
            print("Stream info successfully appended to the data frame!")
            return df
        except Exception as err:
            print("There was an error APPENDING data to the data frame. Error: {}".format(err))
            return None

    def extract_column(self, dataframe, column_name):
        # Extract content from a data frame column that matches the column_name
        try:
            content_list = []
            for name, content in dataframe.iteritems():
                if name == column_name:
                    # Save match to a list
                    content_list = content.values.tolist()
                    break
            return content_list
        except Exception as err:
            print("There was an error looking for the column \"{}\". Error: {}".format(column_name, err))
            return None

    def parse(self):
        # Define regex dictionary for iptv m3u files
        rx_dict = {
            'bad_header': re.compile(
                r"^\#(?!EXTM3U|EXTINF).*",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'channel_content': re.compile(
                r"^(?P<channel_content>\#EXTINF:.*$\n.*$)",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'channel_name': re.compile(
                r"\,(?P<channel_name>.*$)",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'channel_duration': re.compile(
                r"\#EXTINF:(?P<channel_duration>0|-1)",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_id': re.compile(
                r"tvg-id=\"(?P<extinf_tvg_id>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_name': re.compile(
                r"tvg-name=\"(?P<extinf_tvg_name>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_language': re.compile(
                r"tvg-language=\"(?P<extinf_tvg_language>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_country': re.compile(
                r"tvg-country=\"(?P<extinf_tvg_country>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_logo': re.compile(
                r"tvg-logo=\"(?P<extinf_tvg_logo>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_tvg_url': re.compile(
                r"tvg-url=\"(?P<extinf_tvg_url>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'extinf_group_title': re.compile(
                r"group-title=\"(?P<extinf_group_title>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'stream_url': re.compile(
                r"^(?P<stream_url>(?!\#).*$)",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            )
        }
        try:
            print("Validating the m3u file...")
            with open(self.inputm3u, 'r') as f:
                if rx_dict['bad_header'].search(f.read()) is not None:
                    print("The PARSER is unable to VALIDATE the m3u file {} because it has \n"
                          "at least one #HEADER different than #EXTM3U or #EXTINF. Remove the \n"
                          "bad header(s) to allow the program to parse your m3u file.".format(self.inputm3u))
                    raise Exception
                print("Did not find bad headers in the m3u file {}.".format(self.inputm3u))
        except Exception as err:
            print("There was an error VALIDATING the m3u file: {}".format(err))
            print("Will continue but data frame is None.")
            return None
        # Writes m3u file to a data frame
        try:
            print("Parsing the m3u file...")
            with open(self.inputm3u, 'r') as f:
                parsed_data = (
                    (channel_content.group('channel_content'),
                     channel_name.group('channel_name'),
                     channel_duration.group('channel_duration'),
                     tvg_id.group('extinf_tvg_id'),
                     tvg_name.group('extinf_tvg_name'),
                     tvg_language.group('extinf_tvg_language'),
                     tvg_country.group('extinf_tvg_country'),
                     tvg_logo.group('extinf_tvg_logo'),
                     tvg_url.group('extinf_tvg_url'),
                     group_title.group('extinf_group_title'),
                     stream_url.group('stream_url'))
                    for channel_content in
                    rx_dict['channel_content'].finditer(f.read())
                    for channel_name in
                    rx_dict['channel_name'].finditer(channel_content.group('channel_content'))
                    for channel_duration in
                    rx_dict['channel_duration'].finditer(channel_content.group('channel_content'))
                    for tvg_id in
                    rx_dict['extinf_tvg_id'].finditer(channel_content.group('channel_content'))
                    for tvg_name in
                    rx_dict['extinf_tvg_name'].finditer(channel_content.group('channel_content'))
                    for tvg_language in
                    rx_dict['extinf_tvg_language'].finditer(channel_content.group('channel_content'))
                    for tvg_country in
                    rx_dict['extinf_tvg_country'].finditer(channel_content.group('channel_content'))
                    for tvg_logo in
                    rx_dict['extinf_tvg_logo'].finditer(channel_content.group('channel_content'))
                    for tvg_url in
                    rx_dict['extinf_tvg_url'].finditer(channel_content.group('channel_content'))
                    for group_title in
                    rx_dict['extinf_group_title'].finditer(channel_content.group('channel_content'))
                    for stream_url in
                    rx_dict['stream_url'].finditer(channel_content.group('channel_content'))
                )
                df = pandas.DataFrame(parsed_data, columns=['channel-content',
                                                            'channel-name',
                                                            'channel-duration',
                                                            'tvg-id',
                                                            'tvg-name',
                                                            'tvg-language',
                                                            'tvg-country',
                                                            'tvg-logo',
                                                            'tvg-url',
                                                            'group-title',
                                                            'stream-url'])
                if df.empty:
                    print("The data frame is empty after parsing the m3u file!")
                    raise Exception
                print("The m3u file was successfully parsed!")
                return df
        except Exception as err:
            print("There was an error parsing the m3u file: {}".format(err))
            print("Will continue but data frame is None.")
            return None

    def search(self, dataframe, column, term):
        # Return True if there's at least one cell containing the term in the data frame
        try:
            sbool = dataframe[column].str.contains(term).any()
            if sbool:
                return True
            elif not sbool:
                return False
        except Exception as err:
            print("There was an error searching for the term {} on column {}. Error: {}".format(term, column, err))
            return False

    def template(self):
        # Create a template data frame with m3u column labels
        data = {
            "channel-content": [],
            "channel-name": [],
            "channel-duration": [],
            "tvg-id": [],
            "tvg-name": [],
            "tvg-language": [],
            "tvg-country": [],
            "tvg-logo": [],
            "tvg-url": [],
            "group-title": [],
            "stream-url": []
        }
        df = pandas.DataFrame(data)
        print("Empty data frame created.")
        return df

    def update(self,
               dataframe,
               channelid,
               channelname,
               channelcountry,
               channellogo,
               pipecmd,
               url):
        # Search and update a channel's info in the data frame
        try:
            # Find index that contains the channel ID under tvg-id
            target_index = dataframe.loc[dataframe["tvg-id"] == channelid].index

            # Do not override existing info from the m3u file, except for the stream url
            if dataframe.at[target_index[0], "tvg-name"]:
                channelname = dataframe.at[target_index[0], "tvg-name"]
            if dataframe.at[target_index[0], "tvg-country"]:
                channelcountry = dataframe.at[target_index[0], "tvg-country"]
            channellang = dataframe.at[target_index[0], "tvg-language"]
            channelepgurl = dataframe.at[target_index[0], "tvg-url"]
            channelgroup = dataframe.at[target_index[0], "group-title"]

            # Update individual cells from that row
            channelcontent = "#EXTINF:-1 " \
                             "tvg-id=\"{}\" " \
                             "tvg-name=\"{}\" " \
                             "tvg-language=\"{}\" " \
                             "tvg-country=\"{}\" " \
                             "tvg-logo=\"{}\" " \
                             "tvg-url=\"{}\" " \
                             "group-title=\"{}\"," \
                             "{}\n" \
                             "{} {}".format(channelid,
                                                      channelname,
                                                      channellang,
                                                      channelcountry,
                                                      channellogo,
                                                      channelepgurl,
                                                      channelgroup,
                                                      channelname,
                                                      pipecmd,
                                                      url)
            data = {
                "channel-content": channelcontent,
                "channel-name": channelname,
                "channel-duration": "-1",
                "tvg-id": channelid,
                "tvg-name": channelname,
                "tvg-language": channellang,
                "tvg-country": channelcountry,
                "tvg-logo": channellogo,
                "tvg-url": channelepgurl,
                "group-title": channelgroup,
                "stream-url": "{} {}".format(pipecmd, url)
            }
            dataframe.at[target_index[0], "tvg-name"] = data["channel-name"]
            dataframe.at[target_index[0], "tvg-language"] = data["tvg-language"]
            dataframe.at[target_index[0], "tvg-country"] = data["tvg-country"]
            dataframe.at[target_index[0], "tvg-logo"] = data["tvg-logo"]
            dataframe.at[target_index[0], "tvg-url"] = data["tvg-url"]
            dataframe.at[target_index[0], "group-title"] = data["group-title"]
            dataframe.at[target_index[0], "stream-url"] = data["stream-url"]
            boolean = True
            return dataframe, boolean
        except Exception as err:
            print("There was an error UPDATING the data frame. Error: {}".format(err))
            boolean = False
            return dataframe, boolean

    def write(self, dataframe):
        # Consolidate a m3u data frame to a .m3u file
        try:
            with open(self.outputm3u, "w") as f:
                f.write("#EXTM3U\n")
                for row in dataframe.itertuples(index=False):
                    channel_data = {
                        'channel-duration': row[dataframe.columns.get_loc("channel-duration")],
                        'tvg-id': row[dataframe.columns.get_loc("tvg-id")],
                        'tvg-name': row[dataframe.columns.get_loc("tvg-name")],
                        'tvg-language': row[dataframe.columns.get_loc("tvg-language")],
                        'tvg-country': row[dataframe.columns.get_loc("tvg-country")],
                        'tvg-logo': row[dataframe.columns.get_loc("tvg-logo")],
                        'tvg-url': row[dataframe.columns.get_loc("tvg-url")],
                        'group-title': row[dataframe.columns.get_loc("group-title")],
                        'channel-name': row[dataframe.columns.get_loc("channel-name")],
                        'stream-url': row[dataframe.columns.get_loc("stream-url")]
                    }
                    str_channel_data = str("#EXTINF:{} "
                                           "tvg-id=\"{}\" "
                                           "tvg-name=\"{}\" "
                                           "tvg-language=\"{}\" "
                                           "tvg-country=\"{}\" "
                                           "tvg-logo=\"{}\" "
                                           "tvg-url=\"{}\" "
                                           "group-title=\"{}\","
                                           "{}\n"
                                           "{}\n").format(channel_data["channel-duration"],
                                                          channel_data["tvg-id"],
                                                          channel_data["tvg-name"],
                                                          channel_data["tvg-language"],
                                                          channel_data["tvg-country"],
                                                          channel_data["tvg-logo"],
                                                          channel_data["tvg-url"],
                                                          channel_data["group-title"],
                                                          channel_data["channel-name"],
                                                          channel_data["stream-url"])
                    f.write(str_channel_data)
                print("Data frame was successfully exported to {}!".format(self.outputm3u))
        except Exception as err:
            print("There was an error writing the data frame to the m3u file. Error: {}".format(err))
