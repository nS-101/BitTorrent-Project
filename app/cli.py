import argparse
import sys
from torrent import Torrent
from tracker import getPeers 
from peer import handshake, waitForUnchoke, downloadPiece 
#imported required methods, class, packages

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


def main():
    parser = argparse.ArgumentParser(description="A BitTorrent client") #create parser object
    subparsers = parser.add_subparsers(dest="command", required=True) #create subparsers to pull commands like "info" or "peers", required means it crashes without it

    infoParser = subparsers.add_parser("info") #add info command
    infoParser.add_argument("torrentFile") #the .torrent file is the argument for the info command
    infoParser.set_defaults(func=commandInfo) #use commandInfo method when info command is used

    peersParser = subparsers.add_parser("peers") #add peers command
    peersParser.add_argument("torrentFile") ##the .torrent file is the argument for the peers command
    peersParser.set_defaults(func=commandPeers) #use commandInfo method when peers command is used

    args = parser.parse_args() #package arguments the user types in the terminal into args object
    args.func(args) #call specific method on the arguments(what func is for)


if __name__ == "__main__":
    main()

