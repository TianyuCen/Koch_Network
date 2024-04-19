import numpy as np


def zeroSupplement(bitArray):
    if len(bitArray) == 3:
        return bitArray
    elif len(bitArray) < 3:
        for i in range(0, 3 - len(bitArray)):
            bitArray = np.insert(bitArray, 0, False)       # Supply 0 at top
        return bitArray
    else:
        raise IndexError("Please check the dimension of your koch network.")


def inputTransform(addr):       # Turn address into the form of keys
    del addr[len(addr) - 1]
    del addr[len(addr) - 1]     # Remove the last subscript pair
    if " " in addr:
        addr.insert(0, "[")
        addr.insert(-1, "]")
        addr = "".join(addr)
        return addr
    else:
        i = 1
        while True:
            addr.insert(i, " ")      # Insert space between numbers
            i += 2
            if i >= len(addr):
                addr.insert(0, "[")
                addr.insert(len(addr), "]")
                addr = "".join(addr)
                return addr
