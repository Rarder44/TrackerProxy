from tool import getServerList
from settings import serverListUrl
from TrackerProxy import announce




serverList=[
    "udp://127.0.0.1:8000",
    "udp://tracker.opentrackr.org:1337/announce",
    "http://tracker.opentrackr.org:1337/announce",
    "http://bt.okmp3.ru:2710/announce",
    "http://bt1.archive.org:6969/announce"
    ]


serverList=[
    'https://tracker.tamersunion.org:443/announce',
    'https://tracker.gbitt.info:443/announce',
    'http://tracker.gbitt.info:80/announce'
    ]

serverList=getServerList(serverListUrl)

query="info_hash=K%cb%5c%19po%14%3d%f1%e0%82%c0%89T%0bZ%0d%a7%e9%f6&peer_id=-qB4520-!l9kgBnnfM3v&port=63038&uploaded=0&downloaded=0&left=16384&corrupt=0&key=67E45526&event=started&numwant=200&compact=1&no_peer_id=1&supportcrypto=1&redundant=0"

print(announce(query,serverList))

