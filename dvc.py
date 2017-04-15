class DVC(object):
    """abstract distinct value counters"""

    def __len__(self):
        raise NotImplementedError()

    def __and__(self, otherstream):
        raise NotImplementedError()

    def __or__(self, otherstream):
        raise NotImplementedError()

    def add(self, item):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def copy(self):
        raise NotImplementedError()
