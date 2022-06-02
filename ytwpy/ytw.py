#!/usr/bin/env python
from youtubesearchpython import VideosSearch
from youtubesearchpython import PlaylistsSearch
from youtubesearchpython import ChannelsSearch
from youtubesearchpython import Playlist
import sys
import subprocess
from yt_dlp import YoutubeDL
import argparse
from pyfzf.pyfzf import FzfPrompt
from typing import List


fzf = FzfPrompt()

def PlayinMPV(
    urlstrings,
    formatstring,
    mpv="mpv",
    cplayerMode=False,
    loopFile=True,
    loopTimes=None,
    startNewSession=True,
):
    try:
        opencmd = [mpv, f"--ytdl-format={formatstring}"] + urlstrings
        if cplayerMode == False:
            opencmd.append("--player-operation-mode=pseudo-gui")
        else:
            opencmd.append("--player-operation-mode=cplayer")
        if loopFile == True:
            opencmd.append("--loop-file=inf")
        elif loopTimes != None:
            opencmd.append(f"--loop-file={loopTimes}")
        if startNewSession == False or cplayerMode == True:
            print("command: ", opencmd)
            process = subprocess.Popen(opencmd, stdout=sys.stdout, stderr=sys.stderr)
            process.communicate()
        else:
            print("command: ", opencmd)
            subprocess.Popen(opencmd, start_new_session=True)
    except Exception as e:
        print("Error Playing Media in mpv: ", e)
        sys.exit(1)

def WriteToFile(urlstrings,filename):
    with open(filename, 'w') as outfile:
        outfile.write("\n".join(urlstrings))

def YtdlDownload(urlstrings, formatstring):
    try:
        ydl_opts = {"format": formatstring}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(urlstrings)
    except Exception as e:
        print("Error Downloading Media: ", e)
        sys.exit(1)

def YtdlFormat(urlstrings) -> str:
    try:
        ydl_opts = {"listformats": True}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(urlstrings[0])
        formatchoice = input("Enter Format> ")
        return formatchoice
    except Exception as e:
        print("Error Listing Formats of Media: ", e)
        sys.exit(1)


class YtSearch:
    def __init__(self, vidsearchquery, result=None) -> None:
        self.vidsearchquery = vidsearchquery
        self.result = result
        self.videosSearch = VideosSearch(self.vidsearchquery)

    def selectVid(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("quit")
            totalres.append("next")
            totalres.append("search again")
            ind = 0
            for eachres in self.videosSearch.result().get("result"):
                currentres = f'{str(eachres.get("title"))}  {str(eachres.get("duration"))} {str(eachres.get("viewCount").get("short"))} {str(eachres.get("channel").get("name"))}'
                resultdict[currentres] = {"url":f"https://www.youtube.com/watch?v={str(eachres.get('id'))}","ind":ind}
                totalres.append(currentres)
                ind+=1

            if (
                isinstance(self.result, int)
                and self.result >= 0
                and self.result < len(totalres)
            ):
                for _, value in resultdict.items():
                    if value.get("ind") == self.result:
                        return [value.get("url")]

            vidchoice=fzf.prompt(totalres, '--multi')
            if vidchoice:
                if "next" in vidchoice:
                    print("Fetching Next Page")
                    self.videosSearch.next()
                    return self.selectVid()
                elif "quit" in vidchoice:
                    sys.exit(0)
                elif "search again" in vidchoice:
                    vidsearchquery = input("Enter Search Query> ")
                    return YtSearch(vidsearchquery,self.result).selectVid()
                else:
                    return [ val.get("url") for key,val in resultdict.items() if key in vidchoice]
            else:
                sys.exit(0)
        except Exception as e:
            print("Error Searching YouTube: ", e)
            sys.exit(1)

    @staticmethod
    def search(query: str, result=None) -> List[str]:
        return YtSearch(query, result).selectVid()

    

def mainfunction():
    try:
        # argparse
        parser = argparse.ArgumentParser(
            prog="ytw",
            description="Search,Play and Download from Youtube/yt-dlp supported sites",
        )
        parser.add_argument(
            "-f", "--format", type=str, nargs="?", help="Desired Format"
        )
        parser.add_argument(
            "-m",
            "--mpv",
            type=str,
            nargs="?",
            help="Custom Path of mpv and Arguments to it",
        )
        parser.add_argument(
            "--write",
            type=str,
            nargs="?",
            help="Write URLs to File",
        )
        parser.add_argument("-q", "--query", nargs="?", help="Search Query")
        parser.add_argument("-u", "--url", nargs="?", help="URL")
        parser.add_argument(
            "-d", "--download", help="Download Instead of Play", action="store_true"
        )

        parser.add_argument("-l", "--loop", help="Loop Playing", action="store_true")
        parser.add_argument("-t", "--looptimes", help="Loop x times", type=int)
        parser.add_argument("-r", "--result", help="Pick x-th result", type=int)
        parser.add_argument(
            "-b",
            "--best",
            help="Best Format",
            action="store_true",
        )
        parser.add_argument(
            "-w", "--watch", nargs="?", help="Watch Quality (360,480,720,1080)"
        )
        parser.add_argument("-a", "--audio", help="Play Audio", action="store_true")
        parser.add_argument(
            "-c", "--cplayer", help="Use cplayer mode of mpv", action="store_true"
        )
        parser.add_argument(
            "-s",
            "--samesession",
            help="Don't setsid player (Don't use start_new_session in subprocess)",
            action="store_true",
        )
        args = parser.parse_args()

        # get url of media
        yurl = ""
        if args.url != None:
            yurl = args.url
        elif args.query != None:
            yurl = YtSearch.search(args.query, args.result)
        else:
            vidsearchquery = input("Enter Search Query> ")
            yurl = YtSearch.search(vidsearchquery, args.result)

        # mpv path/args
        mpv = "mpv"
        if args.mpv != None:
            mpv = args.mpv

        # Format
        frmtstr = ""
        if args.format != None:
            frmtstr = args.format
        elif args.best == True:
            frmtstr = "bestvideo+bestaudio"
        elif args.audio == True:
            frmtstr = "bestaudio"
        elif args.watch != None:
            frmtstr = f"bestvideo[height<={args.watch}]+bestaudio"
        else:
            frmtstr = YtdlFormat(yurl)

        # startNewSession
        sns = True
        if args.samesession == True:
            sns = False

        # Download or Play
        if args.write != None:
            WriteToFile(yurl,args.write)
        elif args.download == True:
            YtdlDownload(yurl, frmtstr)
        else:
            PlayinMPV(
                yurl,
                frmtstr,
                mpv=mpv,
                loopFile=args.loop,
                loopTimes=args.looptimes,
                cplayerMode=args.cplayer,
                startNewSession=sns,
            )

    except Exception as e:
        print("Error: ", e)
        sys.exit(0)

if __name__ == "__main__":
    mainfunction()
