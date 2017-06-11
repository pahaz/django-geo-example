ANYTHING = 'ANYTHING'


def contains(container, contained):
    """ensure that `contained` is present somewhere in `container`
    
    https://stackoverflow.com/a/36977699/941020

    EXAMPLES:

    contains(
        {'a': 3, 'b': 4},
        {'a': 3}
    ) # True

    contains(
        {'a': [3, 4, 5]},
        {'a': 3},
    ) # True

    contains(
        {'a': 4, 'b': {'a':3}},
        {'a': 3}
    ) # True

    contains(
        {'a': 4, 'b': {'a':3, 'c': 5}},
        {'a': 3, 'c': 5}
    ) # True

    # if an `contained` has a list, then every item from that list must be present
    # in the corresponding `container` list
    contains(
        {'a': [{'b':1}, {'b':2}, {'b':3}], 'c':4},
        {'a': [{'b':1},{'b':2}], 'c':4},
    ) # True

    # You can also use the string literal 'ANYTHING' to match anything
        contains(
        {'a': [{'b':3}]},
        {'a': 'ANYTHING'},
    ) # True

    # You can use 'ANYTHING' as a dict key and it indicates to match the corresponding value anywhere
    # below the current point
    contains(
        {'a': [ {'x':1,'b1':{'b2':{'c':'SOMETHING'}}}]},
        {'a': {'ANYTHING': 'SOMETHING', 'x':1}},
    ) # True

    contains(
        {'a': [ {'x':1, 'b':'SOMETHING'}]},
        {'a': {'ANYTHING': 'SOMETHING', 'x':1}},
    ) # True

    contains(
        {'a': [ {'x':1,'b1':{'b2':{'c':'SOMETHING'}}}]},
        {'a': {'ANYTHING': 'SOMETHING', 'x':1}},
    ) # True
    """

    if contained == ANYTHING:
        return True

    if container == contained:
        return True

    if isinstance(container, list):
        if not isinstance(contained, list):
            contained = [contained]
        true_count = 0
        for contained_item in contained:
            for item in container:
                if contains(item, contained_item):
                    true_count += 1
                    break
        if true_count == len(contained):
            return True

    if isinstance(contained, dict) and isinstance(container, dict):
        contained_keys = set(contained.keys())
        if ANYTHING in contained_keys:
            contained_keys.remove(ANYTHING)
            if not contains(container, contained[ANYTHING]):
                return False

        container_keys = set(container.keys())
        if len(contained_keys - container_keys) == 0:
            if all(
                    contains(container[key], contained[key])
                    for key in contained_keys
            ):
                return True

    # well, we're here, so I guess we didn't find a match yet
    if isinstance(container, dict):
        for value in container.values():
            if contains(value, contained):
                return True

    return False


class AssertionsMixin:
    def assertContainsSubset(self, container, contained):
        self.assertTrue(contains(container, contained))
