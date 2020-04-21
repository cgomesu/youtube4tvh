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
                        help="Add the /path/to/output_playlist.m3u")
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
        youtube.find_id()
    # Find channel logo
    if not args_cli["channellogo"]:
        print("[INFO] Retrieving the URL of the channel's default logo...")
        youtube.find_logo()
    print("[INFO] Retrieving info from the channel's live-stream...")
    # Find info from the channel's live-stream
    stream = youtube.find_stream()
    # TODO: Add m3u handler functions
    # TODO: Add or update stream info to the m3u file

    # M3U handler
    m3u = M3uHandler(args_cli["inputfile"],
                     args_cli["outputfile"])
    # Parse existing input m3u file
    if args_cli["inputfile"]:
        print("[INFO] Found an input M3U playlist at {}.  "
              "Will try to parse it and create a data frame...".format(args_cli["inputfile"]))
        m3u_df = m3u.parse()
        if m3u_df is None:
            m3u_df = m3u.template()
    # Else, create a template data frame
    elif not args_cli["inputfile"]:
        print("[INFO] Did not find an input M3U playlist.  "
              "Will create a template data frame...")
        m3u_df = m3u.template()
    print(m3u_df)
    exit()


if __name__ == "__main__":
    main()
