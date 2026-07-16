import json
import sys
import bencodepy 
import requests 

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"

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
    word = bencoded_value[start:end].decode()
    return word, end #return the actual value as well as the index where the decoding ends

def decode_List(bencoded_value):
    result = []
    index = 1 #start after the "l"

    while bencoded_value[index:index+1] != b"e":
        value, numberOfIndex = decode_recursive(bencoded_value[index:])
        result.append(value)
        index += numberOfIndex
    return result, index+1 #include the "e" in the total amount
    

def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        
        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
