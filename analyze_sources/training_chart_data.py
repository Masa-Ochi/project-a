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


# market_json = {
# 	{"name": "東証一部", "id": "Tosho1bu"},
# 	{"name": "JASDAQｽﾀﾝﾀﾞｰﾄﾞ", "id": "Jasdaq_s"},
# 	{"name": "東証二部", "id": "Tosho2bu"},
# 	{"name": "東証ﾏｻﾞｰｽﾞ", "id": "Tosho_m"},
# }


# "サービス業"
# "その他金融"
# "商社"
# "小売業"
# "電気機器"
# "機械"
# "化学工業"
# "建設"
# "食品"
# "非鉄金属及び金属製品"
# "不動産"
# "その他製造業"
# "銀行"
# "自動車・自動車部品"
# "医薬品"
# "窯業"
# "精密機器"
# "鉄鋼業"
# "繊維"
# "倉庫・運輸関連"
# "陸運"
# "通信"
# "鉄道・バス"
# "パルプ・紙"
# "証券"
# "ゴム"
# "海運"
# "電力"
# "その他輸送機器"
# "石油"
# "保険"
# "水産"
# "ガス"
# "鉱業"
# "造船"
# "空運"


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




class source_data_set_mgr(object):

	def __init__(self):
		print("Initialized...")

	def set_ii_obj_by_stock_market(self, stock_market, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31)):
		self.ii_obj = ii.get_ii_obj_by_stock_market(stock_market, from_date, to_date) # Set True at 2nd arg is to avoid retrieving all charts.

	def set_ii_obj_by_stock_category(self, business_type, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31)):
		self.ii_obj = ii.get_ii_obj_by_category(business_type, from_date, to_date)

	def set_ii_obj_by_id_lst(self, id_lst, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31)):
		self.ii_obj = ii.investing_info(id_lst, from_date, to_date)

	def save_data(self, path=pkls_path):
		save_as_pickled_object(self.ii_obj,          os.path.join(path, "ii_obj.pkl"))
		save_as_pickled_object(self.base_cols,       os.path.join(path, "base_cols.pkl"))
		save_as_pickled_object(self.base_df,         os.path.join(path, "base_df.pkl"))
		save_as_pickled_object(self.source_data_set, os.path.join(path, "source_data_set.pkl"))

	def load_data(self, path=pkls_path):
		# self.ii_obj            = try_to_load_as_pickled_object_or_None(os.path.join(path, "ii_obj.pkl"))
		# self.base_cols         = try_to_load_as_pickled_object_or_None(os.path.join(path, "base_cols.pkl"))
		# self.base_df           = try_to_load_as_pickled_object_or_None(os.path.join(path, "base_df.pkl"))
		self.source_data_set   = try_to_load_as_pickled_object_or_None(os.path.join(path, "source_data_set.pkl"))

	def load_ii_obj(self, path=pkls_path):
		self.ii_obj = try_to_load_as_pickled_object_or_None(os.path.join(path, "ii_obj.pkl"))

	def load_source_data_set(self, path=pkls_path):
		self.source_data_set = try_to_load_as_pickled_object_or_None(os.path.join(path, "source_data_set.pkl"))

	def set_source_data_set(self):
		self.base_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		self.base_df = self.ii_obj.df.loc[:,self.base_cols] 

		base_arr = df_to_array(self.base_df)
		x_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		x_cols_idx = [self.base_cols.index(i) for i in x_cols]
		y_cols = ["open_price", "high_price", "low_price", "close_price"]
		y_cols_idx = [self.base_cols.index(i) for i in y_cols]
		
		id_lst = self.base_df.loc[:,"stock_id"].drop_duplicates().tolist()

		self.source_data_set = source_data_set(base_arr, x_cols, x_cols_idx, y_cols, y_cols_idx, id_lst)

	def plot_data(self, i):
		plt.plot(self.x_vals_test[i, 3, :], 'k-', label='Train xdata')
		plt.plot(self.y_vals_test[i, 3], 'ro', label='Test ydata')
		plt.plot(self.testPredict[i, 3], 'bo', label='Predict ydata')
		plt.legend(loc='upper right')
		plt.show()

	def load_model(self, path=models_path):
		self.model = load_model(path)

	def predict_ii_obj(self, model_path, r_num=range_num):
		self.set_source_data_set()
		self.load_model(model_path)
		x_data = []
		y_data = []
		for i in self.source_data_set.id_lst:
			tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==i, self.base_cols]
			max_price = tmp_df.loc[:, ["open_price", "high_price", "low_price", "close_price"]].max().max()
			tmp_df.loc[:, ["open_price", "high_price", "low_price", "close_price"]] = tmp_df.loc[:, ["open_price", "high_price", "low_price", "close_price"]] / max_price
			tmp_df.loc[:, ["output"]] = tmp_df.loc[:, ["output"]] / tmp_df.loc[:, ["output"]].max()
			tmp_l = len(tmp_df)
			# print(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1])

			# print(np.array(df_to_array(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1]))[0,2:7,:])
			# print(np.array(df_to_array(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1]))[0,2:7,:].reshape(len(self.source_data_set.x_cols), r_num).T)
			# print(np.array(df_to_array(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1])).shape)
			# print(np.array(df_to_array(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1]))[0,2:7,:].reshape(len(self.source_data_set.x_cols), r_num).T.shape)

			tmp_x = np.array(df_to_array(tmp_df.iloc[tmp_l-r_num-1:tmp_l-1]))[0,2:7,:].reshape(len(self.source_data_set.x_cols), r_num, 1).T
			tmp_y = np.array(df_to_array(tmp_df.iloc[tmp_l-1:tmp_l]))[0,2:7,:].reshape(len(self.source_data_set.x_cols), 1).T # To make a code simplly, using x_col for y...
			# print(tmp_x.shape)
			# print(tmp_y.shape)
			# x_data.append(tmp_x)
			# y_data.append(tmp_y)
			tmp_predict = self.model.predict(tmp_x)
			print("------- Target stock_id ---------")
			print(i)
			print("------- Mean Squared Error ---------")
			print(math.sqrt(mean_squared_error(tmp_predict,tmp_y)))
			print("--- Predict & Answer ----")
			print(tmp_predict)
			print(tmp_y)
			print("--- x & Predict & y ----")
			print(tmp_x[0,range_num-1:range_num,:]*max_price)
			print(tmp_predict*max_price)
			print(tmp_y*max_price)
			print("-------")
			print("--- Predict - x & y - x ----")
			print(tmp_predict*max_price - tmp_x[0,range_num-1:range_num,:]*max_price)
			print(tmp_y*max_price - tmp_x[0,range_num-1:range_num,:]*max_price)
			print("-------")

