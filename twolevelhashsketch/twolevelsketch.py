import math, farmhash, logging
import log
import streamproperty
import dvc

log.initialize()
logme = logging.getLogger('estimator')

class TwoLevelSketch(dvc.DVC):
    """Ganguly et al 2-level hash sketch for
    distinct value estimation VLDB05"""

    FLAJOLET_MARTIN_PHI = 1.2928

    def __init__(
            self,
            sketchsize=64,
            numhash=64,
            epsilon=0.95,
            beta=2.0,
            sid=None,
            debug=True
    ):
        def find_sketchsets():
            "calculate r"
            pass

        super(TwoLevelSketch, self).__init__(sid)
        self.epsilon = epsilon
        self.beta = beta
        self.union_estimate = None
        # number of hash functions
        self.sketchsets = numhash

        self.bitsketchsize = sketchsize
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        for _ in range(0, self.sketchsets):
            self.bitsketchset.append([0] * self.bitsketchsize)
            self.bitsketchsetcounter.append(
                [0] * (self.bitsketchsize + 1) * self.bitsketchsize
            )
        self.debug = debug
        if debug:
            self.dataitems = []
            self.distinctitems = set()

    def add(self, item):
        self.update_sketch(item)

        if self.debug:
            self.dataitems.append(item)
            self.distinctitems.add(item)

    def total_items(self):
        """total items"""
        return len(self.dataitems) if self.debug else None

    def distinct_items(self):
        """actual number of distinct items"""
        return len(self.distinctitems) if self.debug else None

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
            return self.bitsketchsize if not h else (h&-h).bit_length()-1

        # update bitsketch and sketch counters
        for r in range(0, self.sketchsets):
            h = get_hash(item, r)
            try:
                pos = least_sig_1bit(h)
                self.bitsketchset[r][pos] = 1
                for i in range(self.bitsketchsize, 0, -1):
                    bit = h%2
                    h = h>>1
                    if bit:
                        self.bitsketchsetcounter[r][pos * (self.bitsketchsize+1)] += 1
                        self.bitsketchsetcounter[r][
                            pos * (self.bitsketchsize+1) + (i-1)
                        ] += 1
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
        for r in range(0, self.sketchsets):
            for m in range(0, self.bitsketchsize, 1):
                if not self.bitsketchset[r][m]:
                    leftmostzero = m
                    break
            total += leftmostzero
        R += self.FLAJOLET_MARTIN_PHI * pow(2.0, total/float(self.sketchsets))
        return R

    def __and__(self, other):
        """estimate for |A ^ B|"""
        assert self.bitsketchsize == other.bitsketchsize
        assert self.sketchsets == other.sketchsets
        self.union_estimate = (self | other)
        def atomic_intersect_estimator(sketchcountersA, sketchcountersB):
            index = int(
                math.log(
                    (self.beta * self.union_estimate)
                    / (1.0 - self.epsilon)
                )
            )
            logme.debug('index : %d', int(index))
            logme.info('sketchA %s', sketchcountersA[index * (self.bitsketchsize+1) : index * (self.bitsketchsize+1) + self.bitsketchsize])
            logme.info('sketchB %s', sketchcountersB[index * (self.bitsketchsize+1) : index * (self.bitsketchsize+1) + self.bitsketchsize])
            if not streamproperty.singleton_union(
                    sketchcountersA, sketchcountersB, self.bitsketchsize, index
                ):
                logme.debug('No estimate for index: %d', int(index))
                return None
            estimate = 0.0
            if(
                    streamproperty.singleton(sketchcountersA, self.bitsketchsize, index) and
                    streamproperty.singleton(sketchcountersB, self.bitsketchsize, index)
            ):
                estimate = 1.0
            logme.debug('Estimate for index: %d', int(index))
            return estimate

        total, count = 0.0, 0.0
        for r in range(0, self.sketchsets):
            atomic_estimate = atomic_intersect_estimator(
                self.bitsketchsetcounter[r], other.bitsketchsetcounter[r]
            )
            if atomic_estimate is not None:
                total += atomic_estimate
                count += 1.0
        logme.debug('sum = %f count = %f', total, count)
        return total * self.union_estimate / count if total and count else 0.0

    def __or__(self, other):
        """estimate for |A U B|"""
        assert self.bitsketchsize == other.bitsketchsize
        assert self.sketchsets == other.sketchsets

        f = (1.0 + self.epsilon) * float(self.sketchsets / 8.0)
        index = 0
        while True:
            count = 0.0
            for r in range(0, self.sketchsets):
                if(
                        not streamproperty.empty(self.bitsketchsetcounter[r], self.bitsketchsize, index) or
                        not streamproperty.empty(other.bitsketchsetcounter[r], self.bitsketchsize, index)
                ):
                    count += 1.0
            if count <= f:
                break
            index += 1
            #logme.debug('bucket index: %d', index)

        p = count / float(self.sketchsets)
        R = pow(2.0, float(index + 1))
        return math.log((1.0 - p), 2)/math.log((1.0 - (1.0/R)), 2)

    def set_diff_estimator(self, other, union_estimate):
        """estimate for |A - B|"""
        assert self.bitsketchsize == other.bitsketchsize
        assert self.sketchsets == other.sketchsets

        def atomic_diff_estimator(sketchcountersA, sketchcountersB):
            index = int(
                math.log(
                    (self.beta * (self.union_estimate or union_estimate))
                    / (1.0 - self.epsilon)
                )
            )
            if not streamproperty.singleton_union(
                    sketchcountersA, sketchcountersB, self.bitsketchsize, index
                ):
                return None
            estimate = 0.0
            if(
                    streamproperty.singleton(sketchcountersA, self.bitsketchsize, index) and
                    streamproperty.empty(sketchcountersB, self.bitsketchsize, index)
            ):
                estimate = 1.0
            return estimate

        total, count = 0.0, 0.0
        for r in range(0, self.sketchsets):
            atomic_estimate = atomic_diff_estimator(
                self.bitsketchsetcounter[r], other.bitsketchsetcounter[r]
            )
            if atomic_estimate is not None:
                total += atomic_estimate
                count += 1.0
        return total * (self.union_estimate or union_estimate) / count

    def clear(self):
        """reset sketches"""
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        if self.debug:
            self.dataitems = []
            self.distinctitems.clear()

    def copy(self, sourcestream):
        """full copy of sketches"""
        self.bitsketchsize = sourcestream.bitsketchsize
        self.sketchsets = sourcestream.sketchsets
        self.bitsketchset = []
        self.bitsketchsetcounter = []
        for r in range(0, self.sketchsets):
            self.bitsketchset.append(list(sourcestream.bitsketchset[r][:]))
            self.bitsketchsetcounter.append(list(sourcestream.bitsketchsetcounter[r][:]))
        if self.debug:
            self.dataitems = list(sourcestream.dataitems[:])
            self.distinctitems = set(sourcestream.distinctitems)

    def relative_error(self):
        """error : x%>0 indicates estimate more than actual by x%
                   x%<0 indicates estimate less than actual by x%
                   x%==0 indicates estimate==actual"""
        if self.debug:
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
    if get_continuous_stream.estimator.debug:
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
    if get_continuous_stream.estimator.debug:
        print('Error rate: {}%'.format(get_continuous_stream.estimator.relative_error()))

if __name__ == '__main__':
    main()
