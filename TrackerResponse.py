from __future__ import annotations
import bencodepy
from Peer import Peer
class TrakerResponse:
    #{b'complete': 2, b'downloaded': 30, b'incomplete': 3, b'interval': 1750, b'min interval': 875, b'peers': b'R0`<\xf6>\xae2\xd8Lp\xc5\xb8\x91f\x98v\xe0.\xf6z\xaeK\xf3-\x0e\xc1\xbfi\xcf'}
    
    def __init__(self) -> None:
        self.complete:int=0
        self.incomplete:int=0
        self.interval:int=0
        self.min_interval:int=0
        self.peers=[]
        
    def parse(bencodedResponse):

        try:
            decoded = bencodepy.decode(bencodedResponse)
            tr= TrakerResponse()
            tr.complete=decoded[b"complete"]
            tr.incomplete=decoded[b"incomplete"]
            tr.interval=decoded[b"interval"]
            tr.min_interval=decoded[b"min interval"]

            peersEnc = decoded[b"peers"]


            tr.peers = [Peer.fromTorrentFormat( peersEnc[i:i+6] ) for i in range(0, len(peersEnc), 6)]
            
            

            for i in range(0,len(peersEnc),6):      #6 step xke ci sono 4byte per l'ip e 2 per la porta per ogni peer
                peerEnc = peersEnc[i:i+6]
                tr.peers.append(Peer.fromTorrentFormat(peerEnc))   
            return tr
        
        except:
            return None
        
    def bencode(self):
        obj= {b'complete': self.complete, b'incomplete': self.incomplete, b'interval': self.interval, b'min interval': self.min_interval}
        obj[b'peers']=b''
        peer:Peer
        for peer in self.peers:
            obj[b'peers']+=peer.toTorrenFormat()

        return bencodepy.encode(obj)


    def merge(self,anotherResponse: TrakerResponse):
        #non posso sapere quanti sono completati e quanti incompleti... quindi prendo il maggiore...
        self.complete=max(self.complete,anotherResponse.complete)
        


        #intervall e min_intervall prendo il minimo
        self.interval=max(self.interval,anotherResponse.interval)
        self.min_interval=max(self.min_interval,anotherResponse.min_interval)

        #unisco i peer
        for peer in anotherResponse.peers:
            if peer not in self.peers:
                self.peers.append(peer)

        #calcolo gli incomplete 
        self.incomplete = len(self.peers)-self.complete


    def __str__(self) -> str:
        return f"complete: {self.complete} | incomplete: {self.incomplete} | peer: {len(self.peers)} | {self.peers}"
    
    def __repr__(self) -> str:
        return str(self) 
