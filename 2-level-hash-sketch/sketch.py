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
        self.bitsketch = []
        self.sketchcounter = []
        self.bitsketchsize = sketchsize
        self.dataitems = []
        self.distinctitems = {}

    def add(self, item):
        """fetch stream items"""
        self.dataitems.append(item)
        if self.distinctitems.get(item):
            self.distinctitems[item] += 1
        else:
            self.distinctitems[item] = 1

    def total_items(self):
        """total items"""
        return len(self.dataitems)

    def distinct_items(self):
        """actual number of distinct items"""
        return len(self.distinctitems)

    def build_sketch(self):
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

        # reset bitsketch
        assert self.numhash
        self.bitsketch = [0] * self.bitsketchsize * self.numhash
        self.sketchcounter = [0] * (self.bitsketchsize + 1) * self.numhash

        # construct bitsketch and sketch counters
        for r in range(0, self.numhash):
            for m in range(0, self.total_items()):
                h = get_hash(self.dataitems[m], r)
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

        # construct bitsketch
        self.build_sketch()

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

def main():
    def openfile(filename, n=64):
        # get words from file
        openfile.estimator = TwoLevelSketch(numhash=n)
        with open(filename) as fp:
            for line in fp:
                for word in line.split():
                    openfile.estimator.add(word)
    n = 4
    while(n<=2048):
        openfile.estimator = None
        openfile('./testfile.txt')
        print(
            '\nTotal items: {} \nDistinct items count: {}\n'.format(
                openfile.estimator.total_items(),
                openfile.estimator.distinct_items()
            )
        )
        print('Flajolet-Martin counts')
        print(
            'Estimated count for nhash:{} is {}'.format(
                n, len(openfile.estimator)
                )
        )
        n *= 2

if __name__ == '__main__':
    main()
