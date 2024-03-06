from TrackerResponse import TrakerResponse
from UDPTrackerClient import TrackerClient
from tool import followUntilUDP,myQueryURLparse
from urllib.parse import unquote_to_bytes
import asyncio
from settings import HTTPtimeout

def announce(queryURLencoded, serverList):

    finalResponse:TrakerResponse= None
    for server in serverList:

        tr=None
        urlq=f"{server}?{queryURLencoded}"

        isUDP,data = followUntilUDP(urlq,HTTPtimeout)
        if isUDP:

            #DOC:
            #https://github.com/elektito/pybtracker
            #http://bittorrent.org/beps/bep_0015.html
            #https://wiki.theory.org/BitTorrentSpecification#Tracker_Request_Parameters

            #converto la richiesta urlencoded in una richiesta UDP 
            #{'info_hash': b'K\xcb\\\x19po\x14=\xf1\xe0\x82\xc0\x89T\x0bZ\r\xa7\xe9\xf6', 'peer_id': '-qB4520-!l9kgBnnfM3v', 'port': '63038', 'uploaded': '0', 'downloaded': '0', 'left': '16384', 'corrupt': '0', 'key': '67E45526', 'event': 'started', 'numwant': '200', 'compact': '1', 'no_peer_id': '1', 'supportcrypto': '1', 'redundant': '0'}

            res= myQueryURLparse(queryURLencoded)
            res["info_hash"]=unquote_to_bytes(res["info_hash"])
                
            #recupero i valori
            peerid=res["peer_id"].encode()

            eventMap={"none":0,"completed":1,"started":2,"stopped":3}
            try:
                eventid=eventMap[res["event"]]
            except:
                eventid=0

            #creo il client con il peerid passato
            client = TrackerClient(announce_uri=server,peerid=peerid,max_retransmissions=1)

            #ottengo i peer
            tr =  asyncio.run( client.announce(
                res["info_hash"],  # infohash
                int(res["downloaded"]),                   
                int(res["left"]),                    
                int(res["uploaded"]),                     
                eventid,                        
                int(res["numwant"]),                      
                port=int(res["port"])
            ))

        else:
            if data != None:
                d = data._content
                tr = TrakerResponse.parse(d)


        if tr == None:
            print(f"{server} error!")
            continue
        
        print(f"{server} ok! -> {tr}")
        if( finalResponse == None):
            finalResponse=tr
        else:
            finalResponse.merge(tr)

    return finalResponse