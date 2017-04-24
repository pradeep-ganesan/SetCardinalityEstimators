import unittest
import twolevelhashsketch.twolevelsketch

class TLHSTests(unittest.TestCase):

    def setup(self, filename):
        estimator = twolevelhashsketch.twolevelsketch.TwoLevelSketch(sketchsize=64, numhash=16, epsilon=0.40)
        with open(filename) as fp:
            for line in fp:
                for word in line.split():
                    estimator.add(word)
        return estimator

    def test_generatesketch(self):
        estimator = self.setup('./testfile1.txt')

    def test_cardinality(self):
        estimator = self.setup('./testfile1.txt')
        print('\ntotal items                : {}'.format(estimator.total_items()))
        print('actual distinct items        : {}'.format(estimator.distinct_items()))
        print('estimated cardinality [r=64] : {}'.format(len(estimator)))

        estimator = self.setup('./testfile2.txt')
        print('\ntotal items                : {}'.format(estimator.total_items()))
        print('actual distinct items        : {}'.format(estimator.distinct_items()))
        print('estimated cardinality [r=64] : {}'.format(len(estimator)))

    def test_unionestimate(self):
        print('\nBuilding sketchA')
        sketchA = self.setup('./testfile1.txt')
        print('Building sketchB')
        sketchB = self.setup('./testfile2.txt')

        print('actual union cardinality  : {}'.format(len(sketchA.distinctitems | sketchB.distinctitems)))
        print('union estimate cardinality: {}'.format(sketchA | sketchB))

    def test_intersectestimate(self):
        print('\nBuilding sketchA')
        sketchA = self.setup('./testfile1.txt')
        print('Building sketchB')
        sketchB = self.setup('./testfile2.txt')

        print('actual intersection cardinality  : {}'.format(len(sketchA.distinctitems & sketchB.distinctitems)))
        print('intersection estimate cardinality: {}'.format(sketchA & sketchB))

if __name__ == '__main__':
    unittest.main()
