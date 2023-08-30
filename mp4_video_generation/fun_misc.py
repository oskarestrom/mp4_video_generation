import numpy as np

def find_nearest(array, value):
    """[Finds the index with the closest value to "value" in the array "array"]

    Args:
        array ([type]): [description]
        value ([type]): [description]

    Returns:
        [type]: [description]
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def print_dic(d):    
    for key,value in d.items():
        print(f'\t{key}: {value}')
    print('\n')