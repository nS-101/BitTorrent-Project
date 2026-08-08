from types import SimpleNamespace
from cli import writeDownloadedFiles

def test_writeDownloadedFiles_multifile(tmp_path): #tmp_path keyword in python creates its own temporary folder for file testing
    fakeTorrent = SimpleNamespace(
        files = [
            {b"length": 5, b"path": [b"file1.txt"]},
            {b"length": 3, b"path": [b"file2.txt"]},
        ],
        infoDict = {b"name": b"MyAlbum"},
    )
    totalFile = b"ABCDEFGH"
    writeDownloadedFiles(fakeTorrent, totalFile, str(tmp_path))
    assert (tmp_path / "MyAlbum" / "file1.txt").read_bytes() == b"ABCDE"
    assert (tmp_path / "MyAlbum" / "file2.txt").read_bytes() == b"FGH"

def test_writeDownloadedFiles_single_file(tmp_path):
    fakeTorrent = SimpleNamespace(files=None)
    outputFile = tmp_path / "movie.mp4"

    writeDownloadedFiles(fakeTorrent, b"some file content", str(outputFile))

    assert outputFile.read_bytes() == b"some file content"

