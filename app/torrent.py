import hashlib 
import bencode #import the file for its decoder methods


class Torrent:
    """represents a parsed .torrent file"""
    
    @classmethod
    def fromFile(cls, torrentFile:str):
        """Read a .torrent file off the disk and built a Torrent from it"""
        with open(torrentFile, "rb") as file:
            fileContents = file.read()
            torrentData = bencode.decodeBencode(fileContents) #use bencode file to decode
            announce = torrentData[b"announce"] 
            infoDict = torrentData[b"info"] #get info dict from torrent file
            return cls(announce, infoDict) #return these two data pieces so init can use them

    def __init__(self, announce:bytes, infoDict:dict):
        self.announce = announce
        self.infoDict = infoDict
        infoDict = bencode.encodeBencode(infoDict) #dict needs to be bencoded to be turned into a hashed dict
        infoHash = hashlib.sha1(infoDict).digest() #convert infoDictionary into sha1 hash(not hex, just bytes)
        self.infoHash = infoHash

    @property
    def length(self) -> int:
        """get total file length in bytes form, for both single file torrents and multifile"""
        if b"length" in self.infoDict: #single file
            return self.infoDict[b"length"]
        else: #multifile 
            files = self.infoDict[b"files"] #files is a list containing multiple dicts of files and their lengths and paths
            totalLength = 0
            for dictionary in files:
                totalLength += dictionary[b"length"] #keep adding each file length to total
            return totalLength

    @property
    def pieceLength(self) -> int:
        """get the standard piece length for the pieces in the .torrent file"""
        pieceLength = self.infoDict[b"piece length"] #self.infoDict already represents the outer key of ["info"] so we just access the piece length from there
        return pieceLength

    @property
    def pieceHashes(self) -> list[bytes]: 
        """get a list of hashes representing the hash of each piece in the .torrent file"""
        allHashes = self.infoDict[b"pieces"] #a continuous string of hashes that needs to be split up in order to get the hashes for individual pieces
        arrayOfIndividualHashes = []
        for i in range(0, len(allHashes), 20):
            arrayOfIndividualHashes.append(allHashes[i: i+20])#append to array the individual hash
        return arrayOfIndividualHashes
