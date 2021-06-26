from typing import Iterable


def order_set_by_iterable(s: Iterable, it: Iterable) -> list:
    return [i for i in it if i in s]
