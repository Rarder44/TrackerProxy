import asyncio
import os
import struct
import logging
import random
import cmd
import argparse
from urllib.parse import urlparse
from collections import defaultdict
from ipaddress import ip_address
from datetime import datetime, timedelta
from version import __version__
from TrackerResponse import TrakerResponse
from Peer import Peer
from settings import UDPtimeout

class ServerError(Exception):
    pass

class UdpTrackerClientProto(asyncio.Protocol):
    def __init__(self, client):
        self.client = client
        self.received_msg = None

        self.sent_msgs = {}
        self.logger = self.client.logger
        self.connection_lost_received = asyncio.Event()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.connection_lost_received.set()

    def datagram_received(self, data, addr):
        if len(data) < 8:
            self.logger.warning('Invalid datagram received.')
            return

        action, tid = struct.unpack('!II', data[:8])
        if tid in self.sent_msgs:
            self.received_msg = (action, tid, data[8:])
            self.sent_msgs[tid].set()
        else:
            self.logger.warning('Invalid transaction ID received.')

    def error_received(self, exc):
        self.logger.info('UDP client transmision error: {}'.format(exc))

    def get_tid(self):
        tid = random.randint(0, 0xffffffff)
        while tid in self.sent_msgs:
            tid = random.randint(0, 0xffffffff)
        self.sent_msgs[tid] = asyncio.Event()
        return tid

    async def send_msg(self, msg, tid):
        n = 0
        timeout = UDPtimeout   

        for i in range(self.client.max_retransmissions):
            try:
                self.transport.sendto(msg)
                await asyncio.wait_for(
                    self.sent_msgs[tid].wait(),
                    timeout=timeout)

                del self.sent_msgs[tid]
            except asyncio.TimeoutError:
                if n >= self.client.max_retransmissions - 1:
                    del self.sent_msgs[tid]
                    #raise TimeoutError('Tracker server timeout.')
                    return

                action = int.from_bytes(msg[8:12], byteorder='big')
                if action != 0: # if not CONNECT
                    delta = timedelta(seconds=self.client.connid_valid_period)
                    if self.client.connid_timestamp < datetime.now() - delta:
                        await self.connect()

                n += 1
                timeout = 15 * 2 ** n

                self.logger.info(
                    'Request timeout. Retransmitting. '
                    '(try #{}, next timeout {} seconds)'.format(n, timeout))
            else:
                return

    async def connect(self):
        self.logger.info('Sending connect message.')
        tid = self.get_tid()
        msg = struct.pack('!QII', 0x41727101980, 0, tid)
        await self.send_msg(msg, tid)
        if self.received_msg:
            action, tid, data = self.received_msg
            if action == 3:
                self.logger.warn('An error was received in reply to connect: {}'
                                 .format(data.decode()))
                self.client.connid = None
                raise ServerError(
                    'An error was received in reply to connect: {}'
                    .format(data.decode()))
            else:
                self.client.callback('connected')
                self.client.connid = int.from_bytes(data, byteorder='big')
                self.client.connid_timestamp = datetime.now()

            self.received_msg = None
        else:
            self.logger.info('No reply received.')

    async def announce(self, infohash, num_want, downloaded, left, uploaded,
                       event=0, ip=0,port=None):
        
        if not self.client.interval or not self.client.connid or \
           datetime.now() > self.client.connid_timestamp + \
           timedelta(seconds=self.client.connid_valid_period):
            # get a connection id first
            await self.connect()

            if not self.client.connid:
                self.logger.info('No reply to connect message.')
                return None

        self.logger.info('Sending announce message.')
        action = 1
        tid = self.get_tid()
        if port == None:
            port = self.transport._sock.getsockname()[1]

        key = random.randint(0, 0xffffffff)
        ip = int.from_bytes(ip_address(ip).packed, byteorder='big')

       
        msg = struct.pack('!QII20s20sQQQIIIIH', self.client.connid, action, tid,
                          infohash, self.client.peerid, downloaded, left,
                          uploaded, event, ip, key, num_want, port)
        await self.send_msg(msg, tid)
        if self.received_msg:
            action, tid, data = self.received_msg
            if action == 3:
                self.logger.warning('An error was received in reply to announce: {}'
                                    .format(data.decode()))
                raise ServerError(
                    'An error was received in reply to announce: {}'
                    .format(data.decode()))
            else:
                if len(data) < 12:
                    self.logger.warning('Invalid announce reply received. Too short.')
                    return None
                self.client.interval, leechers, seeders = struct.unpack('!III', data[:12])

            self.received_msg = None

            data = data[12:]
            if len(data) % 6 != 0:
                self.logger.warning(
                    'Invalid announce reply received. Invalid length.')
                return None

            peers = [data[i:i+6] for i in range(0, len(data), 6)]
            #peers = [(str(ip_address(p[:4])), int.from_bytes(p[4:], byteorder='big')) for p in peers]
            peers = [Peer.fromTorrentFormat( p) for p in peers]


            self.client.callback('announced', infohash, peers)
        else:
            peers = None
            self.logger.info('No reply received to announce message.')
            return None

        tr = TrakerResponse()
        tr.complete = seeders
        tr.incomplete=leechers
        tr.peers=peers

        return tr #peers,leechers,seeders

class TrackerClient:
    def __init__(self,
                 announce_uri,
                 max_retransmissions=8,
                 peerid=None):
        self.logger = logging.getLogger(__name__)

        scheme, netloc, _, _, _, _ = urlparse(announce_uri)
        if scheme != 'udp':
            raise ValueError('Tracker scheme not supported: {}'.format(scheme))
        if ':' not in netloc:
            self.logger.info('Port not specified in announce URI. Assuming 80.')
            tracker_host, tracker_port = netloc, 80
        else:
            tracker_host, tracker_port = netloc.split(':')
            tracker_port = int(tracker_port)

        self.server_addr = tracker_host, tracker_port
        self.max_retransmissions = max_retransmissions

        self.allowed_callbacks = ['connected', 'announced']
        self.connid_valid_period = 60
        self.callbacks = defaultdict(list)
        self.connid = None
        self.connid_timestamp = None
        self.interval = None
        self.peerid = peerid or os.urandom(20)

    def callback(self, cb, *args):
        if cb not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(cb))

        for c in self.callbacks[cb]:
            c(*args)

    def add_callback(self, name, func):
        if name not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(name))

        self.callbacks[name].append(func)

    def rm_callback(self, name, func):
        if name not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(name))

        self.callbacks[name].remove(func)

    async def start(self):
        self.transport, self.proto = await asyncio.get_running_loop().create_datagram_endpoint(lambda: UdpTrackerClientProto(self),remote_addr=self.server_addr)

    async def stop(self):
        self.transport.close()
        await self.proto.connection_lost_received.wait()

    async def announce(self, infohash, downloaded, left, uploaded, event,num_want=160,port=None):
        if not hasattr(self,"transport") or not hasattr(self,"proto"):
            await self.start()

        return await self.proto.announce(infohash, num_want, downloaded, left, uploaded, event,port=port)

    async def connect(self):
        return await self.proto.connect()

def hex_encoded_infohash(v):
    v = bytes.fromhex(v)
    if len(v) != 20:
        raise ValueError
    return v

class NiceArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        print('{}: error: {}'.format(self.prog, message))
        raise argparse.ArgumentError(None, message)

