# Youtube 4 tvh
Youtube4tvh is a non-interactive Python CLI program that uses Youtube API to 
find live-streams and create (or update) m3u playlists. The m3u file 
follows IPTV conventions that allow a TVHeadend (TVH) server to create an IPTV 
network with them, and each stream is piped into TVHeadend via a Streamlink 
(https://streamlink.github.io/) shell script.

# TVH layout
In general, this program is well suited for a TVH server that has the following
layout:

![TVH layout](img/tvhlayout.png)

That is, there's one or more client that accesses a single TVH server that reads 
an m3u playlist (youtubelive.m3u) that contains one or more muxes from Youtube 
live-streams. Such a playlist is generated and managed by the current Python 
program (youtube4tvh.py) and the live-streams are piped into the TVH server via 
Streamlink.

# Requirements
Python 3+

Python packages: Pandas (pandas), RegEx (re), and Requests (requests) is all
you need (see requirements.txt)

A valid Youtube API key (https://developers.google.com/youtube/v3/getting-started). 
Be mindful of your request quota daily limits.

# Status
```diff
- Working
- Last checked on: April 23rd 2020
```

# Installation
```diff
- Pending
```

# Usage
```diff
- Pending
```

# Examples
```diff
- Pending
```