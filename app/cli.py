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

def commandDownloadPiece(args):
    """Download a single piece from a .torrent file and save it to disk"""
    torrent = Torrent.fromFile(args.torrentFile) #read file and get info using fromFile method
    peers = getPeers(torrent) #get list of peers
    sock, peerID = handshake(torrent, peers[0][0], peers[0][1]) #pass arguments for peer handshake and get back the socket and peerClientID
    waitForUnchoke(sock) #wait for unchoke message to continue
    pieceData = downloadPiece(sock, torrent, args.pieceIndex) 
    with open(args.output, "wb") as file:
        file.write(pieceData) #write piece to disk
    

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

    args = parser.parse_args() #package arguments the user types in the terminal into args object
    args.func(args) #call specific method on the arguments(what func is for)


if __name__ == "__main__":
    main()

