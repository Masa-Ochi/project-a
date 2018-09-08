import numpy as np
import math
import pickle
import _pickle as cPickle
import time
import os
import sys
import datetime
import investing_info as ii
import matplotlib.pyplot as plt

import tensorflow as tf
from keras import backend as K
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras.layers import LSTM
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score


import numba 
from numba import prange
import gc

range_num = 30
it_num    = 3000
process_num = 8

Target_name = ["Electronics", "電気機器"]
repo_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/tmp_%d"%range_num
pkls_path   = os.path.join(repo_path, "pkls/" + Target_name[0])
npys_path   = os.path.join(repo_path, "npys/" + Target_name[0])
models_path = os.path.join(repo_path, "models/" + Target_name[0])

if not(os.path.isdir(pkls_path)):
	os.makedirs(pkls_path)
if not(os.path.isdir(npys_path)):
	os.makedirs(npys_path)
if not(os.path.isdir(models_path)):
	os.makedirs(models_path)

def df_to_array(df):
	columns = df.columns
	id_lst = df.loc[:,"stock_id"].drop_duplicates().tolist()
	array = []
	for i in id_lst:
		tmp_df = df.loc[df["stock_id"]==i,:]
		tmp_a = []
		for c_idx in range(len(columns)):
			tmp_a.append(tmp_df[columns[c_idx]].tolist())
		array.append(tmp_a)
	return array

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

class source_data_set(object):
	def __init__(self,
				 base_arr,
				 x_cols, 
				 x_cols_idx,
				 y_cols,
				 y_cols_idx,
				 id_lst,
				 ):
		self.base_arr   = base_arr
		self.x_cols     = x_cols
		self.x_cols_idx = x_cols_idx
		self.y_cols     = y_cols
		self.y_cols_idx = y_cols_idx
		self.id_lst     = id_lst


