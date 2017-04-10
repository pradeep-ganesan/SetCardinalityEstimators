import math
import farmhash

class FlajoletMartin(object):
    """Flajolet & Martin's probabilitic algorithm for
    distinct value estimation, a.k.a set cardinality"""

    PHI = 1.2928

    def __init__(self, filename):
        self.r = 0
        self.M = 0
        self.log_M = 0
        self.bitsketch = []
        self.bitsketchdomain = []
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

        self.M = len(self.dataitems)
        print(int(math.ceil(math.log(self.M, 2))))
        self.log_M = int(math.ceil(math.log(self.M, 2)))

    def get_hash(self, item, seed):
        """use a randomly chosen new hash function to get hash"""
        return farmhash.hash64withseed(item, seed)

    @staticmethod
    def ls1b(h):
        """position of least significant 1-bit"""
        # hash is a 64bit number
        return 64 if not h else (h&-h).bit_length()-1

    @staticmethod
    def ls0b(h):
        """position of least significant 0-bit"""
        h_inv = ~h
        # hash is a 64bit number
        return 64 if not h else (h_inv&-h_inv).bit_length()-1

    @staticmethod
    def val_ls1b(h):
        """2^(position of least significant 1-bit)"""
        return h & (-h)

    @staticmethod
    def val_ls0b(h):
        """2^(position of least significant 0-bit)
        NOT USED"""
        return (~h) & (h + 1)

    def total_size(self):
        """total items"""
        assert sum(self.distinctitems.values()) == len(self.dataitems)
        return len(self.dataitems)

    def distinct_count(self):
        """actual number of distinct items"""
        assert sum(self.distinctitems.values()) == len(self.dataitems)
        return len(self.distinctitems)

    def build_bitsketch_domain(self):
        """set bitsketch domain to
        2^(position of least significant 1bit)"""
        try:
            for m in range(0, self.r):
                for i in range(0, self.total_size()):
                    h = self.get_hash(self.dataitems[i], m)
                    self.bitsketchdomain[i*self.r + m] = self.val_ls1b(h)
        except IndexError:
            print('index error at : {}'.format(i*self.r + m))
            raise

    def reset_bitsketch(self):
        self.bitsketch = [[0] * self.M] * self.r

    def estimate_cardinality(self, r):
        """estimate set cardinality"""
        assert r
        self.r = r
        self.reset_bitsketch()

        # construct bitsketch
        for r in range(0, self.r):
            for m in range(0, self.M):
                h = self.get_hash(self.dataitems[m], r)
                self.bitsketch[r][self.ls1b(h)] = 1

        total, leftmostZero = 0, 0
        for r in range(0, self.r):
            for m in range(self.log_M, -1, -1):
                if not self.bitsketch[r][m]:
                    leftmostZero = m
                    break
                total += leftmostZero

        R = FlajoletMartin.PHI * pow(2, total/self.r)
        return R

def main():
    estimator = FlajoletMartin('/Users/pradeepganesan/Documents/Projects/github/pradeep-ganesan/'+
        'SetCardinalityEstimators/flajoletmartin/essay.txt')

    print(
        'Total items: {} \nDistinct items count: {}\n'.format(
            estimator.total_size(),
            estimator.distinct_count()
            )
    )

    print('Flajolet-Martin counts')
    r = 16
    while r <= 8192:
        print('Estimated count for m[{}]: {}'.format(r, estimator.estimate_cardinality(r)))
        #estimator.cleanup()
        r *= 2

if __name__ == '__main__':
    main()


