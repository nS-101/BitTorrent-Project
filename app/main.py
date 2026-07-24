import json
import sys
import bencodepy 
import requests 
import hashlib
import urllib.parse
import socket
# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"

def decode_BytesKeys(data): #need this method to separate between info and decode command in main since json can't process bytes and there will be an error if we use decode on a list/dict with bytes so we create a copy that has no bytes using this method
    if isinstance(data, dict): #handle dictionaries
        new_dict = {}
        for key, value in data.items():
            if isinstance(key, bytes): #convert key to string if it's in bytes form
                new_key = key.decode()
            else:
                new_key = key
            new_dict[new_key] = decode_BytesKeys(value) #recursively translate from bytes to str for entire dict
        return new_dict
    elif isinstance(data, list): #handle lists
        new_list = []
        for item in data:
            processed_item = decode_BytesKeys(item) #again, recursively translate from bytes to str for entire list
            new_list.append(processed_item)
        return new_list
    elif isinstance(data, bytes): #handle bytes
        return data.decode()
    else:
        return data

def decode_bencode(bencoded_value): #need to split between decode_bencode and decode_recursive since we're returning a tuple to keep track of a index for the list decoding, and we want one method to return the actual value
    value, _ = decode_recursive(bencoded_value)
    return value

def decode_recursive(bencoded_value):
    length = len(bencoded_value)
    if chr(bencoded_value[0]).isdigit(): #string
        decodedString = decode_String(bencoded_value)
        return decodedString
    elif chr(bencoded_value[0]) == "i": #integer 
        decodedInteger = decode_Integer(bencoded_value)
        return decodedInteger
    elif chr(bencoded_value[0]) == "l": #list
        decodedList = decode_List(bencoded_value)
        return decodedList
    elif chr(bencoded_value[0]) == "d": #dictionary
        decodedDictionary = decode_Dictionary(bencoded_value)
        return decodedDictionary

def decode_Integer(bencoded_value):
    endIndex = bencoded_value.find(b"e")
    actualNumber = bencoded_value[1:endIndex] #get actual number by cutting out the i and e
    try:
        actualNumber = int(actualNumber.decode()) #convert to int() since .decode would return string 76 otherwise
        return actualNumber, endIndex+1 #return the actual value as well as the index where the decoding ends
    except ValueError:
        raise ValueError("invalid format for numbers")

def decode_String(bencoded_value):
    first_colon_index = bencoded_value.find(b":")
    lengthOfString = int(bencoded_value[:first_colon_index].decode()) #get the number before the colon that represents the length of the string
    start = first_colon_index + 1
    end = start + lengthOfString
    if first_colon_index == -1:
        raise ValueError("Invalid encoded value")
    word = bencoded_value[start:end]
    return word, end #return the actual value as well as the index where the decoding ends

def decode_List(bencoded_value):
    result = []
    index = 1 #start after the "l"

    while bencoded_value[index:index+1] != b"e":
        value, numberOfIndex = decode_recursive(bencoded_value[index:])
        result.append(value)
        index += numberOfIndex
    return result, index+1 #include the "e" in the total amount

def decode_Dictionary(bencoded_value):
    result = [] #start as array, will convert to dictionary once all keys/values are added
    colonIndex = bencoded_value.find(b":") #get index of colon
    number = bencoded_value[1:colonIndex].decode() 
    index = 1 #start after the "d"
    while bencoded_value[index:index+1] != b"e":
        value, numberOfIndex = decode_recursive(bencoded_value[index:])
        index += numberOfIndex
        result.append(value)
    #all keys/values added at this point
    newDict = dict(zip(result[0::2], result[1::2])) #keys start at index 0 and every 2nd value is a key, values start at index 1 and every second value is a value corresponding to a key
    return newDict, index+1

def torrentReader(torrentFile):
    with open(torrentFile, "rb") as file:
        fileContents = file.read()
        torrentData = decode_bencode(fileContents)
        return torrentData
    
