from lib.m3uhandler import M3uHandler
from lib.youtubehandler import YoutubeHandler
from argparse import ArgumentParser
# from pathlib import Path


def cli():
    ap = ArgumentParser()
    ap.add_argument("--apikey",
                    type=str,
                    required=True,
                    help="API KEY to use the Youtube API.")
    ap.add_argument("--apiurl",
                    type=str,
                    default="https://www.googleapis.com/youtube/v3/",
                    required=False,
                    help="Base URL of the Youtube API. Default is the Youtube API v3.")
    ap.add_argument("--channelid",
                    required=False,
                    type=str,
                    help="ID of a channel with a live-stream.")
    ap.add_argument("--channellogo",
                    required=False,
                    type=str,
                    help="URL of the channel's LOGO.")
    ap.add_argument("--channelname",
                    required=True,
                    type=str,
                    help="NAME of the channel with a live-stream.")
    ap.add_argument("--channelurl",
                    required=False,
                    type=str,
                    help="The URL of a channel with a live-stream.")
    ap.add_argument("--inputfile",
                    required=False,
                    type=str,
                    help="/path/to/input_playlist.m3u")
    ap.add_argument("--outputfile",
                    required=False,
                    default="output.m3u",
                    type=str,
                    help="/path/to/output.m3u. Default is output.m3u.")
    ap.add_argument("--pathbash",
                    required=False,
                    default="/bin/bash",
                    type=str,
                    help="Absolute /path/to/bash. Default is /bin/bash.")
    ap.add_argument("--pathstreamlinksh",
                    required=False,
                    default="/opt/youtubelivem3u/streamlink.sh",
                    type=str,
                    help="Absolute /path/to/streamlink.sh. Default is /opt/youtubelivem3u/streamlink.sh.")
    return vars(ap.parse_args())


# def os_path():
#    folder = Path().parent.absolute()
#    return folder


def main():
    # YOUTUBE API HANDLER
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

    # M3U HANDLER
    m3u = M3uHandler(args_cli["inputfile"],
                     args_cli["outputfile"])
    # Parse existing input m3u file
    if args_cli["inputfile"]:
        print("[INFO] User provided an input M3U playlist at {}.  "
              "Will try to parse it and create a data frame...".format(args_cli["inputfile"]))
        m3u_df = m3u.parse()
        if m3u_df is None:
            print("[INFO] Generating an empty data frame...")
            m3u_df = m3u.template()
    # Else, create a template data frame
    elif not args_cli["inputfile"]:
        print("[INFO] Did not find an input M3U playlist.  "
              "Generating an empty data frame...")
        m3u_df = m3u.template()
    # Append or update data frame
    if m3u_df.empty:
        print("[INFO] Appending stream info to data frame...")
        m3u_df = m3u.append(m3u_df,
                            args_cli["channelid"],
                            args_cli["channelname"],
                            stream["region"],
                            args_cli["channellogo"],
                            args_cli["pathbash"],
                            args_cli["pathstreamlinksh"],
                            stream["url"])
    elif not m3u_df.empty:
        # Check if the channel id exists in the data frame
        channelsearch = m3u.search(m3u_df, "tvg-id", args_cli["channelid"])
        if channelsearch:
            print("[INFO] Found the same channel on {}. "
                  "Will try to update its info to {}...".format(args_cli["inputfile"], args_cli["outputfile"]))
            m3u_df = m3u.update(m3u_df,
                                args_cli["channelid"],
                                args_cli["channelname"],
                                stream["region"],
                                args_cli["channellogo"],
                                args_cli["pathbash"],
                                args_cli["pathstreamlinksh"],
                                stream["url"])
            if m3u_df is None:
                print("[INFO] Will now try to append the channel info to {}...".format(args_cli["outputfile"]))
                m3u_df = m3u.append(m3u_df,
                                    args_cli["channelid"],
                                    args_cli["channelname"],
                                    stream["region"],
                                    args_cli["channellogo"],
                                    args_cli["pathbash"],
                                    args_cli["pathstreamlinksh"],
                                    stream["url"])
        elif not channelsearch:
            print("[INFO] Did not find the same channel on {}. "
                  "Will append the channel info to {}...".format(args_cli["inputfile"], args_cli["outputfile"]))
            m3u_df = m3u.append(m3u_df,
                                args_cli["channelid"],
                                args_cli["channelname"],
                                stream["region"],
                                args_cli["channellogo"],
                                args_cli["pathbash"],
                                args_cli["pathstreamlinksh"],
                                stream["url"])
    # Consolidate m3u data frame to a .m3u file
    m3u.write(m3u_df)
    m3u.export_csv(m3u_df)
    print("We're all done here. Bye!")
    exit()


if __name__ == "__main__":
    args_cli = cli()
    main()
