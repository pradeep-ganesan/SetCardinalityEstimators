import math
import farmhash
import logging

logme = logging.getLogger('estimator')

class TwoLevelSketch(object):
    """Ganguly et al 2-level hash sketch for
    distinct value estimation"""

    FLAJOLET_MARTIN_PHI = 1.2928

    def __init__(self, sketchsize=64, numhash=256):
        self.numhash = numhash
        self.bitsketchsize = sketchsize
        self.bitsketch = [0] * self.bitsketchsize * self.numhash
        self.sketchcounter = [0] * (self.bitsketchsize + 1) * self.numhash
        if __debug__:
            self.dataitems = []
            self.distinctitems = {}

    def add(self, item):
        """fetch stream items"""
        self.update_sketch(item)

        if __debug__:
            self.dataitems.append(item)
            if self.distinctitems.get(item):
                self.distinctitems[item] += 1
            else:
                self.distinctitems[item] = 1

    def total_items(self):
        """total items"""
        return len(self.dataitems) if __debug__ else None

    def distinct_items(self):
        """actual number of distinct items"""
        return len(self.distinctitems) if __debug__ else None

    def update_sketch(self, item):
        """construct bitsketch and sketch counters"""
        pos = 0

        def get_hash(item, seed):
            """use a randomly chosen hash function to generate hash"""
            return (
                farmhash.hash32withseed(item, seed)
                if self.bitsketchsize == 32 else
                farmhash.hash64withseed(item, seed)
            )

        def least_sig_1bit(h):
            """position of least significant 1-bit
            zer-based position"""
            # hash is a 32bit number
            return self.bitsketchsize if not h else (h&-h).bit_length()-1

        # update bitsketch and sketch counters
        for r in range(0, self.numhash):
            h = get_hash(item, r)
            try:
                pos = least_sig_1bit(h)
                self.bitsketch[r * self.bitsketchsize + pos] = 1
                self.sketchcounter[r * (self.bitsketchsize+1)] += 1
                self.sketchcounter[r * (self.bitsketchsize+1) + (pos+1)] += 1
            except IndexError:
                logme.error(
                    'index error at : %d %d for hash %s',
                    r, pos, h
                )

    def __len__(self):
        """flajoletmartin cardinality estimation"""
        R = 0.0

        # estimate the count of distinct values
        total, leftmostzero = 0.0, self.bitsketchsize
        for r in range(0, self.numhash):
            for m in range(0, self.bitsketchsize, 1):
                if not self.bitsketch[r*self.bitsketchsize+m]:
                    leftmostzero = m
                    break
            total += leftmostzero
        R = self.FLAJOLET_MARTIN_PHI * pow(2.0, total/float(self.numhash))

        return R

    def error(self):
        """error rate: x%>0 indicates estimate more than actual by x%
                       x%<0 indicates estimate less than actual by x%
                       x%==0 indicates estimate==actual"""
        if __debug__:
            err_percent = float(len(self) - self.distinct_items()) / float(self.distinct_items())
            return err_percent
        return None

def main():
    def get_continuous_stream(filename):
        # get words from file
        get_continuous_stream.estimator = TwoLevelSketch()
        with open(filename) as fp:
            for line in fp:
                for word in line.split():
                    get_continuous_stream.estimator.add(word)
    get_continuous_stream.estimator = None

    get_continuous_stream('./testfile.txt')
    if __debug__:
        print(
            'Total items: {} \nDistinct items count: {}\n'.format(
                get_continuous_stream.estimator.total_items(),
                get_continuous_stream.estimator.distinct_items()
            )
        )
    print(
        'Estimated count for 64-hashset is {}'.format(
            len(get_continuous_stream.estimator)
            )
        )
    if __debug__:
        print('Error rate: {}%'.format(get_continuous_stream.estimator.error()))

if __name__ == '__main__':
    main()
