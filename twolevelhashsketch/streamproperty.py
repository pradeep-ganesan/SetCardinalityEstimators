"""property checks of continuous update streams"""
import logging

logme = logging.getLogger('estimator')

def empty(sketchcounters, sketchsize, bucket):
    """checks if bucket of sketch is empty"""
    # check total counter for this sketch bucket at pos 0
    if sketchcounters[bucket * (sketchsize+1)] == 0:
        return True
    return False
    '''    logme.debug(
        'len(sketchcounters):%d sketcounters[%d] bucket:%d sketchsize:%d',
        len(sketchcounters),
        bucket*(sketchsize+1),
        bucket,
        sketchsize
    )'''

def singleton(sketchcounters, sketchsize, bucket):
    """checks if bucket of sketch is singleton"""
    if empty(sketchcounters, sketchsize, bucket):
        return False
    for i in range(1, sketchsize+1):
        if(
                sketchcounters[bucket * (sketchsize+1)] > 0
                and (
                    sketchcounters[bucket * (sketchsize+1)] >
                    sketchcounters[bucket * (sketchsize+1) + i]
                )
        ):
            return False
    return True

def identical_singleton(sketchcountersA, sketchcountersB, sketchsize, bucket):
    """checks if two sketches are singleton at same bucket"""
    if (not singleton(sketchcountersA, sketchsize, bucket)
            or not singleton(sketchcountersB, sketchsize, bucket)
       ):
        logme.debug('Not identical')
        return False
    for i in range(1, sketchsize+1):
        if(
                sketchcountersA[bucket * (sketchsize+1) + i] > 0
                and sketchcountersB[bucket * (sketchsize+1) + i] > 0
                and (
                    sketchcountersA[bucket * (sketchsize+1 + i)] !=
                    sketchcountersB[bucket * (sketchsize+1) + i]
                )
        ):
            return False
    return True

def singleton_union(sketchcountersA, sketchcountersB, sketchsize, bucket):
    """if union bucket of both sketches is a singleton"""
    if(
            (
                singleton(sketchcountersA, sketchsize, bucket)
                and empty(sketchcountersB, sketchsize, bucket)
            )
            or (
                singleton(sketchcountersB, sketchsize, bucket)
                and empty(sketchcountersA, sketchsize, bucket)
            )
    ):
        return True
    return identical_singleton(sketchcountersA, sketchcountersB, sketchsize, bucket)