def prep_training_data(scd, seq=0):
	start = time.time()
	
	data_set_path = os.path.join(npys_path, 'whole_data_%d.npy'%(seq))
	data_set_num_lst_path = os.path.join(npys_path, 'data_set_num_lst_%d.npy'%(seq))

	if not(os.path.isfile(data_set_path) and os.path.isfile(data_set_num_lst_path)):
		print("--- [Create Data Set] ---")
		arr = []
		num_lst = []
		for i in range(len(scd.base_arr)):
			num_lst.append(len(scd.base_arr[i][0]))
			for c_idx in scd.x_cols_idx:
				arr.extend(scd.base_arr[i][c_idx])
		print(len(arr))

		data_set, data_set_num_lst = set_training_data_fast(num_lst, arr, scd.x_cols_idx, scd.y_cols_idx, seq)
		elapsed_time = time.time() - start
		print ("***** total_elapsed_time:{0}".format(elapsed_time) + "[sec]")

	else:
		print("--- [Load Data Set] ---")
		data_set = np.load(data_set_path)
		data_set_num_lst = np.load(data_set_num_lst_path)

	start = time.time()
	# x_cols_idx = scd.x_cols_idx
	# y_cols_idx = scd.y_cols_idx
	print("--- [Retrieve XY Data] ---")
	x_data, y_data, standard_x, standard_y, x_cols_idx, y_cols_idx = retrieve_xy_dataset(data_set, data_set_num_lst, scd.x_cols_idx, scd.y_cols_idx, seq)

	np.savez_compressed(os.path.join(npys_path, 'x_data_%d'%(seq)), x_data)
	np.savez_compressed(os.path.join(npys_path, 'y_data_%d'%(seq)), y_data)
	np.savez_compressed(os.path.join(npys_path, 'standard_x_%d'%(seq)), standard_x)
	np.savez_compressed(os.path.join(npys_path, 'standard_y_%d'%(seq)), standard_y)
	np.savez_compressed(os.path.join(npys_path, 'x_cols_idx_%d'%(seq)), x_cols_idx)
	np.savez_compressed(os.path.join(npys_path, 'y_cols_idx_%d'%(seq)), y_cols_idx)

	elapsed_time = time.time() - start
	print ("***** total_eelapsed_time:{0}".format(elapsed_time) + "[sec]")
	


