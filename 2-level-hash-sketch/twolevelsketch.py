import math
import farmhash
import logging
import streamproperty
from ... import dvc

logme = logging.getLogger('estimator')

class TwoLevelSketch(dvc.DVC):
    """Ganguly et al 2-level hash sketch for
    distinct value estimation"""

    FLAJOLET_MARTIN_PHI = 1.2928

    def __init__(
            self,
            sketchsize=64,
            numhash=256,
            epsilon=0.05,
            beta=1.05,
            sid=None
    ):
        def find_sketchsets():
            "calculate r"
            pass

        super(TwoLevelSketch, self).__init__(sid)
        self.epsilon = epsilon
        self.beta = beta
        self.union_estimate = None
        self.numhash = numhash
        self.sketchsets = 8

        self.bitsketchsize = sketchsize
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        for i in range(0, self.sketchsets):
            self.bitsketchset.append([0] * self.bitsketchsize * self.numhash)
            self.bitsketchsetcounter.append(
                [0] * (self.bitsketchsize + 1) * self.numhash
            )
        #self.bitsketch = [0] * self.bitsketchsize * self.numhash
        #self.sketchcounter = [0] * (self.bitsketchsize + 1) * self.numhash
        if __debug__:
            self.dataitems = []
            self.distinctitems = set()

    def add(self, item):
        self.update_sketch(item)

        if __debug__:
            self.dataitems.append(item)
            self.distinctitems.add(item)

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
        h_n = self.sketchsets * self.numhash
        for skset in range(0, self.sketchsets):
            for r in range(0, self.numhash):
                h = get_hash(item, h_n)
                try:
                    pos = least_sig_1bit(h)
                    self.bitsketchset[skset][r * self.bitsketchsize + pos] = 1
                    self.bitsketchsetcounter[skset][r * (self.bitsketchsize+1)] += 1
                    self.bitsketchsetcounter[skset][
                        r * (self.bitsketchsize+1) + (pos+1)
                    ] += 1
                except IndexError:
                    logme.error(
                        'index error at : %d %d for hash %s',
                        r, pos, h
                    )
                h_n -= 1

    def __len__(self):
        """flajoletmartin cardinality estimation"""
        R = 0.0

        # estimate the count of distinct values
        total, leftmostzero = 0.0, self.bitsketchsize
        for skset in range(0, self.sketchsets):
            for r in range(0, self.numhash):
                for m in range(0, self.bitsketchsize, 1):
                    if not self.bitsketchset[skset][r*self.bitsketchsize+m]:
                        leftmostzero = m
                        break
                total += leftmostzero
            R += self.FLAJOLET_MARTIN_PHI * pow(2.0, total/float(self.numhash))

        return R/float(skset)

    def __and__(self, other):
        """estimate for |A^B|"""
        def atomic_intersect_estimator(skset):
            index = int(
                math.log(
                    (self.beta - (
                        self.union_estimate
                        )
                    ) / (1.0 - self.epsilon)
                )
            )
            if not streamproperty.singleton_union(self, other, skset, index):
                return None
            estimate = 0.0
            if(
                    streamproperty.singleton(self, skset, index) and
                    streamproperty.singleton(other, skset, index)
            ):
                estimate = 1.0
            return estimate

        total, count = 0.0, 0.0
        for skset in range(0, self.sketchsets):
            atomic_estimate = atomic_intersect_estimator(skset)
            if atomic_estimate is not None:
                total += atomic_estimate
                count += 1.0
        return total * self.union_estimate / count

    def __or__(self, other):
        f = (1.0 + self.epsilon) * float(self.bitsketchsize / 8.0)
        index = 0
        while True:
            count = 0.0
            for skset in range(0, self.sketchsets):
                if(
                        not streamproperty.empty(self, skset, index) or
                        not streamproperty.empty(other, skset, index)
                ):
                    count += 1.0
            if count <= f:
                break
            index += 1

        p = count / float(index)
        R = pow(2.0, float(index + 1))
        return math.log((1.0 - p), 2)/math.log((1.0 - (1.0/R)), 2)

    def set_diff_estimator(self, other, union_estimate):
        """estimate for |A-B|"""

        def atomic_diff_estimator(skset):
            index = int(
                math.log(
                    (self.beta - (
                        self.union_estimate or union_estimate
                        )
                    ) / (1.0 - self.epsilon)
                )
            )
            if not streamproperty.singleton_union(self, other, skset, index):
                return None
            estimate = 0.0
            if(
                    streamproperty.singleton(self, skset, index) and
                    streamproperty.empty(other, skset, index)
            ):
                estimate = 1.0
            return estimate

        total, count = 0.0, 0.0
        for skset in range(0, self.sketchsets):
            atomic_estimate = atomic_diff_estimator(skset)
            if atomic_estimate is not None:
                total += atomic_estimate
                count += 1.0
        return total * (self.union_estimate or union_estimate) / count

    def clear(self):
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        if __debug__:
            self.dataitems = []
            self.distinctitems.clear()

    def copy(self, sourcestream):
        self.bitsketchsize = sourcestream.bitsketchsize
        self.numhash = sourcestream.numhash
        self.sketchsets = sourcestream.sketchsets
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        for skset in range(0, self.sketchsets):
            self.bitsketchset.append(sourcestream.bitsketchset[skset][:])
            self.bitsketchsetcounter.append(sourcestream.bitsketchsetcounter[skset][:])
        if __debug__:
            self.dataitems = sourcestream.dataitems[:]
            self.distinctitems = set(sourcestream.distinctitems)

    def relative_error(self):
        """error rate: x%>0 indicates estimate more than actual by x%
                       x%<0 indicates estimate less than actual by x%
                       x%==0 indicates estimate==actual"""
        if __debug__:
            err_percent = (
                float(
                    len(self) - self.distinct_items()
                ) / float(
                    self.distinct_items()
                )
            )
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
        print('Error rate: {}%'.format(get_continuous_stream.estimator.relative_error()))

if __name__ == '__main__':
    main()