def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        rawData = decode_bencode(bencoded_value)
        formattedData = decode_BytesKeys(rawData)
        print(json.dumps(formattedData)) 
    
    elif command == "info": 
        torrentFile = sys.argv[2]
        torrentData = torrentReader(torrentFile)
        tracker = torrentData[b"announce"].decode()
        length = torrentData[b"info"][b"length"] #it's a nested dictionary to begin with, so we need two keys to get the length
        infoDictionary = torrentData[b"info"] #get info dictionary
        infoDictionary = bencodepy.encode(infoDictionary) #make sure the info dictionary is bencoded
        infoHash = hashlib.sha1(infoDictionary).hexdigest() #convert infoDictionary into sha1 hash 
        pieceLength = torrentData[b"info"][b"piece length"] 
        allHashes = torrentData[b"info"][b"pieces"] #a continuous string of hashes that needs to be split up in order to get the hashes for individual pieces
        arrayOfIndividualHashes = []
        for i in range(0, len(allHashes), 20):
            arrayOfIndividualHashes.append(allHashes[i: i+20].hex())#append to array the individual hash
        
        print(f"Tracker URL: {tracker}")
        print(f"Length: {length }")
        print(f"Info Hash: {infoHash}")
        print(f"Piece Length: {pieceLength}")
        print("Piece Hashes: ")
        print(*(hash for hash in arrayOfIndividualHashes), sep="\n") #print each individual hash on a new line we'll send data to

    
    elif command == "peers": #command to get the ip addresses and port numbers for the different peers we can connect to
        torrentFile = sys.argv[2]
        torrentData = torrentReader(torrentFile)
        tracker = torrentData[b"announce"].decode() #the tracker URL with the ip addresses
        length = torrentData[b"info"][b"length"] #it's a nested dictionary to begin with, so we need two keys to get the length
        infoDictionary = torrentData[b"info"] #get info dictionary
        infoDictionary = bencodepy.encode(infoDictionary) #make sure the info dictionary is bencoded
        infoHash = hashlib.sha1(infoDictionary).digest() #convert infoDictionary into sha1 hash(not hex, just bytes)
        urlEncodedInfoHash = urllib.parse.quote_from_bytes(infoHash) #convert inot url encoded format so urls can accept it(they dont accept just bytes)
        pieceLength = torrentData[b"info"][b"piece length"] 
        allHashes = torrentData[b"info"][b"pieces"] #a continuous string of hashes that needs to be split up in order to get the hashes for individual pieces
        arrayOfIndividualHashes = []
        for i in range(0, len(allHashes), 20):
            arrayOfIndividualHashes.append(allHashes[i: i+20].hex())#append to array the individual hash
        parameters = {
            "info_hash": infoHash,
            "peer_id": "12345678901234567890", #random 20 byte string
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": length,
            "compact": 1
        } #parameters specified

        response = requests.get(tracker, params=parameters) #response is what is returned by sending these specific parameters
        trackerData = decode_bencode(response.content)
        peers = trackerData[b"peers"] #string of bytes encoded ip addresses and ports for each peer we can connect to
        for i in range(0, len(peers),6):
            data = peers[i:i+6] #each element is separated per six bytes
            ipData = data[:4] #first four bytes are the ip address
            ipAddress = ".".join(str(element) for element in ipData) #create the ip address string by converting from bytes to string

            portData = data[4:6] #last two bytes are the port bytes
            port = int.from_bytes(portData, byteorder="big") #convert to int from bytes to form port number

            print(f"{ipAddress}:{port}")
    
    elif command == "handshake":
        torrentFile = sys.argv[2]
        torrentData = torrentReader(torrentFile)
        tracker = torrentData[b"announce"].decode() #the tracker URL with the ip addresses
        length = torrentData[b"info"][b"length"] #it's a nested dictionary to begin with, so we need two keys to get the length
        infoDictionary = torrentData[b"info"] #get info dictionary
        infoDictionary = bencodepy.encode(infoDictionary) #make sure the info dictionary is bencoded
        infoHash = hashlib.sha1(infoDictionary).digest() #convert infoDictionary into sha1 hash(not hex, just bytes)
        urlEncodedInfoHash = urllib.parse.quote_from_bytes(infoHash) #convert inot url encoded format so urls can accept it(they dont accept just bytes)
        pieceLength = torrentData[b"info"][b"piece length"] 
        allHashes = torrentData[b"info"][b"pieces"] #a continuous string of hashes that needs to be split up in order to get the hashes for individual pieces
        arrayOfIndividualHashes = []


        peerData = sys.argv[3] #has peerIP and peer port
        peerIP, peerPort = peerData.split(":", 1) #split into two different variables
        protocolStringLength = 19
        protocolStringLength = protocolStringLength.to_bytes(1, byteorder="big") #convert 19 to bytes object
        protocolString = b"BitTorrent protocol"
        reservedBytes = b"\x00" * 8 #create 8 empty bytes
        #infoHash
        peerID = b"\x10" * 20 #20 random bytes to send as ID
        continousBytes = b"".join([protocolStringLength, protocolString, reservedBytes, infoHash, peerID]) #string of bytes we send to peer
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket: #open tcp connection
            clientSocket.connect((peerIP, int(peerPort)))
            clientSocket.sendall(continousBytes) #send bytes
            responseFromClient = clientSocket.recv(68)
            printedHexResponse = responseFromClient[48:].hex() #take last 20 bytes since that's the peer ID, everything else is just the data I sent
        print(f"Peer ID: {printedHexResponse}")

    else:
        raise NotImplementedError(f"Unknown command {command}")



if __name__ == "__main__":
    main()
