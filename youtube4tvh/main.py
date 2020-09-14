#!/usr/bin/python3
# Purpose:      Save a Youtube live-stream to an M3U playlist
# Author:       cgomesu
# Date:         September 11th, 2020
# Disclaimer:   Use at your own discretion.
#               Be mindful of the API daily quota.
#               The author does not provide any sort warranty whatsoever.

from lib.m3uhandler import M3uHandler
from lib.youtubehandler import YoutubeHandlerAPI, YoutubeHandlerNoAPI
from argparse import ArgumentParser


def cli():
    ap = ArgumentParser()
    ap.add_argument('--apikey',
                    type=str,
                    required=False,
                    help='your API KEY to use the Youtube API. '
                         'see https://developers.google.com/youtube/v3/getting-started.')
    ap.add_argument('--apiurl',
                    type=str,
                    default='https://www.googleapis.com/youtube/v3/',
                    required=False,
                    help='base URL of the Youtube API. default uses the Youtube API v3.')
    ap.add_argument('--channelid',
                    required=False,
                    type=str,
                    help='for --mode=add. the ID of a channel with a live-stream. '
                         'if not provided, obtained from a channel name query.')
    ap.add_argument('--channellogo',
                    required=False,
                    type=str,
                    help='for --mode=add. the URL of the channel\'s LOGO. '
                         'if the channel id is not provided, it will be obtained from a channel name query.')
    ap.add_argument('--channelname',
                    required=False,
                    type=str,
                    help='REQUIRED for --mode=add. the NAME of the channel with a live-stream.')
    ap.add_argument('--m3uinput',
                    required=False,
                    type=str,
                    help='REQUIRED for --mode=update. the /path/to/input.m3u. '
                         'used to import data from an existing m3u file.')
    ap.add_argument('--m3uoutput',
                    required=False,
                    default='output.m3u',
                    type=str,
                    help='the /path/to/output.m3u. default is output.m3u.')
    ap.add_argument('--mode',
                    choices=['add', 'update'],
                    type=str,
                    default='add',
                    required=False,
                    help='mode of execution. choose add or update. '
                         'mode=add will add a single channel to an m3u file (default). '
                         'mode=update will update the URL of multiple channels from an m3u file.')
    ap.add_argument('--pipecmd',
                    required=False,
                    default='pipe:///bin/bash /opt/youtube4tvh/streamlink.sh',
                    type=str,
                    help='the command to pipe data to a player/server. '
                         'for TVH and streamlink, it is pipe:///path/to/bash /path/to/streamlink.sh, for example. '
                         'default is \'pipe:///bin/bash /opt/youtube4tvh/streamlink.sh\'.')
    return vars(ap.parse_args())


