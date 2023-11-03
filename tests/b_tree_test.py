import unittest
import bisect
from b_tree.main import BTree


class TestBTree(unittest.TestCase):
    def test_binary_search_insection_index_same_as_bisect_left(self):
        btree = BTree()
        l = [1, 2, 2, 5, 6, 7, 8, 9, 9, 13, 15, 20]

        for i in range(-1, 25):
            actual_idx = btree._bisect_left(l, i)
            expected_idx = bisect.bisect_left(l, i)
            self.assertEqual(expected_idx, actual_idx)

    # def test_insert_root_leaf_should_be_sorted(self):
    #     btree = BTree(5)
    #     btree.insert(1)
    #     btree.insert(5)
    #     btree.insert(2)
    #     btree.insert(3)

    #     self.assertEqual([1, 2, 3, 5], btree._root.keys)


if __name__ == '__main__':
    unittest.main()