@numba.jit(nopython=True)
def sum_lst(lst):
	rtn_val = 0
	for i in lst:
		rtn_val = rtn_val + i
	return rtn_val

@numba.jit(nopython=True)
def insert_lst(lst_a, lst_b):
	rtn_lst = np.zeros(len(lst_a) + len(lst_b))
	for i in range(len(lst_b)):
		rtn_lst[i] = lst_b[i]
	for j in range(len(lst_a)):
		rtn_lst[len(lst_b) + j] = lst_a[j]
	return rtn_lst

@numba.jit
def set_training_data_fast(num_lst, arr, x_cols_idx, y_cols_idx, seq=0):
# def set_training_data(self, seq=-1, input_id_lst="",from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31)):

	# Comment out to exec numba........
	# try:
	#     print("Length of raw_data: %s" % len(self.base_df))
	# except AttributeError:
	# 	self.ii_obj = ii.investing_info(input_id_lst, from_date, to_date)
	# 	self.base_df = self.ii_obj.df.loc[:,["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]] 

	data_set = np.zeros(len(num_lst) * len(x_cols_idx) * it_num * (range_num+1))
	cur_data_set_idx = 0
	num_lst_wk = insert_lst(num_lst, [0])
	data_set_num_lst = np.ones(len(num_lst)) * it_num

	start = time.time()
	for i in range(len(num_lst)):

		if num_lst[i] < range_num + 1:
			data_set_num = 0
			data_set_num_lst[i] = data_set_num
		else:
			data_set_num = min(num_lst[i] - (range_num + 1) + 1, it_num)
			data_set_num_lst[i] = data_set_num

			tmp_a = int(sum_lst(num_lst_wk[0:i+1]) * len(x_cols_idx))
			tmp_b = int(sum_lst(num_lst_wk[0:i+2]) * len(x_cols_idx))
			wk_arr = arr[tmp_a:tmp_b]

			## 1. Random data case --
			# print("**Data size: %d" % (min(len(wk_arr[0]) - (range_num + 1) + 1, it_num)))
			for n in range(data_set_num):
				r = np.random.randint(num_lst[i] - (range_num + 1) + 1)
			## 2. Whole data case ---
			# print("**Data size: %d" % (len(wk_arr[0]) - (range_num + 1)))
			# for n in range(len(wk_arr[0]) - (range_num + 1) + 1):
				# r = n

				for x_c_idx in range(len(x_cols_idx)):
					tmp_a = int(x_c_idx*num_lst[i])
					tmp_b = int((x_c_idx+1)*num_lst[i])
					wk_arr_col = wk_arr[tmp_a:tmp_b]

					data_set[cur_data_set_idx:cur_data_set_idx+range_num+1] = wk_arr_col[r:r+range_num+1]
					cur_data_set_idx = cur_data_set_idx + range_num + 1

		elapsed_time = time.time() - start
		if i % 20 == 0:
			print ("***** elapsed_time:{0}".format(elapsed_time) + "[sec] --%d / %d" % (i, len(num_lst)))
			start = time.time()


	data_set = data_set[0:int(sum_lst(data_set_num_lst) * len(x_cols_idx) * (range_num+1))]

	# repo_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/tmp"
	# seq = 0
	np.save(os.path.join(npys_path, 'whole_data_%d.npy'%(seq)), data_set)
	np.save(os.path.join(npys_path, 'data_set_num_lst_%d.npy'%(seq)), data_set_num_lst)

	return data_set, data_set_num_lst


