class DVC(object):
    """abstract distinct value counters"""

    STREAM_ID = 0

    def __init__(self, sid=None):
        self.streamid = sid or (self.STREAM_ID + 1)

    def __len__(self):
        raise NotImplementedError()

    def __and__(self, other):
        raise NotImplementedError()

    def __or__(self, other):
        raise NotImplementedError()

    def add(self, item):
        """fetch stream items and build sketches"""
        raise NotImplementedError()

    def clear(self):
        """clear sketches for this stream"""
        raise NotImplementedError()

    def copy(self, sourcestream):
        """copy the stream sketches"""
        raise NotImplementedError()
