import bencode

def test_decode_string():
    assert bencode.decodeBencode(b"5:hello") == b"hello"

def test_decode_integer():
    assert bencode.decodeBencode(b"i42e") == 42

def test_decode_negative_integer():
    ...

def test_decode_list():
    ...

def test_decode_dict():
    ...

def test_round_trip():
    """encodeBencode(decodeBencode(x)) should equal x for several types."""
    samples = [b"hello", 42, -5, [b"hello", 42], {b"foo": b"bar"}]
    for original in samples:
        ...