# @numba.jit(nopython=True, parallel=True)
# @numba.jit(parallel=True)
# @numba.jit(nopython=True)
def retrieve_xy_dataset(data_set, data_set_num_lst, x_cols_idx, y_cols_idx, seq=0):

	#Standardize data
	x_size = int(sum_lst(data_set_num_lst) * len(x_cols_idx) * range_num)
	y_size = int(sum_lst(data_set_num_lst) * len(x_cols_idx)) # To calc easily, using x_cols_idx instead of y_cols_idx
	x_data = np.zeros(x_size)
	y_data = np.zeros(y_size)
	standard_x = np.zeros(x_size)
	standard_y = np.zeros(y_size)
	x_curr_idx = 0
	y_curr_idx = 0

	start = time.time()

	for i in range(int(sum_lst(data_set_num_lst))):

		tmp_a = int(i     * len(x_cols_idx) * (range_num+1))
		tmp_b = int((i+1) * len(x_cols_idx) * (range_num+1))
		wk_arr_for_st = data_set[int(tmp_a):int(tmp_b)] # Array of i's data set

		tmp_p = int((range_num+1)*(len(x_cols_idx)-1))
		tmp_max_price  = wk_arr_for_st[0:int(tmp_p)].max()
		tmp_max_output = wk_arr_for_st[int(tmp_p):int(len(wk_arr_for_st))].max()
		tmp_standard_prices = wk_arr_for_st[0:int(tmp_p)] / tmp_max_price
		tmp_standard_output = wk_arr_for_st[int(tmp_p):int(len(wk_arr_for_st))] / tmp_max_output

		tmp_standard_data_set = np.zeros(len(wk_arr_for_st), np.float64)
		tmp_standard_data_set[0:int(tmp_p)] = tmp_standard_prices
		tmp_standard_data_set[int(tmp_p):int(len(wk_arr_for_st))] = tmp_standard_output

		for c_idx in range(len(x_cols_idx)):
			tmp_c_a = c_idx * (range_num+1)
			tmp_c_b = (c_idx+1) * (range_num+1)
			wk_arr_col_for_st = wk_arr_for_st[tmp_c_a:tmp_c_b] # Array of 'c_idx's column
			st_arr_col_for_st = tmp_standard_data_set[tmp_c_a:tmp_c_b] # Array of 'c_idx's column

			x_data[x_curr_idx:x_curr_idx+range_num]     = wk_arr_col_for_st[0:range_num]
			standard_x[x_curr_idx:x_curr_idx+range_num] = st_arr_col_for_st[0:range_num]
			x_curr_idx = x_curr_idx + range_num

			y_data[y_curr_idx:y_curr_idx+1]     = wk_arr_col_for_st[range_num:range_num+1]
			standard_y[y_curr_idx:y_curr_idx+1] = st_arr_col_for_st[range_num:range_num+1]
			y_curr_idx = y_curr_idx + 1

		del tmp_standard_data_set
		del tmp_standard_output
		del tmp_standard_prices
		del wk_arr_for_st

		elapsed_time = time.time() - start
		if i % 100000 == 0:
			print ("***** elapsed_time:{0}".format(elapsed_time) + "[sec] --%d / %d" % (i, sum_lst(data_set_num_lst)))
			# print(x_data[i-range_num*10:i])
			# print(y_data[i-10:i])
			# print(standard_x[i-range_num*10:i])
			# print(standard_y[i-10:i])
			start = time.time()

	# print(x_data[i-range_num*10:i])
	# print(y_data[i-10:i])
	# print(standard_x[i-range_num*10:i])
	# print(standard_y[i-10:i])

	return x_data, y_data, standard_x, standard_y, x_cols_idx, y_cols_idx





@numba.jit(nopython=True)
# @numba.jit
def set_tr_te_data_wk(standard_x, standard_y, x_cols_idx, y_cols_idx, x_vals, y_vals, x_idx, y_idx, i):

		x_vals[x_idx:x_idx+len(x_cols_idx)*range_num] = standard_x[i*len(x_cols_idx)*range_num:(i+1)*len(x_cols_idx)*range_num]
		x_idx = x_idx + len(x_cols_idx) * range_num
		y_vals[y_idx:y_idx+len(x_cols_idx)]  = standard_y[i*len(x_cols_idx):(i+1)*len(x_cols_idx)]
		y_idx = y_idx + len(x_cols_idx)

		return x_vals, y_vals, x_idx, y_idx



