import numpy as np


def zero_supplement(bitArray):
    if len(bitArray) == 3:
        return bitArray
    elif len(bitArray) < 3:
        for i in range(0, 3 - len(bitArray)):
            bitArray = np.insert(bitArray, 0, False)  # Supply 0 at top
        return bitArray
    else:
        raise IndexError("Please check the dimension of your koch network.")


def input_transform(addr):
    """
    Eg：["1", "0", "2", "1"] -> "[1 0 2 1]"
    """
    return "[" + " ".join(addr) + "]"