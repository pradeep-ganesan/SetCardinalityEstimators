"""property checks of continuous update streams"""

def empty(stream, bucket):
    """checks if bucket of stream is empty"""
    if stream.sketchcounter[bucket * (stream.bitsketchsize+1)] == 0:
        return True
    return False

def singleton(stream, bucket):
    """checks if bucket of stream is singleton"""
    for i in range(1, stream.bitsketchsize+1):
        if(
                stream.sketchcounter[bucket * (stream.bitsketchsize+1) + i] > 0
                and (
                    stream.sketchcounter[bucket * (stream.bitsketchsize+1 + i)] >
                    stream.sketchcounter[bucket * (stream.bitsketchsize+1)]
                )
        ):
            return False
    return True

def identical_singleton(streamA, streamB, bucket):
    """checks if two streams are singleton at same bucket"""
    assert streamA.bitsketchsize == streamB.bitsketchsize
    if not singleton(streamA, bucket) or not singleton(streamB, bucket):
        return False
    for i in range(1, streamA.bitsketchsize+1):
        if(
                streamA.sketchcounter[bucket * (streamA.bitsketchsize+1) + i] > 0
                and streamB.sketchcounter[bucket * (streamB.bitsketchsize+1) + i] > 0
                and (
                    streamA.sketchcounter[bucket * (streamA.bitsketchsize+1 + i)] !=
                    streamB.sketchcounter[bucket * (streamB.bitsketchsize+1) + i]
                )
        ):
            return False
    return True

def singleton_union(streamA, streamB, bucket):
    """if union of bucket of both streams is a singleton"""
    assert streamA.bitsketchsize == streamB.bitsketchsize
    if(
            (singleton(streamA, bucket) and empty(streamB, bucket))
            or (singleton(streamB, bucket) and empty(streamA, bucket))
    ):
        return True
    return identical_singleton(streamA, streamB, bucket)