@numba.jit
def set_tr_te_data(standard_x, standard_y, x_cols_idx, y_cols_idx, seq):

	# Set for reproducible results
	seed = 99
	np.random.seed(seed)
	tf.set_random_seed(seed)
	# x_data_set = standard_x.reshape(-1, len(x_cols_idx), range_num)
	# y_data_set_wk = standard_y.reshape(-1, len(x_cols_idx))
	data_num = int(len(standard_y) / len(x_cols_idx))
	# y_data_set = y_data_set_wk[:, 0:4]
	# print(y_data_set.shape)

	# Split data into train/test = 80%/20%
	# train_indices = np.random.choice(x_data_set.shape[0], round(x_data_set.shape[0]*0.8), replace=False)
	train_indices = np.random.choice(data_num, round(data_num*0.8), replace=False)
	print(train_indices)
	test_indices  = np.array(list(set(range(data_num)) - set(train_indices)))
	print(test_indices)
	# test_indices  = np.array(list(set(range(data_num)) - set(train_indices)))

	# x_vals_train = x_data_set[train_indices]
	# x_vals_test  = x_data_set[test_indices]
	# y_vals_train = y_data_set[train_indices]
	# y_vals_test  = y_data_set[test_indices]


	x_vals_train = np.zeros(len(train_indices)*len(x_cols_idx)*range_num)	
	y_vals_train = np.zeros(len(train_indices)*len(x_cols_idx))	
	x_vals_test = np.zeros(len(test_indices)*len(x_cols_idx)*range_num)	
	y_vals_test = np.zeros(len(test_indices)*len(x_cols_idx))	

	x_tr_idx = 0
	y_tr_idx = 0
	x_te_idx = 0
	y_te_idx = 0
	# data_num = int(len(standard_y) / len(x_cols_idx))

	print("*** Set training data")
	start = time.time()
	for i in range(len(train_indices)):
		x_vals_train, y_vals_train, x_tr_idx, y_tr_idx = set_tr_te_data_wk(standard_x, standard_y, x_cols_idx, y_cols_idx, x_vals_train, y_vals_train, x_tr_idx, y_tr_idx, i)

		elapsed_time = time.time() - start
		if i % 100000 == 0:
			print ("***** elapsed_time:{0}".format(elapsed_time) + "[sec] --%d / %d" % (i, len(train_indices)))
			# print(x_vals_train[x_tr_idx-10:x_tr_idx])
			# print("[%d, %d]"%(x_tr_idx, int(x_tr_idx/5)))
			start = time.time()

	# print(x_vals_train[x_tr_idx-10:x_tr_idx])
	# print("[%d, %d]"%(x_tr_idx, int(x_tr_idx/5)))

	print("*** Set test data")
	start = time.time()
	for i in range(len(test_indices)):
		x_vals_test, y_vals_test, x_te_idx, y_te_idx = set_tr_te_data_wk(standard_x, standard_y, x_cols_idx, y_cols_idx, x_vals_test, y_vals_test, x_te_idx, y_te_idx, i)

		elapsed_time = time.time() - start
		if i % 10000 == 0:
			print ("***** elapsed_time:{0}".format(elapsed_time) + "[sec] --%d / %d" % (i, len(test_indices)))
			start = time.time()

	# print("Set tr te data ***")
	# x_vals_train, y_vals_train, x_vals_test, y_vals_test = set_tr_te_data_wk(standard_x, standard_y, x_cols_idx, y_cols_idx, train_indices, test_indices)

	print(y_vals_train[len(y_vals_train)-10:len(y_vals_train)])
	print(y_vals_test[len(y_vals_test)-10:len(y_vals_test)])
	print(len(x_vals_train))
	print(len(y_vals_train))
	print(len(x_vals_test))
	print(len(y_vals_test))

	np.savez_compressed(os.path.join(npys_path, 'x_vals_train_%d'%(seq)), x_vals_train)
	np.savez_compressed(os.path.join(npys_path, 'x_vals_test_%d'%(seq)), x_vals_test)
	np.savez_compressed(os.path.join(npys_path, 'y_vals_train_%d'%(seq)), y_vals_train)
	np.savez_compressed(os.path.join(npys_path, 'y_vals_test_%d'%(seq)), y_vals_test)


