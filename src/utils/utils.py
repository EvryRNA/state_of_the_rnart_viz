from typing import List


def get_unique_list(in_list: List) -> List:
    """
    Return the list with unique values.
    It has to be ordered.
    :param in_list:
    :return:
    """
    out_list = []
    for item in in_list:
        if item not in out_list:
            out_list.append(item)
    return out_list
