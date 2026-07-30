def decodeBencode(bencodedValue: bytes): #need to split between decodeBencode and decodeRecursive since we're returning a tuple to keep track of a index for the list decoding, and we want one method to return the actual value
    """Decode a full top-level bencoded value.
    Returns just the value, callers shouldn't need to know about
    the internal index tracking used during recursive decoding.
    """

    value, _ = decodeRecursive(bencodedValue)
    return value

def encodeBencode(value) -> bytes:
    """Encode an input into bencoded form. Handles bytes, int, list, dicts"""

    if isinstance(value, bytes): #bencoding strings from bytes
        encodedLengthString = bytes(str(len(value)), "ascii")
        return encodedLengthString + b":" + value

    elif isinstance(value, int): #bencoding ints 
        return f"i{value}e".encode("ascii")

    elif isinstance(value, list): #bencoding lists 
        arr = []
        for item in value:
            arr.append(encodeBencode(item))
        returnedList = b"".join(arr)
        returnedList = "l".encode() + returnedList + "e".encode()
        return returnedList
    
    elif isinstance(value, dict): #bencoding dictionaries
        sortedDict = sorted(value.items())
        arr = []
        for key, corrValue in sortedDict:
            arr.append(encodeBencode(key) + encodeBencode(corrValue))
        returnedDict = b"".join(arr)
        returnedDict = "d".encode() + returnedDict + "e".encode()
        return returnedDict

    else:
        raise TypeError(f"can't bencode type {type(value)}")

def decodeRecursive(bencodedValue: bytes):
    """Decode one bencoded value starting at the front of bencodedValue.
    Returns (value, endIndex) where endIndex is how many bytes were
    consumed, this is needed so lists/dicts know where the next element starts.
    """

    length = len(bencodedValue)
    if chr(bencodedValue[0]).isdigit(): #string
        decodedString = decodeString(bencodedValue)
        return decodedString
    elif chr(bencodedValue[0]) == "i": #integer 
        decodedInteger = decodeInteger(bencodedValue)
        return decodedInteger
    elif chr(bencodedValue[0]) == "l": #list
        decodedList = decodeList(bencodedValue)
        return decodedList
    elif chr(bencodedValue[0]) == "d": #dictionary
        decodedDictionary = decodeDictionary(bencodedValue)
        return decodedDictionary


def decodeInteger(bencodedValue: bytes):
    endIndex = bencodedValue.find(b"e")
    actualNumber = bencodedValue[1:endIndex] #get actual number by cutting out the i and e
    try:
        actualNumber = int(actualNumber.decode()) #convert to int() since .decode would return string 76 otherwise
        return actualNumber, endIndex+1 #return the actual value as well as the index where the decoding ends
    except ValueError:
        raise ValueError("invalid format for numbers")



def decodeString(bencodedValue: bytes):
    firstColonIndex = bencodedValue.find(b":")
    lengthOfString = int(bencodedValue[:firstColonIndex].decode()) #get the number before the colon that represents the length of the string
    start = firstColonIndex + 1
    end = start + lengthOfString
    if firstColonIndex == -1:
        raise ValueError("Invalid encoded value")
    word = bencodedValue[start:end]
    return word, end #return the actual value as well as the index where the decoding ends



def decodeList(bencodedValue: bytes):
    result = []
    index = 1 #start after the "l"

    while bencodedValue[index:index+1] != b"e":
        value, numberOfIndex = decodeRecursive(bencodedValue[index:])
        result.append(value)
        index += numberOfIndex
    return result, index+1 #include the "e" in the total amount



def decodeDictionary(bencodedValue: bytes):
    result = [] #start as array, will convert to dictionary once all keys/values are added
    colonIndex = bencodedValue.find(b":") #get index of colon
    number = bencodedValue[1:colonIndex].decode() 
    index = 1 #start after the "d"
    while bencodedValue[index:index+1] != b"e":
        value, numberOfIndex = decodeRecursive(bencodedValue[index:])
        index += numberOfIndex
        result.append(value)
    #all keys/values added at this point
    newDict = dict(zip(result[0::2], result[1::2])) #keys start at index 0 and every 2nd value is a key, values start at index 1 and every second value is a value corresponding to a key
    return newDict, index+1


def decodeBytesKeys(data): #need this method to separate between info and decode command in main since json can't process bytes and there will be an error if we use decode on a list/dict with bytes so we create a copy that has no bytes using this method
    if isinstance(data, dict): #handle dictionaries
        newDict = {}
        for key, value in data.items():
            if isinstance(key, bytes): #convert key to string if it's in bytes form
                newKey = key.decode()
            else:
                newKey = key
            newDict[newKey] = decodeBytesKeys(value) #recursively translate from bytes to str for entire dict
        return newDict
    elif isinstance(data, list): #handle lists
        newList = []
        for item in data:
            processedItem = decodeBytesKeys(item) #again, recursively translate from bytes to str for entire list
            newList.append(processedItem)
        return newList
    elif isinstance(data, bytes): #handle bytes
        return data.decode()
    else:
        return data