from requests import get
from yt_dlp import YoutubeDL
import json

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

def search(arg):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(arg) 
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return video