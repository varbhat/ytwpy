#!/usr/bin/env python
from youtubesearchpython import VideosSearch
from youtubesearchpython import PlaylistsSearch
from youtubesearchpython import ChannelsSearch
from youtubesearchpython import Playlist
from youtubesearchpython import Channel
from youtubesearchpython import playlist_from_channel_id
from youtubesearchpython import Search
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
        for item in urlstrings:
            outfile.write(f"{item}\n")

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
        formatchoice = input("Enter Format(type \"fetch\" to let yt-dlp fetch formats for you)> ")
        if formatchoice == "fetch":
            ydl_opts = {"listformats": True}
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(urlstrings[0])
            fc = input("Enter Format> ")
            return fc
        else:
            if formatchoice.startswith((' ', '\t')):
                return formatchoice.strip()
            elif formatchoice == "a" or formatchoice == "audio":
                return "bestaudio"
            else:
                return f"bestvideo[height<={formatchoice}]+bestaudio"
    except Exception as e:
        print("Error Listing Formats of Media: ", e)
        sys.exit(1)


class YtSearch:
    def __init__(self, vidsearchquery, result=None,searchtype="video") -> None:
        self.vidsearchquery = vidsearchquery
        self.result = result
        self.listofpls = []
        self.listofchanpls = []
        if searchtype == "video":
            self.videosSearch = VideosSearch(self.vidsearchquery)
        elif searchtype == "playlist":
            self.playlistsSearch = PlaylistsSearch(self.vidsearchquery)
        elif searchtype == "channel":
            self.channelsSearch = ChannelsSearch(self.vidsearchquery)
        elif searchtype == "all":
            self.allSearch = Search(self.vidsearchquery)

    def listVids(self,listofvids):
        try:
            totalres = []
            resultdict = {}
            totalres.append("quit")
            for eachresitem in listofvids:
                for eachres in eachresitem.get("videos"):
                    currentres = f'{str(eachres.get("title"))}  {str(eachres.get("duration"))}  {str(eachres.get("channel").get("name"))}'
                    resultdict[currentres] = str(eachres.get("link"))
                    totalres.append(currentres)

            vidchoice=fzf.prompt(totalres, '--multi')
            if vidchoice:
                if "quit" in vidchoice:
                    sys.exit(0)
                else:
                    return [ val for key,val in resultdict.items() if key in vidchoice]
            else:
                sys.exit(0)
        except Exception as e:
            print("Error listing Videos",e)
            sys.exit(1)

    def listVidfromPLs(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            for eachpl in self.listofpls:
                for eachres in eachpl.videos:
                    currentres = f'{str(eachres.get("title"))}  {str(eachres.get("duration"))}  {str(eachres.get("channel").get("name"))}'
                    resultdict[currentres] = str(eachres.get("link"))
                    totalres.append(currentres)

            vidchoice=fzf.prompt(totalres, '--multi')
            if vidchoice:
                if "next" in vidchoice:
                    for curPlaylist in self.listofpls:
                        if curPlaylist.hasMoreVideos:
                             curPlaylist.getNextVideos()
                    return self.listVidfromPLs()
                else:
                    return [ val for key,val in resultdict.items() if key in vidchoice]
            else:
                sys.exit(0)
        except Exception as e:
            print("Error listing Videos",e)
            sys.exit(1)

    def listChanPLs(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            for eachpl in self.listofchanpls:
                pls = eachpl.result["playlists"]
                for eachres in pls:
                    currentres = f'{str(eachres.get("title"))}  {str(eachres.get("videoCount"))}  {str(eachres.get("lastEdited"))}'
                    resultdict[currentres] = "https://www.youtube.com/playlist?list=" +str(eachres.get("id"))
                    totalres.append(currentres)

            vidchoice=fzf.prompt(totalres, '--multi')
            if vidchoice:
                if "next" in vidchoice:
                    for curChan in self.listofchanpls:
                        if curChan.has_more_playlists():
                             curChan.next()
                    return self.listChanPLs()
                else:
                    self.listofpls = [ Playlist(val) for key,val in resultdict.items() if key in vidchoice]
                    return self.listVidfromPLs()
            else:
                sys.exit(0)
        except Exception as e:
            print("Error listing Videos",e)
            sys.exit(1)  

    def selectVid(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            totalres.append("search again")
            ind = 0
            for eachres in self.videosSearch.result().get("result"):
                currentres = f'{str(eachres.get("title"))}  {str(eachres.get("duration"))} {str(eachres.get("viewCount").get("short"))} {str(eachres.get("channel").get("name"))}'
                resultdict[currentres] = {"url":str(eachres.get("link")),"ind":ind}
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

    def selectSearchAll(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            totalres.append("search again")
            ind = 0
            for eachres in self.allSearch.result().get("result"):
                currentres = ""
                curtype = eachres.get("type")
                if curtype == "channel":
                    currentres = f'(c) {str(eachres.get("title"))} {str(eachres.get("videoCount"))} | {str(eachres.get("subscribers"))}'
                elif curtype == "video":
                    currentres = f'(v) {str(eachres.get("title"))} {str(eachres.get("duration"))} {str(eachres.get("viewCount").get("short"))} {str(eachres.get("channel").get("name"))}'
                elif curtype == "playlist":
                    currentres = f'(p) {str(eachres.get("title"))}  {str(eachres.get("videoCount"))} {str(eachres.get("channel").get("name"))}'
                resultdict[currentres] = {"url":str(eachres.get("link")),"id":str(eachres.get("id")),"ind":ind,"type":curtype}
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
                    self.allSearch.next()
                    return self.selectSearchAll()
                elif "search again" in vidchoice:
                    vidsearchquery = input("Enter Search Query> ")
                    return YtSearch(vidsearchquery,self.result,"all").selectVid()
                else:
                    if len(vidchoice) == 1:
                        curType = resultdict[vidchoice[0]].get("type")
                        curURL = resultdict[vidchoice[0]].get("url")
                        if curType == "playlist":
                            selchoices = ["Play the Playlist","List Videos"]
                            selchoice = fzf.prompt(selchoices)
                            if selchoice[0] == selchoices[0]:
                                return [curURL]
                            else:
                                self.listofpls = []
                                self.listofpls.append(Playlist(curURL))
                                return self.listVidfromPLs()
                        elif curType == "channel":
                            curID = resultdict[vidchoice[0]].get("id")
                            selchoices = ["Play the Channel","List Videos","List Channel Playlists"]
                            selchoice = fzf.prompt(selchoices)
                            if selchoice[0] == selchoices[0]:
                                return [curID]
                            if selchoice[0] == selchoices[2]:
                                self.listofchanpls = []
                                self.listofchanpls.append(Channel(curID))
                                return self.listChanPLs()
                            else:
                                self.listofpls = []
                                self.listofpls.append(Playlist(playlist_from_channel_id(curID)))
                                return self.listVidfromPLs()
                        else:
                            return [curURL]
                    else:
                        return [ val.get("url") for key,val in resultdict.items() if key in vidchoice]
            else:
                sys.exit(0)
        except Exception as e:
            print("Error Searching YouTube1: ", e)
            sys.exit(1)

    def selectPL(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            totalres.append("search again")
            ind = 0
            for eachres in self.playlistsSearch.result().get("result"):
                currentres = f'{str(eachres.get("title"))}  {str(eachres.get("videoCount"))} {str(eachres.get("channel").get("name"))}'
                resultdict[currentres] = {"url": str(eachres.get("link")),"ind":ind}
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
                    self.playlistsSearch.next()
                    return self.selectPL()
                elif "search again" in vidchoice:
                    vidsearchquery = input("Enter Search Query> ")
                    return YtSearch(vidsearchquery,self.result,"playlist").selectPL()
                else:
                    listofplaylists = [ val.get("url") for key,val in resultdict.items() if key in vidchoice]
                    selchoices = ["Play the Playlist","List Videos"]
                    selchoice = fzf.prompt(selchoices)
                    if selchoice[0] == selchoices[0]:
                        return listofplaylists
                    else:
                        self.listofpls = []
                        for eachpl in listofplaylists:
                            self.listofpls.append(Playlist(eachpl))
                        return self.listVidfromPLs()
            else:
                sys.exit(0)
        except Exception as e:
            print("Error Searching YouTube Playlist: ", e)
            sys.exit(1)

    def selectChan(self):
        try:
            totalres = []
            resultdict = {}
            totalres.append("next")
            totalres.append("search again")
            ind = 0
            for eachres in self.channelsSearch.result().get("result"):
                currentres = f'{str(eachres.get("title"))}  {str(eachres.get("videoCount"))} | {str(eachres.get("subscribers"))}'
                resultdict[currentres] = {"url": str(eachres.get("link")),"id":str(eachres.get("id")),"ind":ind}
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
                    self.channelsSearch.next()
                    return self.selectChan()
                elif "search again" in vidchoice:
                    vidsearchquery = input("Enter Search Query> ")
                    return YtSearch(vidsearchquery,self.result,"channel").selectChan()
                else:
                    listofchans = [ val.get("id") for key,val in resultdict.items() if key in vidchoice]
                    selchoices = ["Play the Channel","List Videos","List Channel Playlists"]
                    selchoice = fzf.prompt(selchoices)
                    if selchoice[0] == selchoices[0]:
                        return [ val.get("url") for key,val in resultdict.items() if key in vidchoice]
                    if selchoice[0] == selchoices[2]:
                        self.listofchanpls = []
                        for eachchan in listofchans:
                            self.listofchanpls.append(Channel(eachchan))
                        return self.listChanPLs()
                    else:
                        self.listofpls = []
                        for eachpl in listofchans:
                            self.listofpls.append(Playlist(playlist_from_channel_id(eachpl)))
                        return self.listVidfromPLs()
            else:
                sys.exit(0)
        except Exception as e:
            print("Error Searching YouTube Channels: ", e)
            sys.exit(1)

    @staticmethod
    def search(query: str, result=None) -> List[str]:
        return YtSearch(query, result).selectVid()

    @staticmethod
    def searchpl(query: str, result=None) -> List[str]:
        return YtSearch(query, result,"playlist").selectPL()

    @staticmethod
    def searchchan(query: str, result=None) -> List[str]:
        return YtSearch(query, result,"channel").selectChan()

    @staticmethod
    def searchAll(query: str, result=None) -> List[str]:
        return YtSearch(query, result,"all").selectSearchAll()
    
   

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

        parser.add_argument(
             "--playlist", help="Search for Playlists", action="store_true"
        )
        parser.add_argument(
             "--channel", help="Search for Channels", action="store_true"
        )
        parser.add_argument(
             "--all", help="Search for Videos,Playlists and Channels", action="store_true"
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
            if args.all == True:
                yurl = YtSearch.searchAll(args.query,args.result)
            elif args.playlist == True:
                yurl = YtSearch.searchpl(args.query,args.result)
            elif args.channel == True:
                yurl = YtSearch.searchchan(args.query,args.result)
            else:
                yurl = YtSearch.search(args.query, args.result)
        else:
            if args.all == True:
               vidsearchquery = input("Search YouTube> ")
               yurl = YtSearch.searchAll(vidsearchquery,args.result) 
            elif args.playlist == True:
                vidsearchquery = input("Search YouTube Playlists> ")
                yurl = YtSearch.searchpl(vidsearchquery,args.result) 
            elif args.channel == True:
                vidsearchquery = input("Search YouTube Channels> ")
                yurl = YtSearch.searchchan(vidsearchquery,args.result)
            else:
                vidsearchquery = input("Search YouTube Videos> ")
                yurl = YtSearch.search(vidsearchquery, args.result)

        # mpv path/args
        mpv = "mpv"
        if args.mpv != None:
            mpv = args.mpv

        # Format
        frmtstr = ""

        # startNewSession
        sns = True
        if args.samesession == True:
            sns = False

        # Download or Play
        if args.write != None:
            WriteToFile(yurl,args.write)
        else:
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

if __name__ == "__main__":
    mainfunction()
