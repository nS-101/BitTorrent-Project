import argparse
import sys
import json
from bencode import decodeBencode, decodeBytesKeys
from torrent import Torrent
from tracker import getPeers 
from peer import downloadPiece, connectToPeer
#imported required methods, class, packages, files

def commandDecode(args):
    """Decode a raw bencoded value from the cli and print it as json"""
    bencodedVal = args.bencodedValue
    decodedValue = decodeBencode(bencodedVal.encode()) #convert to bytes before passing to decodeBencode since it accepts bytes but args isn't bytes
    decodedValue = decodeBytesKeys(decodedValue) #need to pass to decodeBytesKeys since json can't handle raw bytes, and this method already took care of that since this probleme existed before the code refactoring
    print(json.dumps(decodedValue))
    


def commandInfo(args):
    """Print's the torrent file's data: trackerURL, length, info hash, piece hashes"""
    torrent = Torrent.fromFile(args.torrentFile) #read file and get info using fromFile method

    print("TrackerURL:", torrent.announce.decode()) 
    print("Length:", torrent.length)
    print("Info Hash:", torrent.infoHash.hex())
    print("Piece Length:", torrent.pieceLength)
    print("Piece Hashes:")
    for hash in torrent.pieceHashes:
        print(hash.hex())

def commandPeers(args):
    """Get possible peers to connect to, prints out trackerURL's peer list"""
    torrent = Torrent.fromFile(args.torrentFile) #read file and get info using fromFile method

    listOfPeers = getPeers(torrent) 
    for data in listOfPeers:
        print(data) #print each tuple containing IP address and port number of each peer

def commandDownloadPiece(args):
    """Download a single piece from a .torrent file and save it to disk"""
    torrent = Torrent.fromFile(args.torrentFile) #read file and get info using fromFile method
    peers = getPeers(torrent) #get list of peers
    try:
        sock, peerID = connectToPeer(torrent, peers) #connectToPeer incorporates both the handshake and the unchoke protocols
    except RuntimeError:
        print(f"Runtime error ocurred, no peers successfully connected to while trying to download a piece")
        sys.exit(1) #gracefuly exit cli with clean error message instead of raised error
    pieceData = downloadPiece(sock, torrent, args.pieceIndex) 
    with open(args.output, "wb") as file:
        file.write(pieceData) #write piece to disk
    
def commandDownload(args):
    """Download an entire .torrent file by downloading every piece"""
    torrent = Torrent.fromFile(args.torrentFile) #read file and get info using fromFile method
    peers = getPeers(torrent) #get list of peers
    
    numOfPieces = len(torrent.pieceHashes) #length of pieceHashes is how many pieces there are since pieceHashes has the hash for every piece
    totalFile = bytearray() #create bytearray to hold entire file once all pieces are collected
    try:
        sock, peerID = connectToPeer(torrent, peers) #connectToPeer incorporates both the handshake and the unchoke protocols
    except RuntimeError:
        print(f"RunTime error ocurred, no peers successfully connected to while trying to download a file")
        sys.exit(1) #gracefully exit cli with clean error message instead of raised error
    for currentPieceIndex in range(numOfPieces):
        currentPieceData = downloadPiece(sock, torrent, currentPieceIndex) #send request for piece data
        totalFile.extend(currentPieceData)
    #all pieces collected in totalfile at this point

    with open(args.output, "wb") as file:
        file.write(totalFile) #write entire file


def main():
    parser = argparse.ArgumentParser(description="A BitTorrent client") #create parser object
    subparsers = parser.add_subparsers(dest="command", required=True) #create subparsers to pull commands like "info" or "peers", required means it crashes without it

    infoParser = subparsers.add_parser("info") #add info command
    infoParser.add_argument("torrentFile") #the .torrent file is the argument for the info command, first argument after the info command is stored as torrentFile
    infoParser.set_defaults(func=commandInfo) #use commandInfo method when info command is used

    peersParser = subparsers.add_parser("peers") #add peers command
    peersParser.add_argument("torrentFile") ##the .torrent file is the argument for the peers command, first argument after the peers command is stored as torrentFile
    peersParser.set_defaults(func=commandPeers) #use commandPeers method when peers command is used

    downloadPieceParser = subparsers.add_parser("download_piece") #add download_piece command
    downloadPieceParser.add_argument("torrentFile") #the .torrent file is the argument for the download_piece command, first argument after the download_piece command is stored as torrentFile
    downloadPieceParser.add_argument("pieceIndex", type=int) #download_piece also requires an int representing the piece index, second argument after the download_piece command is stored as pieceIndex
    downloadPieceParser.add_argument("-o", "--output", required=True) #other arguments needed for download_piece method
    downloadPieceParser.set_defaults(func=commandDownloadPiece) #use commandDownloadPiece method when download_piece command is used

    downloadParser = subparsers.add_parser("download") #add download command
    downloadParser.add_argument("torrentFile") #the .torrent file is the argument for the download command, first argument after the download command is stored as torrentFile
    downloadParser.add_argument("-o", "--output", required=True) #store file path for where to store data as output, is required
    downloadParser.set_defaults(func=commandDownload) #use commandDownload method when download command is used

    decodeParser = subparsers.add_parser("decode") #add decode command
    decodeParser.add_argument("bencodedValue") #the bencoded value we have to convert to json
    decodeParser.set_defaults(func=commandDecode) #use commandDecode method when decode command is used


    args = parser.parse_args() #package arguments the user types in the terminal into args object
    args.func(args) #call specific method on the arguments(what func is for)


if __name__ == "__main__":
    main()

