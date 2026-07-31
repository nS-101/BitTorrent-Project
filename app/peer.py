import socket
import struct

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

def waitForUnchoke(sock: socket.socket) -> None:
    """After the handshake, exchange the messages needed before the peer will
    let us request necessary piece data: read the optional bitfield, send
    "interested", and then block until the peer sends us "unchoke"
    """
    sock.settimeout(2.0) #wait for max 2 seconds before moving on if connection not established
    try:
        bitFieldMessagePrefix = sock.recv(4) #receive 4byte prefix for bitfield message after handshake so we can determine the length of the entire bitfield message
        lengthOfBitfield = int.from_bytes(bitFieldMessagePrefix, byteorder="big") #convert prefix into int to determine full length of bitfield message
        bitFieldMessage = sock.recv(lengthOfBitfield) #get full bitfield message
        if bitFieldMessage[0] == 5: #ID byte for bitfield should be 5, since we already read the prefix, it starts after so we can use the zero index and the second recv call doesnt use the prefix
            bitFieldMessagePayload = bitFieldMessage[1:] #everything after the id byte is the payload
        #bitfield message received
    except socket.timeout:
        pass
    sock.settimeout(None) #reset
    #using try/except here for handling in case peer doesn't send bitfield first

    interestedMessage = struct.pack(">IB", 1, 2) #4byte integer for the prefix representing length 1 and a 1byte integer that represents id 2
    sock.sendall(interestedMessage) 
    #created and sent the interested message 

    unchokeMessagePrefix =  sock.recv(4) #receive 4byte prefix for unchoke message
    lengthOfUnchoke = int.from_bytes(unchokeMessagePrefix, byteorder="big") #convert bytes to int to determine full length of unchoke message
    unchokeMessage = sock.recv(lengthOfUnchoke)
    if unchokeMessage[0] == 1: #id for unchoke message is 1, we can use the zero index since because we already read the prefix, it doesn't get read again in this second recv call
        unchokeMessagePayload = unchokeMessage[1:] #payload is everything after id byte
    #received and read the unchoke message
