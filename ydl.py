#!/usr/bin/env python
from youtubesearchpython import VideosSearch
from tabulate import tabulate
import sys
import subprocess
from yt_dlp import YoutubeDL
import argparse

MPV_COMMAND="mpv"

def PlayinMPV(urlstring,formatstring):
    process = subprocess.Popen([MPV_COMMAND,"--player-operation-mode=pseudo-gui",f"--ytdl-format={formatstring}",urlstring ],stdout=sys.stdout, stderr=sys.stderr)
    process.communicate()



def YtdlFormat(urlstring):
    ydl_opts = {'listformats':True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([urlstring])
    formatchoice = input("Enter Format: ")
    PlayinMPV(urlstring,formatchoice)
   
class YtSearch():
    def __init__(self,vidsearchquery) -> None:
        self.vidsearchquery = vidsearchquery
        self.videosSearch = VideosSearch(vidsearchquery)
    
    def selectVid(self) -> str:
        totalres = []
        tablelist = []
        for eachres in self.videosSearch.result().get("result"):
            eachresdictobj = {"title": str(eachres.get("title")) ,"duration": str(eachres.get("duration")) , "views": str(eachres.get("viewCount").get("short")) ,"channel":  str(eachres.get("channel").get("name")),"urllink": f"https://www.youtube.com/watch?v={str(eachres.get('id'))}"}
            totalres.append(eachresdictobj)
            tablelist.append([eachresdictobj.get("title"),eachresdictobj.get("duration"),eachresdictobj.get("views"),eachresdictobj.get("channel")])

        print(tabulate(tablelist,showindex="always"))
        vidchoice = input("Enter choice: ")
        if vidchoice == "next" or vidchoice == "n":
            print("Fetching Next Page")
            self.videosSearch.next()
            return self.selectVid()
        elif vidchoice == "quit" or vidchoice == "q":
            sys.exit(0)
        else:
            return totalres[int(vidchoice)].get("urllink")


def search():
    vidsearchquery = input("Enter: ")
    yotool=YtSearch(vidsearchquery)
    YtdlFormat(yotool.selectVid())



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="yotool",description='Search,Play and Download from Youtube/yt-dlp supported sites')
    parser.add_argument('-f','--format', type=str, nargs='?',help='Desired Format')
    parser.add_argument('-m','--mpvarg', type=str, nargs='?',help='Additional Argument that needs to be Passed to mpv')
    parser.add_argument('-y','--ytdlparg', type=str, nargs='?',help='Additional Argument that needs to be Passed to yt-dlp')
    parser.add_argument('-mp','--mpvpath', type=str, nargs='?',help='Custom Path of mpv')
    parser.add_argument('-u','--url', nargs='+', help='URLs')

    subparsers = parser.add_subparsers(title='subcommands',dest='subparser_name')
    searchcommand = subparsers.add_parser('search', aliases=['s'],help='Search Youtube')
    playcommand = subparsers.add_parser('play', aliases=['p'],help='Play Media')
    dlcommand = subparsers.add_parser('download', aliases=['d'],help='Download Media')


    args = parser.parse_args()
    print("Argument values:")
    print(args.mpvarg)
    print(args.ytdlparg)
    print(args.mpvpath)
    print(args.format)