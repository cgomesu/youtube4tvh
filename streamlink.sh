#!/bin/bash
####################################################
################ Streamlink script #################
####################################################
# The default version writes the data from the best
# stream ($1, the first argument) to stdout using a
# thread pool of size 2 to download HLS segments.
# Everything else follows default values.
#
# Inspired by niwi_niwi's post at
# https://tvheadend.org/boards/5/topics/35658
#
# More info: https://streamlink.github.io/cli.html
#
####################################################
#### Add/modify script according to your needs #####
streamlink \
--stdout \
--hls-segment-threads 4 \
--hls-live-edge 10 \
"$1" best
