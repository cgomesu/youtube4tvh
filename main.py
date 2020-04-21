from lib.m3uhandler import M3uHandler
from lib.youtubehandler import YoutubeHandler
import argparse


# Parse CLI arguments
parser_cli = argparse.ArgumentParser()
parser_cli.add_argument("--apikey",
                        type=str,
                        required=True,
                        help="API key to use the Youtube API.")
parser_cli.add_argument("--apiurl",
                        type=str,
                        default="https://www.googleapis.com/youtube/v3/",
                        required=False,
                        help="Base URL to the Youtube API. Default is the Youtube API v3.")
parser_cli.add_argument("--channelid",
                        required=False,
                        type=str,
                        help="The ID of a channel with a live-stream.")
parser_cli.add_argument("--channellogo",
                        required=False,
                        type=str,
                        help="The URL of the channel's LOGO.")
parser_cli.add_argument("--channelname",
                        required=True,
                        type=str,
                        help="The NAME of the channel with a live-stream.")
parser_cli.add_argument("--channelurl",
                        required=False,
                        type=str,
                        help="The URL of a channel with a live-stream.")
parser_cli.add_argument("--inputfile",
                        required=False,
                        type=str,
                        help="Add the /path/to/input_playlist.m3u")
parser_cli.add_argument("--outputfile",
                        required=False,
                        default="output.m3u",
                        type=str,
                        help="Add the /path/to/output.m3u. Default is output.m3u.")
parser_cli.add_argument("--pathbash",
                        required=False,
                        default="/bin/bash",
                        type=str,
                        help="Add the /path/to/bash. Default is /bin/bash.")
parser_cli.add_argument("--pathsh",
                        required=False,
                        default="/opt/youtubelivem3u/bash/streamlink.sh",
                        type=str,
                        help="Add the /path/to/streamlink.sh bash script. "
                             "Default is /opt/youtubelivem3u/bash/streamlink.sh.")
args_cli = vars(parser_cli.parse_args())


def main():
    # Youtube API handler
    youtube = YoutubeHandler(args_cli["apiurl"],
                             args_cli["apikey"],
                             args_cli["channelid"],
                             args_cli["channelurl"],
                             args_cli["channelname"],
                             args_cli["channellogo"])
    # Validate api key
    print("[INFO] Validating the Youtube API key...")
    if not youtube.validate_api():
        exit()
    # Find channel id
    if not args_cli["channelid"]:
        print("[INFO] Retrieving the channel ID using the channel NAME provided...")
        args_cli["channelid"] = youtube.find_id()
    # Find channel logo
    if not args_cli["channellogo"]:
        print("[INFO] Retrieving the URL of the channel's default logo...")
        args_cli["channellogo"] = youtube.find_logo()
    print("[INFO] Retrieving info from the channel's live-stream...")
    # Find info from the channel's live-stream
    stream = youtube.find_stream()

    # M3U handler
    m3u = M3uHandler(args_cli["inputfile"],
                     args_cli["outputfile"])
    # Parse existing input m3u file
    if args_cli["inputfile"]:
        print("[INFO] User provided an input M3U playlist at {}.  "
              "Will try to parse it and create a data frame...".format(args_cli["inputfile"]))
        m3u_df = m3u.parse()
        if m3u_df is None:
            m3u_df = m3u.template()
        # Search data frame for the same stream
        channelsearch = m3u.search()
        if channelsearch:
            print("[INFO] Found the same channel on {}. "
                  "Will try to update its info to {}...".format(args_cli["inputfile"], args_cli["outputfile"]))
            m3u_df = m3u.update(m3u_df,
                                channelsearch,
                                args_cli["channelid"],
                                args_cli["channelname"],
                                stream["region"],
                                args_cli["channellogo"],
                                args_cli["pathbash"],
                                args_cli["pathsh"],
                                stream["url"])
        elif not channelsearch:
            print("[INFO] Did not find the same channel on {}. "
                  "Will append the channel info to {}...".format(args_cli["inputfile"], args_cli["ouputtfile"]))
            m3u_df = m3u.append(m3u_df,
                                args_cli["channelid"],
                                args_cli["channelname"],
                                stream["region"],
                                args_cli["channellogo"],
                                args_cli["pathbash"],
                                args_cli["pathsh"],
                                stream["url"])
    # Else, create a template data frame
    elif not args_cli["inputfile"]:
        print("[INFO] Did not find an input M3U playlist.  "
              "Will create a template data frame...")
        m3u_df = m3u.template()
        m3u_df = m3u.append(m3u_df,
                            args_cli["channelid"],
                            args_cli["channelname"],
                            stream["region"],
                            args_cli["channellogo"],
                            args_cli["pathbash"],
                            args_cli["pathsh"],
                            stream["url"])

    # Write m3u data frame to a .m3u file
    m3u.write(m3u_df)
    print("We're all done here. Bye!")
    exit()


if __name__ == "__main__":
    main()