@numba.jit(nopython=True)
def calc_lstm_wk(seq, train_start_pos, test_start_pos, target_num, x_cols_idx, x_vals_train_wk, x_vals_test_wk, y_vals_train_wk, y_vals_test_wk):

	train_num = int((len(x_vals_train_wk) / (len(x_cols_idx)*range_num)) * target_num)
	test_num = int((len(x_vals_test_wk) / (len(x_cols_idx)*range_num)) * target_num)

	x_vals_train_tmp = x_vals_train_wk[train_start_pos:train_start_pos + train_num * len(x_cols_idx) * range_num]
	y_vals_train_tmp = y_vals_train_wk[train_start_pos:train_start_pos + train_num * len(x_cols_idx)]
	x_vals_test_tmp  = x_vals_test_wk[test_start_pos:test_start_pos + test_num * len(x_cols_idx) * range_num]
	y_vals_test_tmp  = y_vals_test_wk[test_start_pos:test_start_pos + test_num * len(x_cols_idx)]

	return train_num, test_num, x_vals_train_tmp, x_vals_test_tmp, y_vals_train_tmp, y_vals_test_tmp

def calc_lstm(seq):

	train_start_pos  = 0
	test_start_pos  = 0
	target_num = 1

	print("*** Loading data set.....")
	# repo_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/tmp"
	x_cols_idx = np.load(os.path.join(npys_path, 'x_cols_idx_%d.npz'%(seq)))['arr_0']
	x_vals_train_wk = np.load(os.path.join(npys_path, 'x_vals_train_%d.npz'%(seq)))['arr_0']
	x_vals_test_wk  = np.load(os.path.join(npys_path, 'x_vals_test_%d.npz'%(seq)))['arr_0']
	y_vals_train_wk = np.load(os.path.join(npys_path, 'y_vals_train_%d.npz'%(seq)))['arr_0']
	y_vals_test_wk  = np.load(os.path.join(npys_path, 'y_vals_test_%d.npz'%(seq)))['arr_0']

	print("*** Arranging data set.....")
	train_num, test_num, x_vals_train_tmp, x_vals_test_tmp, y_vals_train_tmp, y_vals_test_tmp = calc_lstm_wk(seq, train_start_pos, test_start_pos, target_num, x_cols_idx, x_vals_train_wk, x_vals_test_wk, y_vals_train_wk, y_vals_test_wk)

	print("--- Training_data")
	print(x_vals_train_tmp[len(x_vals_train_tmp)-10:len(x_vals_train_tmp)])
	print(x_vals_train_tmp.shape)
	print(y_vals_train_tmp[len(y_vals_train_tmp)-10:len(y_vals_train_tmp)])
	print(y_vals_train_tmp.shape)
	print("--- Training_data")
	print(x_vals_test_tmp[len(x_vals_test_tmp)-10:len(x_vals_test_tmp)])
	print(x_vals_test_tmp.shape)
	print(y_vals_test_tmp[len(y_vals_test_tmp)-10:len(y_vals_test_tmp)])
	print(y_vals_test_tmp.shape)

	print("*** Reshaping data set.....")
	x_vals_train = x_vals_train_tmp.reshape(train_num, len(x_cols_idx), range_num).transpose(0,2,1)
	x_vals_test  = x_vals_test_tmp.reshape(test_num, len(x_cols_idx), range_num).transpose(0,2,1)

	print("[%lf %lf %lf %lf %lf][%lf %lf %lf %lf %lf][%lf %lf %lf %lf %lf]" % (x_vals_train_tmp[0],           x_vals_train_tmp[range_num],   x_vals_train_tmp[range_num*2],  x_vals_train_tmp[range_num*3], x_vals_train_tmp[range_num*4], \
																x_vals_train_tmp[range_num*0+1], x_vals_train_tmp[range_num*1+1], x_vals_train_tmp[range_num*2+1],  x_vals_train_tmp[range_num*3+1], x_vals_train_tmp[range_num*4+1], \
																x_vals_train_tmp[range_num*5],x_vals_train_tmp[range_num*6],x_vals_train_tmp[range_num*7], x_vals_train_tmp[range_num*8],x_vals_train_tmp[range_num*9]))
	print("[%lf %lf %lf %lf %lf][%lf %lf %lf %lf %lf][%lf %lf %lf %lf %lf]" % (x_vals_train[0][0][0], x_vals_train[0][0][1], x_vals_train[0][0][2], x_vals_train[0][0][3], x_vals_train[0][0][4], \
																x_vals_train[0][1][0], x_vals_train[0][1][1], x_vals_train[0][1][2], x_vals_train[0][1][3], x_vals_train[0][1][4], \
																x_vals_train[1][0][0], x_vals_train[1][0][1], x_vals_train[1][0][2], x_vals_train[1][0][3], x_vals_train[1][0][4]))
	print(x_vals_train_tmp[range_num*5])
	print(x_vals_train[0][1][0])
	print(x_vals_train_tmp)
	print(x_vals_train)

	y_vals_train = y_vals_train_tmp.reshape(train_num, len(x_cols_idx))
	y_vals_test  = y_vals_test_tmp.reshape(test_num, len(x_cols_idx))

	print("*** Start learning.....")
	config = tf.ConfigProto(allow_soft_placement=True)
	# config.gpu_options.allow_growth = True
	config.gpu_options.per_process_gpu_memory_fraction = 0.95
	session = tf.Session(config=config)
	K.set_session(session)

	callbacks = []
	callbacks.append(EarlyStopping("val_loss", patience=1))
	callbacks.append(ModelCheckpoint(filepath=os.path.join(models_path,"model.ep{epoch:02d}.h5")))

	# n_units = 1000
	model = Sequential()
	model.add(LSTM(256, return_sequences=True, input_shape=(x_vals_test.shape[1], x_vals_test.shape[2])))
	# model.add(LSTM(32, return_sequences=True, input_shape=(x_vals_test.shape[1], x_vals_test.shape[2])))
	model.add(Dropout(0.8))
	model.add(LSTM(512))
	# model.add(LSTM(64))
	model.add(Dropout(0.5))
	model.add(Dense(5))
	model.compile(loss='mean_squared_error', optimizer='adam')
	# model.fit(x_vals_train, y_vals_train, epochs=1000, batch_size=1, verbose=1)
	model.fit(x_vals_train, y_vals_train, epochs=50, batch_size=1024, verbose=1, callbacks=callbacks)
	# model.fit(x_vals_train, y_vals_train, epochs=50, verbose=1)

	trainPredict = model.predict(x_vals_train)
	testPredict  = model.predict(x_vals_test)

	trainScore = math.sqrt(mean_squared_error(y_vals_train[:,0], trainPredict[:,0]))
	print('Train Score: %.2f RMSE' % (trainScore))
	testScore = math.sqrt(mean_squared_error(y_vals_test[:,0], testPredict[:,0]))
	print('Test Score: %.2f RMSE' % (testScore))

	# repo_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/tmp"
	# save_as_pickled_object(model, os.path.join(repo_path, "lstm_model.pkl"))
	model.save(os.path.join(models_path,'lstm_model.h5'))  # creates a HDF5 file 'my_model.h5'


	# plt.plot(x_vals_test[0, 3, :], 'k-', label='Train xdata')
	# plt.plot(y_vals_test[0, 3], 'ro', label='Test ydata')
	# plt.plot(testPredict[0, 3], 'bo', label='Predict ydata')
	# plt.legend(loc='upper right')
	# plt.show()


