#!/usr/bin/env python
from youtubesearchpython import VideosSearch
import sys
import subprocess
from yt_dlp import YoutubeDL
import argparse


class colors:
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ENDC = "\033[0m"


def PlayinMPV(
    urlstring,
    formatstring,
    mpv="mpv",
    cplayerMode=False,
    loopFile=True,
    loopTimes=None,
    startNewSession=True,
):
    try:
        opencmd = [mpv, f"--ytdl-format={formatstring}", urlstring]
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


def YtdlDownload(urlstring, formatstring):
    try:
        ydl_opts = {"format": formatstring}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([urlstring])
    except Exception as e:
        print("Error Downloading Media: ", e)
        sys.exit(1)


def YtdlFormat(urlstring) -> str:
    try:
        ydl_opts = {"listformats": True}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([urlstring])
        formatchoice = input("Enter Format: ")
        return formatchoice
    except Exception as e:
        print("Error Listing Formats of Media: ", e)
        sys.exit(1)


class YtSearch:
    def __init__(self, vidsearchquery, result=None) -> None:
        self.vidsearchquery = vidsearchquery
        self.videosSearch = VideosSearch(vidsearchquery)
        self.result = result

    def selectVid(self) -> str:
        try:
            totalres = []
            ind = 0
            for eachres in self.videosSearch.result().get("result"):
                eachresdictobj = {
                    "title": str(eachres.get("title")),
                    "duration": str(eachres.get("duration")),
                    "views": str(eachres.get("viewCount").get("short")),
                    "channel": str(eachres.get("channel").get("name")),
                    "urllink": f"https://www.youtube.com/watch?v={str(eachres.get('id'))}",
                }
                totalres.append(eachresdictobj)
                print(
                    f'{colors.BLUE}{ind} {colors.CYAN}{eachresdictobj.get("title")} {colors.BLUE}{eachresdictobj.get("duration")} {colors.MAGENTA}{eachresdictobj.get("views")} {colors.GREEN}{eachresdictobj.get("channel")}{colors.ENDC}'
                )
                ind += 1

            if (
                isinstance(self.result, int)
                and self.result >= 0
                and self.result < len(totalres)
            ):
                return totalres[self.result].get("urllink")

            vidchoice = input(
                "Enter choice (type 'n'/'next' to fetch next page and 'q'/'quit' to quit):\n"
            )
            if vidchoice == "next" or vidchoice == "n":
                print("Fetching Next Page")
                self.videosSearch.next()
                return self.selectVid()
            elif vidchoice == "quit" or vidchoice == "q":
                sys.exit(0)
            else:
                return totalres[int(vidchoice)].get("urllink")
        except Exception as e:
            print("Error Searching YouTube: ", e)
            sys.exit(1)

    @staticmethod
    def search(query: str, result=None) -> str:
        return YtSearch(query, result).selectVid()


if __name__ == "__main__":
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
            vidsearchquery = input("Enter Search Query: ")
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
        if args.download == True:
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
