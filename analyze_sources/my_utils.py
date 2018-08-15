import numpy as np
import math
import pickle
import _pickle as cPickle
import time
import os
import sys
from datetime import datetime, timedelta
import investing_info as ii
import matplotlib.pyplot as plt




# Ref: http://moritamori.hatenablog.com/entry/pickle_big_data
def save_as_pickled_object(obj, filepath):
    max_bytes = 2**31 - 1
    bytes_out = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    n_bytes = sys.getsizeof(bytes_out)
    with open(filepath, 'wb') as f_out:
        for idx in range(0, n_bytes, max_bytes):
            f_out.write(bytes_out[idx:idx+max_bytes])

def try_to_load_as_pickled_object_or_None(filepath):
    max_bytes = 2**31 - 1
    try:
        input_size = os.path.getsize(filepath)
        bytes_in = bytearray(0)
        with open(filepath, 'rb') as f_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += f_in.read(max_bytes)
        obj = cPickle.loads(bytes_in)
    except:
        return None
    return obj
