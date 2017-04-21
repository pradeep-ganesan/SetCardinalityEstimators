"""property checks of continuous update streams"""

def empty(stream, skset, bucket):
    """checks if bucket of stream is empty"""
    if stream.bitsketchcounter[skset][bucket * (stream.bitsketchsize+1)] == 0:
        return True
    return False

def singleton(stream, skset, bucket):
    """checks if bucket of stream is singleton"""
    for i in range(1, stream.bitsketchsize+1):
        if(
                stream.bitsketchcounter[skset][bucket * (stream.bitsketchsize+1) + i] > 0
                and (
                    stream.bitsketchcounter[skset][bucket * (stream.bitsketchsize+1 + i)] >
                    stream.bitsketchcounter[skset][bucket * (stream.bitsketchsize+1)]
                )
        ):
            return False
    return True

def identical_singleton(streamA, streamB, skset, bucket):
    """checks if two streams are singleton at same bucket"""
    assert streamA.bitsketchsize == streamB.bitsketchsize
    assert streamA.sketchsets == streamB.sketchsets
    if not singleton(streamA, skset, bucket) or not singleton(streamB, skset, bucket):
        return False
    for i in range(1, streamA.bitsketchsize+1):
        if(
                streamA.bitsketchcounter[skset][bucket * (streamA.bitsketchsize+1) + i] > 0
                and streamB.bitsketchcounter[skset][bucket * (streamB.bitsketchsize+1) + i] > 0
                and (
                    streamA.bitsketchcounter[skset][bucket * (streamA.bitsketchsize+1 + i)] !=
                    streamB.bitsketchcounter[skset][bucket * (streamB.bitsketchsize+1) + i]
                )
        ):
            return False
    return True

def singleton_union(streamA, streamB, skset, bucket):
    """if union of bucket of both streams is a singleton"""
    assert streamA.bitsketchsize == streamB.bitsketchsize
    assert streamA.sketchsets == streamB.sketchsets
    if(
            (singleton(streamA, skset, bucket) and empty(streamB, skset, bucket))
            or (singleton(streamB, skset, bucket) and empty(streamA, skset, bucket))
    ):
        return True
    return identical_singleton(streamA, streamB, skset, bucket)
