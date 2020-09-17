#!/bin/bash
###################################################
################### VLC script ####################
###################################################
# This is an alternative bash script that uses VLC
# (https://github.com/videolan/vlc) to pipe data
# into a TVHeadend server.
#
# To use it, change the '--pipecmd' from
# 'pipe:///bin/bash /opt/youtube4tvh/streamlink.sh'
# to 'pipe:///bin/bash /opt/youtube4tvh/vlc.sh'.
#
# This will only work if VLC is able to extract
# the livestream URL from Youtube's website. You
# can test by running 'vlc URL', in which URL is a
# Youtube livestream URL. If that works, this script
# should also work. Otherwise, stick to streamlink.
#
# The default version writes the data from the
# stream ($1, the first argument) to stdout.
# Everything else follows default values.
#
# To transcode the stream before piping into
# TVH, add 'transcode{OPTIONS}' to '--sout'.
#
# More info: https://wiki.videolan.org.
# Last tested with: VLC v3.0.11 Vetinari
#
###################################################
#### Add/modify script according to your needs ####
vlc \
-I dummy \
--quiet \
--sout "#:std{access=file,mux=ts,dst=-}" \
"$1"
