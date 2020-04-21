import re
import pandas


class M3uHandler:

    def __init__(self, inputfile, outputfile):
        self.inputfile = inputfile
        self.outputfile = outputfile

    def parse(self):
        # Define regex dictionary for iptv m3u files
        rx_dict = {
            'header_m3u': re.compile(
                r"^\#EXTM3U",
                re.IGNORECASE | re.VERBOSE
            ),
            'header_extinf': re.compile(
                r"^\#EXTINF",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'header_others': re.compile(
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
        # TODO: Validate m3u file before parsing it
        # Writes m3u file to a data frame
        try:
            with open(self.inputfile, 'r') as f:
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
                    print("Empty DataFrame. The script was unable to parse anything from the file.")
                    return None
                return df
        except Exception as err:
            print("There was an error parsing the m3u file: {}".format(err))
            print("Assuming Empty DataFrame.")
            return None

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
        return df

    def append(self,
               dataframe,
               channelid,
               channelname,
               channelcountry,
               channellogo,
               pathbash,
               pathsh,
               url):
        df = dataframe
        channelcontent = "#EXTINF:-1 " \
                         "tvg-id=\"{}\" " \
                         "tvg-name=\"{}\" " \
                         "tvg-language=\"\" " \
                         "tvg-country=\"{}\" " \
                         "tvg-logo=\"{}\" " \
                         "tvg-url=\"\" " \
                         "group-title=\"\"," \
                         "{}\n" \
                         "pipe://{} {} {}".format(channelid,
                                                  channelname,
                                                  channelcountry,
                                                  channellogo,
                                                  channelname,
                                                  pathbash,
                                                  pathsh,
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
            "stream-url": "pipe://{} {} {}".format(pathbash, pathsh, url)
        }
        # Append stream data to data frame
        try:
            df = df.append(data, ignore_index=True)
            return df
        except Exception as err:
            print("There was an error appending data to data frame. Error: {}".format(err))
            return None

    def write(self, dataframe):
        # Uses a data frame to output a m3u file
        try:
            with open(self.outputfile, "w") as f:
                f.write("#EXTM3U\n")
                for row in range(dataframe.shape[0]):
                    channel_data = {
                        'channel-duration': dataframe.ix[row, "channel-duration"],
                        'tvg-id': dataframe.ix[row, "tvg-id"],
                        'tvg-name': dataframe.ix[row, "tvg-name"],
                        'tvg-language': dataframe.ix[row, "tvg-language"],
                        'tvg-country': dataframe.ix[row, "tvg-country"],
                        'tvg-logo': dataframe.ix[row, "tvg-logo"],
                        'tvg-url': dataframe.ix[row, "tvg-url"],
                        'group-title': dataframe.ix[row, "group-title"],
                        'channel-name': dataframe.ix[row, "channel-name"],
                        'stream-url': dataframe.ix[row, "stream-url"]
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
                    # TODO: Validate the output before appending data to it
                    f.write(str_channel_data)
                print("Data frame successfully written to {}!".format(self.outputfile))
                return True
        except Exception as err:
            print("There was an error while working with the m3u file. Error: {}".format(err))
            print("Assuming nothing was written to {}.".format(self.outputfile))
            return False
