import unittest
import flajoletmartin.flajolet

class FMTests(unittest.TestCase):

    def test_fm(self):
        estimator = flajoletmartin.flajolet.FlajoletMartin(
            './testfile.txt', 32
        )
        print(
            'Total items: {} \nDistinct items count: {}\n'.format(
                estimator.total_size(),
                estimator.distinct_count()
            )
        )
        print('Flajolet-Martin counts')
        r = 16
        while r <= 1024:
            cardinality = estimator.estimate_cardinality(r)
            print(
                'Estimated count for m[{}]: {}'.format(
                    r,
                    cardinality
                    )
            )
            self.assertAlmostEqual(
                estimator.distinct_count(),
                cardinality,
                delta=estimator.total_size()*0.1
            )
            r *= 2

if __name__ == '__main__':
    unittest.main()
