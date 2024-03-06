from ipaddress import ip_address
class Peer:
    def __init__(self) -> None:
        self.ip=""
        self.port=0

    def fromTorrentFormat(bitEncoded):
        p = Peer()
        p.ip=str(ip_address(bitEncoded[:4]))
        p.port=int.from_bytes(bitEncoded[4:], "big")
        return p
    
        #old working code qua sotto

        p = Peer()
        ip1 = int(bitEncoded[0])
        ip2 = int(bitEncoded[1])
        ip3 = int(bitEncoded[2])
        ip4 = int(bitEncoded[3])
        p.ip=f"{ip1}.{ip2}.{ip3}.{ip4}"
        p.port=int.from_bytes(bitEncoded[4:], "big")
        return p

    def toTorrenFormat(self):
        encStr=b''

        #ip
        #ipParts = self.ip.split(".")
        #for ipPart in ipParts:
        #    encStr+=int(ipPart).to_bytes(1, byteorder='big')

        #parte sopra commentata è la stessa cosa di questa qua sotto
        encStr += ip_address(self.ip).packed


        #port
        encStr+=self.port.to_bytes(2, byteorder='big')
        
        return encStr

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __value: object) -> bool:
        return self.ip == __value.ip and self.port==__value.port
