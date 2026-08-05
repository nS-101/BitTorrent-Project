import pytest #needed for @pytest.fixture
from torrent import Torrent
from pathlib import Path

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