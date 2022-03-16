<h1 align="center">ytwpy</h1> 
<p align="center">Search,Play and Download from Youtube/yt-dlp supported sites</p>
<hr>

## Installation
* Install Requirements of `ytwpy` first:
    * [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
    * [`youtube-search-python`](https://github.com/alexmercerind/youtube-search-python)
    * [`mpv`](https://mpv.io/)
    * [`ffmpeg`](https://ffmpeg.org/)
* You can then run the Python script found in this Repository.


## Usage

```bash
usage: ytw.py [-h] [-f [FORMAT]] [-m [MPV]] [-q [QUERY]] [-u [URL]] [-d] [-l]
           [-t LOOPTIMES] [-r RESULT] [-b] [-w [WATCH]] [-a] [-c] [-s]

Search,Play and Download from Youtube/yt-dlp supported sites

options:
  -h, --help            show this help message and exit
  -f [FORMAT], --format [FORMAT]
                        Desired Format
  -m [MPV], --mpv [MPV]
                        Custom Path of mpv and Arguments to it
  -q [QUERY], --query [QUERY]
                        Search Query
  -u [URL], --url [URL]
                        URL
  -d, --download        Download Instead of Play
  -l, --loop            Loop Playing
  -t LOOPTIMES, --looptimes LOOPTIMES
                        Loop x times
  -r RESULT, --result RESULT
                        Pick x-th result
  -b, --best            Best Format
  -w [WATCH], --watch [WATCH]
                        Watch Quality (360,480,720,1080)
  -a, --audio           Play Audio
  -c, --cplayer         Use cplayer mode of mpv
  -s, --samesession     Don't setsid player (Don't use start_new_session in
                        subprocess)
```

## License
[GPLv3](LICENSE)
