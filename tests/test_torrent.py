import pytest #needed for @pytest.fixture
from torrent import Torrent
from pathlib import Path
import bencode



SAMPLE_TORRENT = Path(__file__).parent / "sample.torrent" #create path for sample file
@pytest.fixture
def torrent():
    """Build a torrent object that can be used in tests so it's not being
    repetitively created per test"""
    torrent = Torrent.fromFile(str(SAMPLE_TORRENT)) #copy of sample.torrent in tests folder
    return torrent
#the parameters for the test methods will be called torrent, to match up
#with the name of the torrent method, making them use the same object so
#we don't have to keep instantiating a torrent object per method


def test_length_with_multi_file_torrent():
    """Multifile torrents have info[b"files"] instead of info[b"length"],
    length should still return the total amount across every file
    """
    multiFileInfo = {
        b"name": b"some-folder",
        b"piece length": 32768,
        b"pieces": b"x" * 20,
        b"files": [
            {b"length": 1000, b"path": [b"file1.txt"]},
            {b"length": 2000, b"path": [b"file2.txt"]},
        ],
    }
    t = Torrent(b"https://fake-tracker.example.com/announce", multiFileInfo) 
    assert t.length == 3000 #total amount is 3000 from adding the two files in this torrent
    #above assertion should fail until we have multifile support


#assert that certain methods work for known attributes of sample.torrent
#since we're testing against a known file, we're regression testing, and not
#coverage testing, which may change in the future
def test_length(torrent): 
    assert torrent.length == 92063

def test_piece_length(torrent):
    assert torrent.pieceLength == 32768

def test_piece_hashes_count(torrent):
    assert len(torrent.pieceHashes) == 3

def test_announce(torrent):
    assert torrent.announce == b"http://bittorrent-test-tracker.codecrafters.io/announce"

def test_info_hash(torrent):
    assert torrent.infoHash.hex() == "d69f91e6b2ae4c542468d1073a71d4ea13879a7f"