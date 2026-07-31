import requests
import bencode

def getPeers(torrent) -> list[tuple[str, int]]:
    """Announce to the tracker and return a list of ip addresses and port numbers 
    corresponding to peer addresses """
    parameters = {
        "info_hash": torrent.infoHash,
        "peer_id": "12345678901234567890", #random 20 byte string
        "port": 6881,
        "uploaded": 0,
        "downloaded": 0,
        "left": torrent.length,
        "compact": 1
    } #parameters for GET request specified
    response = requests.get(torrent.announce.decode(), params=parameters) #send GET request with tracker and parameters

    trackerData = bencode.decodeBencode(response.content) 
    peersBlob = trackerData[b"peers"] #get list of peers from response content

    peersArray = []
    for i in range(0, len(peersBlob),6):
        data = peersBlob[i:i+6] #each element is separated per six bytes
        ipData = data[:4] #first four bytes are the ip address
        ipAddress = ".".join(str(element) for element in ipData) #create the ip address string by converting from bytes to string

        portData = data[4:6] #last two bytes are the port bytes
        port = int.from_bytes(portData, byteorder="big") #convert to int from bytes to form port number

        peerTuple = (ipAddress, port) 
        peersArray.append(peerTuple) #peersArray will hold a list of peers' data, meaning ip address as well as port numbers
    
    return peersArray

