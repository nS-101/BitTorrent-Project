import socket

def handshake(torrent, peerIP: str, peerPort: int) -> tuple[socket.socket, bytes]:
    """Perform BitTorrent handshake with a peer. returns the open, connected socket for 
    reuse in case of more piece requests. also returns peer's 20byte peer ID"""

    protocolStringLength = 19
    protocolStringLength = protocolStringLength.to_bytes(1, byteorder="big") #convert 19 to bytes object
    protocolString = b"BitTorrent protocol"
    reservedBytes = b"\x00" * 8 #create 8 empty bytes
    peerID = b"\x10" * 20 #20 random bytes to send as ID
    #now have necessary info for the handshake
    continousBytes = b"".join([protocolStringLength, protocolString, reservedBytes, torrent.infoHash, peerID]) #string of bytes we send to peer

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((peerIP, peerPort)) #establish connection
    sock.sendall(continousBytes) #send bytes
    responseFromClient = sock.recv(68)
    clientPeerID = responseFromClient[48:] #take last 20 bytes since that's the peer ID, everything else is just the data I sent

    return sock, clientPeerID