#this entire file is for pytest, making sure various functions work and pass

import bencode

def test_decode_string():
    assert bencode.decodeBencode(b"5:hello") == b"hello"

def test_decode_integer():
    assert bencode.decodeBencode(b"i42e") == 42

def test_decode_negative_integer():
    assert bencode.decodeBencode(b"i-3e") == -3

def test_decode_list():
    assert bencode.decodeBencode(b"l5:helloi-5ee") == [b"hello", -5]

def test_decode_dict():
    assert bencode.decodeBencode(b"d8:terminali5ee") == {b"terminal":5}

def test_round_trip():
    """encodeBencode(decodeBencode(x)) should equal x for several types."""
    samples = [b"hello", 42, -5, [b"hello", 42], {b"foo": b"bar"}]
    for original in samples:
        encoded = bencode.encodeBencode(original) #convert into bencode
        decoded = bencode.decodeBencode(encoded) #decode from bencode back to original
        assert original == decoded #make sure it's the same

