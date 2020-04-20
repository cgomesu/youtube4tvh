import re
import pandas


class M3uHandler:
    def __init__(self, inputfile, outputfile, df):
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.df = df

    def parser(self):
        # define regex dictionary for m3u file
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
            'extinf_group_name': re.compile(
                r"group-name=\"(?P<extinf_group_name>.*?)\"",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            ),
            'stream_url': re.compile(
                r"^(?P<stream_url>(?!\#).*$)",
                re.IGNORECASE | re.MULTILINE | re.VERBOSE
            )
        }
        # TODO: Validate m3u file before parsing it
        # writes m3u file to a data frame
        try:
            with open(self.inputfile, 'r') as f:
                parsed_data = ((channel_content.group('channel_content'),
                                channel_name.group('channel_name'),
                                channel_duration.group('channel_duration'),
                                tvg_id.group('extinf_tvg_id'),
                                tvg_name.group('extinf_tvg_name'),
                                tvg_language.group('extinf_tvg_language'),
                                tvg_country.group('extinf_tvg_country'),
                                tvg_logo.group('extinf_tvg_logo'),
                                tvg_url.group('extinf_tvg_url'),
                                stream_url.group('stream_url'))
                               for channel_content in
                               rx_dict['channel_content'].finditer(f.read())
                               for channel_name in
                               rx_dict['channel_name'].finditer(channel_content.group('channel_content'))
                               for channel_duration in
                               rx_dict['channel_duration'].finditer(channel_content.group('channel_content'))
                               for tvg_id in rx_dict['extinf_tvg_id'].finditer(channel_content.group('channel_content'))
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
                               for stream_url in
                               rx_dict['stream_url'].finditer(channel_content.group('channel_content')))

                self.df = pandas.DataFrame(parsed_data, columns=['channel-content',
                                                                   'channel-name',
                                                                   'channel-duration',
                                                                   'tvg-id',
                                                                   'tvg-name',
                                                                   'tvg-language',
                                                                   'tvg-country',
                                                                   'tvg-logo',
                                                                   'tvg-url',
                                                                   'stream-url'])
                if self.df.empty:
                    print("Empty DataFrame. The script was unable to parse anything from the file.")
                    return None
                return self.df
        except Exception as err:
            print("There was an error parsing the m3u file: {}".format(err))
            exit()

    def writer(self):
        # Uses df to output a .m3u file
        try:
            for row in range(self.df.shape[0]):
                channel_data = {
                    'channel-duration': self.df.ix[row, "channel-duration"],
                    'tvg-id': self.df.ix[row, "tvg-id"],
                    'tvg-name': self.df.ix[row, "tvg-name"],
                    'tvg-language': self.df.ix[row, "tvg-language"],
                    'tvg-country': self.df.ix[row, "tvg-country"],
                    'tvg-logo': self.df.ix[row, "tvg-logo"],
                    'tvg-url': self.df.ix[row, "tvg-url"],
                    'group-title': self.df.ix[row, "group-title"],
                    'channel-name': self.df.ix[row, "channel-name"],
                    'stream-url': self.df.ix[row, "stream-url"]
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
                m3u_file = open(self.outputfile, "a")
                if row == 0:
                    m3u_file.write("#EXTM3U\n")
                else:
                    m3u_file.write(str_channel_data)
                m3u_file.close()
            return m3u_file
        except Exception as err:
            print("There was an error while working with the m3u file. Error: {}".format(err))

