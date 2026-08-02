import socket
import struct
import hashlib
import sys

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

def downloadPiece(sock: socket.socket, torrent, pieceIndex: int) -> bytes:
    """Request every block of a piece from an already unchoked peer, 
    reassemble the piece data and then verify this piece's hash with the expected
    hash for that piece"""

    numPieces = (torrent.length + torrent.pieceLength -1)//torrent.pieceLength #calculate pieceLength, total length of the piece and round up in case it each part is not equal size
    if int(pieceIndex) == numPieces-1: #if it's the last one
        currentPieceLength = torrent.length - (int(pieceIndex) * torrent.pieceLength) #calculate length of last piece which is likely to be smaller thatn pieceLength which is how long the other pieces before this are likely to be
    else:
        currentPieceLength = torrent.pieceLength #if it's not the last piece, then the length is just pieceLength
    #this makes sure we can handle different piece lengths and our program doesn't crash/work incorrectly if we have a piece length shorter than every other piece

    arrayOfBytes = bytearray() #empty now but will be used to hold data we receive after sending requests
    subPieceSize = 16384
    for i in range(0, currentPieceLength, subPieceSize): #loop through the piece and go in chunks of 16384 since each sub piece of the piece is this size, all until we have all subpieces comprising the entire piece
        pieceIndex = pieceIndex 
        currentSubPieceLength = min(subPieceSize, currentPieceLength-i) #would be 16384 but in the case that we reach the last subpiece and it has a size less that 16384, we have to be able to handle it
        requestToSend = struct.pack(">IBIII", 13, 6, int(pieceIndex), i, currentSubPieceLength) #these are the parameters of our request message
        #1. 13 for length excluding prefix, 2. 6 for message id being 6, 3. pieceIndex for what piece we want, 4. i represents our offset as we move through the piece, 5.currentSubPieceLength for how much data to take from our current offset(usually 16384 unless the last subPiece is smaller)
        sock.sendall(requestToSend) #request for subpiece sent
        subPiecePrefix = sock.recv(4) #receive 4byte prefix
        if not subPiecePrefix:
            break
        subPieceLength = int.from_bytes(subPiecePrefix, byteorder="big") #convert to int for length
        subPiece = b""
        while len(subPiece) < subPieceLength: 
            packet = sock.recv(subPieceLength - len(subPiece)) #keep getting data until we match the length
            if not packet:
                break
            subPiece += packet
        #while loop gets data until we've matched the length the subPiece is supposed to be
        if subPiece and subPiece[0] == 7:
            subPiecePayload = subPiece[9:] #get actual data of subpiece
            arrayOfBytes.extend(subPiecePayload) #add actual data to continuous array
        #now have continous array of bytes representing data in the piece

    hashOfData = hashlib.sha1(arrayOfBytes).digest()
    expectedHash = torrent.pieceHashes[pieceIndex] #get the expected hash for the piece
    if (hashOfData == expectedHash): #final check where we compare our data's hash to the piece's hash that we were already given
        return arrayOfBytes
    else:
        raise ValueError(f"Hash mismatch, hashes do not match")
   