import pytest
import struct
import socket
from peer import waitForUnchoke #.toml file automatically does the necessary configuration to successfully import files

#testing that when we have a correct socket and parameters, we don't get any exceptions
#and when we do have something incorrect, like wrong byteID,(0 instead of 1),
#we get the right exception

#in the fakeSocket class, we use method names that have the same name as actual
#socket method names(recv, sendall, etc.) to trick the waitForUnchoke method
# into using our fake socket methods and objects, unaware that it's actually
#not a real socket with a stream of data. we use this to test using pytest

#each fakeSocket object has a list of elements, whether they're bytes or socket
#timeout exception objects. in __init__, we have a list that corresponds to this
#and recv pulls elements from this list, eventually getting bytes and the exceptions


class FakeSocket:
    """Stands in for a real socket. recvQueue is a list where each item
    is either bytes that are returned by the next recv call or an Exception instance
    raised by the next recv call"""

    def __init__(self, recvQueue):
        self.recvQueue = list(recvQueue)
        self.sentData = []

    def settimeout(self, seconds):
        pass #no real timing needed in a fake, only to appease waitForUnchoke when it calls this

    def recv(self, n):
        item = self.recvQueue.pop(0)
        if isinstance(item, bytes):
            return item
        elif isinstance(item, Exception):
            raise item

    def sendall(self, data):
        self.sentData.append(data) #since this is a fake, just record the data and don't actually send it

def test_waitForUnchoke_succeeds_with_real_unchoke():
    """No bitfield sent, peer sends a real unchoke, should not raise"""
    fakeSock = FakeSocket([
        socket.timeout(), #bitfield recv times out(none sent)
        (1).to_bytes(4, byteorder="big"), #unchoke message prefix, with 1 representing the length of the next
        bytes([1]), #unchoke message body, first byte representing unchoke
    ]) 
    waitForUnchoke(fakeSock) #should complete with no exception

def test_waitForUnchoke_raises_on_choke():
    """Peer sends choke(id 0) instead of unchoke, this should raise the ConnectionRefused error
    when recv is called from waitForUnchoke"""
    fakeSock = FakeSocket([
        socket.timeout(),
        (1).to_bytes(4, byteorder="big"), #4 bytes represents the prefix
        bytes([0]), #0 instead of 1 for choke
    ])
    with pytest.raises(ConnectionRefusedError): #make sure the right exception is raised
        waitForUnchoke(fakeSock) 

def test_waitForUnchoke_raises_on_no_response():
    """Peer never sends anything after the handshake, this should raise socket.timeout"""
    fakeSock = FakeSocket([
        socket.timeout(),
        socket.timeout()
    ])
    with pytest.raises(socket.timeout): #we want this particular exception raised when we get timed out
        waitForUnchoke(fakeSock) 


