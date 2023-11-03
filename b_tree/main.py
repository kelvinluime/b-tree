from b_tree.utils import bisect


class _BTreeNode:
    def __init__(self, order: int):
        self.num_keys = 0
        self.keys = [None] * (order - 1)
        self.children = [None] * order
        self.leaf = False
        self.parent = None
        self.order = order

    def is_full(self):
        return self.num_keys == self.order - 1

    def add_key(self, key: int) -> bool:
        if self.is_full():
            raise ValueError(f'Node is full. Unable to add key {key}.')

        index = bisect.bisect_left(self.keys, key)

        for i in range(self.num_keys, index, -1):
            self.keys[i] = self.keys[i - 1]

        self.keys[index] = key
        self.num_keys += 1

    def remove_child(self, node: '_BTreeNode') -> bool:
        if not node:
            raise ValueError(f'Node is None. Unable to remove child.')

        for i in range(self.num_keys + 1):
            if self.children[i] == node:
                self.children[i] = None
                return True

        return False


class BTree:
    def __init__(self, order: int = 5):
        self._root = None
        self.order = order

    def insert(self, key: int):
        if not self._root:
            self._root = _BTreeNode(self.order)
            self._root.leaf = True

        self._insert_key_to_leaf(self._root, key)

    def search(self, key: int) -> _BTreeNode:
        return self._search_key_from_node(self._root, key)

    def _search_key_from_node(self, node: _BTreeNode, key: int) -> _BTreeNode:
        if not node or node.num_keys == 0:
            return None

        if node.leaf:
            # rewrite with binary search to optimize
            return node if key in node.keys else None

        """
        Order:    4
        keys:     [          10,       20,        30        ]
        children: [(-inf, 10], (10, 20], (20, 30], (30, inf]]

        1. children[i] < keys[i] and keys[i] <= children[i + 1] < keys[i + 1]
            if i > 0 and i < order - 1
        2. children[0] < keys[0] 
        3. children[order - 1] >= keys[order - 2]
        """
        i = self._binary_search_insection_index(node.keys, key)
        if key >= node.keys[i]:
            i += 1

        return self._search_key_from_node(node.children[i], key)

    def _insert_key_to_leaf(self, root: _BTreeNode, key: int):
        if not root:
            raise ValueError(f'Node is None. Unable to insert key {key}.')
        
        print(f'Inserting {key} to {root.keys}')

        if root.leaf:
            if root.is_full():
                print(f'Leaf is full. Splitting leaf.')
                self._split_node(root, [key])
            else:
                print(f'Node is leaf. Inserting {key} to {root.keys}')
                root.add_key(key)
        else:
            index = 0
            if root.num_keys == 0 or key > root.keys[0]:
                index = bisect.bisect_left(root.keys, key)

            if not root.children[index]:
                root.children[index] = _BTreeNode(self.order)
                root.children[index].leaf = True

            print(f'Node is not leaf, continue to traverse to {root.children[index].keys} to insert {key}')

            self._insert_key_to_leaf(root.children[index], key)

    def _split_node(self, node: _BTreeNode, additional_keys: list = []):
        all_keys = self._merge_lists_sorted(node.keys, additional_keys)

        print(f'Splitting node {node.keys} with additional keys {additional_keys} -> {all_keys}')

        if not node.is_full():
            raise ValueError(f'Node is not full. Unable to split node.')

        mid = (int)(len(all_keys) / 2) - 1
        left_node = _BTreeNode(self.order)
        for i in range(mid + 1):
            left_node.keys[i] = all_keys[i]
            left_node.num_keys += 1
        left_node.leaf = node.leaf

        right_node = _BTreeNode(self.order)
        for i in range(mid + 1, len(all_keys)):
            right_node.keys[i - mid - 1] = all_keys[i]
            right_node.num_keys += 1
        right_node.leaf = node.leaf

        print(f'Splitted to left node {left_node.keys} and right node {right_node.keys}')

        if not node.parent:
            print(f'Node {node.keys} is root. Creating new root.')
            node.parent = _BTreeNode(self.order)
            node.parent.leaf = False
            self._root = node.parent
        else:
            node.parent.remove_child(node)

        is_parent_split = False
        if node.parent.is_full():
            print(f'Parent {node.parent.keys} is full. Splitting parent.')
            parent = self._split_node(node.parent, [all_keys[mid]])
            node.parent = parent
            print(f'Parent is splitted to {node.parent.keys}.')
            is_parent_split = True
        else:
            node.parent.add_key(all_keys[mid])

        left_idx = bisect.bisect_left(node.parent.keys, all_keys[mid])
        node.parent.children[left_idx] = left_node
        node.parent.children[left_idx + 1] = right_node
        print(f'Left node {left_node.keys} and right node {right_node.keys} are added to parent {node.parent.keys} with bisect index {left_idx}.')

        left_node.parent = node.parent
        right_node.parent = node.parent

        if not node.leaf:
            for i in range(mid + 1):
                if node.children[i]:
                    left_node.children[i] = node.children[i]
                    left_node.children[i].parent = left_node
                    print(f'Child {left_node.children[i].keys} is added to left node {left_node.keys} at index {i}.')

            if is_parent_split == False:
                print(f'Parent was not splitted.')
                for i in range(mid + 1, len(node.children)):
                    if node.children[i]:
                        right_node.children[i - mid - 1] = node.children[i]
                        right_node.children[i - mid - 1].parent = right_node
                        print(f'Child {right_node.children[i - mid - 1].keys} is added to right node {right_node.keys} at index {i - mid - 1}.')
            else:
                print(f'Parent was splitted.')
                for i in range(mid + 1, len(node.children)):
                    if node.children[i]:
                        right_node.children[i - mid] = node.children[i]
                        right_node.children[i - mid].parent = right_node
                        print(f'Child {right_node.children[i - mid].keys} is added to right node {right_node.keys} at index {i - mid}.')

        return left_node

    def _merge_lists_sorted(self, list1: list, list2: list) -> list:
        if not list1:
            return list2
        if not list2:
            return list1

        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i] < list2[j]:
                result.append(list1[i])
                i += 1
            else:
                result.append(list2[j])
                j += 1

        if i < len(list1):
            result += list1[i:]
        if j < len(list2):
            result += list2[j:]

        return result


if __name__ == '__main__':
    btree = BTree(4)
    btree.insert(5)
    btree.insert(2)
    btree.insert(10)
    btree.insert(30)
    btree.insert(20)
    btree.insert(35)
    btree.insert(27)
    btree.insert(21)
    btree.insert(19)
    btree.insert(13)

    print(f'root: {btree._root.keys}')
    for i in range(btree._root.num_keys + 1):
        print(f'child {i}: {btree._root.children[i].keys} (num_keys={btree._root.children[i].num_keys})')

        for j in range(btree._root.children[i].num_keys + 1):
            print(
                f'grandchild {i}.{j}: {btree._root.children[i].children[j].keys} (num_keys={btree._root.children[i].children[j].num_keys})')
