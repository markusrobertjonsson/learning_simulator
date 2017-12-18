import unittest

import LsUtil


class TestLsUtil(unittest.TestCase):
    def setUp(self):
        pass

    def iseq(self, d1, d2):
        for _, val in d1.items():
            val.sort()
        for _, val in d2.items():
            val.sort()
        self.assertEqual(d1, d2)

    def test_dict_inv(self):
        d = {'a': ['x', 'y'], 'b': ['x', 'y', 'z'], 'c': 'w'}
        dinv = LsUtil.dict_inv(d)
        expected = {'w': ['c'], 'x': ['b', 'a'], 'y': ['b', 'a'], 'z': ['b']}
        self.iseq(dinv, expected)

        d = {}
        dinv = LsUtil.dict_inv(d)
        expected = {}
        self.iseq(dinv, expected)

        d = {2: '2', '3': '3'}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {2: [2, 3, 'j'], '3': ['a', 'b', 'c']}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {'A': ''}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {'': 'A'}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)
