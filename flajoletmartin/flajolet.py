import math
import mmh3

class FlajoletMartin(object):
    """Flajolet & Martin's probabilitic algorithm for
    distinct value estimation, a.k.a set cardinality"""

    PHI = 1.2928

    def __init__(self, filename, sketchsize=32):
        self.r = 0
        self.bitsketch = []
        self.bitsketchsize = sketchsize
        self.dataitems = []
        self.distinctitems = {}

        # get words from file
        with open(filename) as fp:
            self.dataitems = [words for line in fp for words in line.split()]
        for item in self.dataitems:
            if self.distinctitems.get(item):
                self.distinctitems[item] += 1
            else:
                self.distinctitems[item] = 1
 
    def get_hash(self, item, seed):
        """use a randomly chosen hash function to generate hash"""
        return mmh3.hash(item, seed)

    @staticmethod
    def ls1b(h):
        """position of least significant 1-bit"""
        # code reference: https://github.com/svengato/FlajoletMartin
        # hash is a 32bit number
        return 32 if not h else (h&-h).bit_length()-1

    def total_size(self):
        """total items"""
        assert sum(self.distinctitems.values()) == len(self.dataitems)
        return len(self.dataitems)

    def distinct_count(self):
        """actual number of distinct items"""
        assert sum(self.distinctitems.values()) == len(self.dataitems)
        return len(self.distinctitems)

    def reset_bitsketch(self):
        assert self.r
        self.bitsketch = [0] * self.bitsketchsize * self.r

    def estimate_cardinality(self, hash_group_size=32):
        """estimate set cardinality"""
        self.r = hash_group_size
        R = 0.0
        self.reset_bitsketch()

        # construct bitsketch
        try:
            for r in range(0, self.r):
                for m in range(0, self.total_size()):
                    h = self.get_hash(self.dataitems[m], r)
                    self.bitsketch[r*self.bitsketchsize+self.ls1b(h)] = 1
        except IndexError:
            print('index error at : [{}][{}] for hash {}'.format(r, self.ls1b(h), h))
            raise

        total, leftmostZero = 0.0, self.bitsketchsize
        for r in range(0, self.r):
            for m in range(0, self.bitsketchsize, 1):
                if not self.bitsketch[r*self.bitsketchsize+m]:
                    leftmostZero = m
                    break
            total += leftmostZero

        return FlajoletMartin.PHI * pow(2.0, total/float(self.r))

def main():
    estimator = FlajoletMartin('./testfile.txt', 32)

    print(
        'Total items: {} \nDistinct items count: {}\n'.format(
            estimator.total_size(),
            estimator.distinct_count()
            )
    )

    print('Flajolet-Martin counts')
    r = 2
    while r <= 1024:
        print(
            'Estimated count for m[{}]: {}'.format(
                r,
                estimator.estimate_cardinality(r)
                )
        )
        r *= 2

if __name__ == '__main__':
    main()