if __name__ == '__main__':
	import training_chart_data
	seq = 0



	sdsm = training_chart_data.source_data_set_mgr()
	print("Set ii_obj ***")
	# sdsm.set_ii_obj_by_id_lst([])
	# sdsm.set_ii_obj_by_stock_market("東証ﾏｻﾞｰｽﾞ")
	sdsm.set_ii_obj_by_stock_category(Target_name[1])
	print("Set sds ***")
	sdsm.set_source_data_set()
	print("Save data ***")
	sdsm.save_data()
	# print("Load data ***")
	# sdsm.load_data()
	training_chart_data.prep_training_data(sdsm.source_data_set, seq)


	import os
	import numpy as np

	print("Numpy Loading ***")
	standard_x = np.load(os.path.join(npys_path, 'standard_x_%d.npz'%(seq)))['arr_0']
	standard_y = np.load(os.path.join(npys_path, 'standard_y_%d.npz'%(seq)))['arr_0']
	x_cols_idx = np.load(os.path.join(npys_path, 'x_cols_idx_%d.npz'%(seq)))['arr_0']
	y_cols_idx = np.load(os.path.join(npys_path, 'y_cols_idx_%d.npz'%(seq)))['arr_0']
	print("Data setting***")
	training_chart_data.set_tr_te_data(standard_x, standard_y, x_cols_idx, y_cols_idx, seq)
	training_chart_data.calc_lstm(seq)