def add_stream():
    # Create or append a live-stream to an m3u file
    if not args_cli['channelname']:
        print('[INFO] A channel name must be provided at the very least. See --help.  Bye!')
        exit()
    # YOUTUBE API HANDLER
    if args_cli['apikey']:
        youtube = YoutubeHandlerAPI(apiurl=args_cli['apiurl'],
                                    apikey=args_cli['apikey'],
                                    channelid=args_cli['channelid'],
                                    channelname=args_cli['channelname'],
                                    channellogo=args_cli['channellogo'])
    elif not args_cli['apikey']:
        youtube = YoutubeHandlerNoAPI(channelid=args_cli['channelid'],
                                      channelname=args_cli['channelname'],
                                      channellogo=args_cli['channellogo'])
    # Extract channel info
    if not args_cli['channelid']:
        print('[INFO] Retrieving channel info using the NAME provided...')
        args_cli['channelid'], args_cli['channellogo'] = youtube.find_chinfo()
    print('[INFO] Retrieving info from the channel\'s live-stream...')
    # Find info from the channel's live-stream
    stream = youtube.find_stream()
    if stream:
        # M3U HANDLER
        m3u = M3uHandler(args_cli['m3uinput'],
                         args_cli['m3uoutput'])
        m3u_parameters = {
            'channelid': args_cli['channelid'],
            'channelname': args_cli['channelname'],
            'channelcountry': stream['region'],
            'channellogo': args_cli['channellogo'],
            'pipecmd': args_cli['pipecmd'],
            'url': stream['url']
        }
        # Parse existing input m3u file
        if args_cli['m3uinput']:
            print('[INFO] User provided an input M3U playlist at {}.  '
                  'Will try to parse it and create a data frame...'.format(args_cli['m3uinput']))
            m3u_df = m3u.parse()
            if m3u_df is None:
                print('[INFO] Generating an empty data frame...')
                m3u_df = m3u.template()
        # Else, create a template data frame
        elif not args_cli['m3uinput']:
            print('[INFO] Did not find an input M3U playlist.  '
                  'Generating an empty data frame...')
            m3u_df = m3u.template()
        # Append or update data frame
        if m3u_df.empty:
            print('[INFO] Appending stream info to the data frame...')
            m3u_df = m3u.append(m3u_df, **m3u_parameters)
        elif not m3u_df.empty:
            # Check if the channel id exists in the data frame
            chbool = m3u.search(m3u_df, 'tvg-id', args_cli['channelid'])
            if chbool:
                print('[INFO] Found the same channel on {}. '
                      'Updating its url in the data frame...'.format(args_cli['m3uinput']))
                m3u_df, upboolean = m3u.update(m3u_df, **m3u_parameters)
                # Check if update() returned None owing to an error while updating channel data
                if not upboolean:
                    print('[INFO] It seems update() failed. '
                          'Will try to append the stream info to the data frame instead...')
                    m3u_df = m3u.append(m3u_df, **m3u_parameters)
            elif not chbool:
                print('[INFO] Did not find the same channel on {}. '
                      'Will append the stream info to the data frame...'.format(args_cli['m3uinput']))
                m3u_df = m3u.append(m3u_df, **m3u_parameters)
        # Consolidate m3u data frame to a .m3u file
        print('[INFO] Writing data frame to .m3u file...')
        m3u.write(m3u_df)
        print('[INFO] Done!')
    if not stream:
        print('[WARNING] Unable to retrieve data from channel \'{}\'.'.format(args_cli['channelname']))


def update_stream():
    # Update stream from a file
    if not args_cli['m3uinput']:
        print('[WARNING] An input m3u file is required to use this program in update mode. See --help.  Bye!')
        exit()
    # M3U HANDLER
    m3u = M3uHandler(args_cli['m3uinput'],
                     args_cli['m3uoutput'])
    # Parse user provided m3u file
    print('[INFO] User provided an input M3U playlist at {}.  '
          'Will try to parse it and create a data frame...'.format(args_cli['m3uinput']))
    m3u_df = m3u.parse()
    if m3u_df is None:
        # Unable to parse or empty file
        print('[WARNING] The data frame is empty. Unable to continue in update mode. Bye!')
        exit()
    names = m3u.extract_column(m3u_df, 'channel-name')
    if names is None:
        print('[WARNING] The list of channels is empty. Unable to continue in update mode. Bye!')
        exit()
    for channel in names:
        print('##############################################')
        print('[INFO] Updating channel: {}...'.format(channel))
        print('##############################################')
        args_cli['channelname'], args_cli['channelid'], args_cli['channellogo'] = channel, '', ''
        # TODO: improve the way errors are handled (retry then change request method)
        try:
            add_stream()
        except Exception:
            print('[WARNING] Error updating info from channel \'{}\''.format(channel))
            continue


def main():
    print('##############################################')
    print('[INFO] Running Youtube4TVH in \'{}\' mode.'.format(args_cli['mode']))
    print('##############################################')
    add_stream() if args_cli['mode'] == 'add' else update_stream()
    print('##############################################')
    print('[INFO] We are all done here. Bye!')
    print('##############################################')
    exit()


if __name__ == '__main__':
    args_cli = cli()
    main()
