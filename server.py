#!/usr/bin/python
from flask import Flask
from flask import request
from tool import getMyIP,getServerList
from TrackerProxy import announce
from settings import serverListUrl
from Peer import Peer

app=Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True

serverList=[]


@app.route('/announce/')
def announce_proxy():
    query = request.query_string.decode()
    if query=='':
        return
    resp = announce(query,serverList)

    peer:Peer
    for peer in resp.peers:
        print(f"{peer.ip}:{peer.port}")
    print(resp)
    return resp.bencode()


    
    


@app.route("/<name>")
def test(name):
    return "this is a test code====="+name


@app.route("/ip")
def ip():
    return getMyIP()


if __name__ == "__main__":
    serverList=getServerList(serverListUrl)

    app.run(port=25565,host="0.0.0.0") #,host="10.12.4.53")