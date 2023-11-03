def bisect_left(list, key):
    """
    It finds the first separator key that is greater than the searched value.
    """
    lo = 0
    hi = len(list)

    while lo < hi:
        mid = (int)(lo + (hi - lo) / 2)

        if list[mid] and list[mid] < key:
            lo = mid + 1
        else:
            hi = mid

    return lo
