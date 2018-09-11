import numpy as np
import pandas as pd
import math
import pickle
import _pickle as cPickle
import time
import os
import sys
from datetime import datetime, timedelta, date
import investing_info as ii

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib.dates import date2num

from my_utils import *

import tensorflow as tf
from keras import backend as K
from keras.models import Sequential
from keras.models import load_model

import download_charts_selenium as dcs
import stock_charts_updateDB as scud

from crud_for_stock_detail import CRUD_for_STOCK_DETAIL



class prediction_mgr_for_ii_arr(object):
	total_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
	target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]

	def __init__(self, ii_obj, models):
		self.ii_obj = ii_obj
		self.models = models


	def get_predict_price_by_models(self, days_range=1, return_with_ii_info=True):
		start = time.time()
	
		return_df = pd.DataFrame()

		crud = CRUD_for_STOCK_DETAIL()

		for cur_day_delta in reversed(range(days_range)):
			m = 0
			for model in self.models:
				r = model.input.shape.dims[1].value
				arr, id_lst, date_lst, max_val_lst = self.ii_obj.get_arr_over_range(r, cur_day_delta, True , prediction_mgr_for_ii_arr.target_cols)
				if len(arr) == 0: continue
				tmp_predict_lst = model.predict(arr)

				tmp_arr = np.insert(arr, r, tmp_predict_lst, axis=1)[:, 1:r+1, :]
				tmp_pre_predict_lst = model.predict(tmp_arr)

				tmp_df = pd.DataFrame()
				tmp_df["stock_id"] = id_lst
				for l in range(len(prediction_mgr_for_ii_arr.target_cols)):
					if  l < len(prediction_mgr_for_ii_arr.target_cols) - 1:
						tmp_df["predict_"   + prediction_mgr_for_ii_arr.target_cols[l]] = tmp_predict_lst[:, l] * max_val_lst[:,0]
						tmp_df["pre_predict_" + prediction_mgr_for_ii_arr.target_cols[l]] = tmp_pre_predict_lst[:, l] * max_val_lst[:,0]
					else:
						tmp_df["predict_"   + prediction_mgr_for_ii_arr.target_cols[l]] = tmp_predict_lst[:, l] * max_val_lst[:,1]
						tmp_df["pre_predict_" + prediction_mgr_for_ii_arr.target_cols[l]] = tmp_pre_predict_lst[:, l] * max_val_lst[:,1]
				tmp_df["date"] = date_lst.max(axis=1)
				tmp_df["model"]    = str(m)
				return_df = return_df.append(tmp_df, ignore_index=True)
				m = m + 1

		elapsed_time = time.time() - start
		print ("[get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]]")

		# return_df = return_df.groupby(["stock_id","date"],as_index=False).min().sort_values(by=["date"], ascending=True)
		if return_with_ii_info:
			return_df = pd.merge(self.ii_obj.df, return_df, on=["stock_id", "date"], how='right')
		
		return_df["stock_id"] = return_df["stock_id"].astype('int16')
		return_df["open_price"] = return_df["open_price"].astype('float16')
		return_df["high_price"] = return_df["high_price"].astype('float16')
		return_df["low_price"] = return_df["low_price"].astype('float16')
		return_df["close_price"] = return_df["close_price"].astype('float16')
		return_df["output"] = return_df["output"].astype('int32')
		return_df = return_df.sort_values(by=["date"], ascending=True)
		return return_df



class prediction_mgr_for_hs_arr(object):
	total_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
	target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]

	def __init__(self, held_stock_lst, target_date, models):
		self.hs_lst = held_stock_lst
		self.models = models
		self.d = target_date # Date to determine whether to hold or sell

	def get_predict_price_by_models(self, update_fl=False):
		start = time.time()
		predict_lst     = []
		pre_predict_lst = []
		whole_id_lst    = []

		crud = CRUD_for_STOCK_DETAIL()

		for hs in self.hs_lst:
			if update_fl:
				dcs.update_stock(hs.stock_id)
				scud.update_charts_stats(hs.stock_id)
				hs.update_ii_obj(self.d)
			whole_id_lst.append(hs.stock_id)

		m=0
		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			tmp_ii_obj = ii.investing_info(whole_id_lst, self.d-timedelta(days=r*2), self.d-timedelta(days=1))

			arr, id_lst = tmp_ii_obj.get_arr_over_range(r, True, prediction_mgr_for_hs_arr.target_cols)
			print(arr)
			tmp_predict_lst = model.predict(arr)

			tmp_arr = np.insert(arr, r, tmp_predict_lst, axis=1)[:, 1:r+1, :]
			tmp_pre_predict_lst = model.predict(tmp_arr)

			predict_lst     = np.append(predict_lst, tmp_predict_lst)
			pre_predict_lst = np.append(pre_predict_lst, tmp_pre_predict_lst)

			for id_n in range(len(id_lst)):
				try:
					cur_arr = arr[id_n,:,0:4]
					cur_arr = np.insert(cur_arr, len(cur_arr), tmp_predict_lst[id_n, 0:4], axis=0)
					cur_arr = np.insert(cur_arr, len(cur_arr), tmp_pre_predict_lst[id_n, 0:4], axis=0)
					cur_id = id_lst[id_n]
					fig = plt.figure()
					d_lst = tmp_ii_obj.df["date"].values[len(tmp_ii_obj.df["date"])-r:len(tmp_ii_obj.df["date"])]
					d_lst = np.append(d_lst, [d_lst.max() + timedelta(days=1), d_lst.max() + timedelta(days=2)])
					xdate = [x for x in d_lst]  # 日付
					
					ax = plt.subplot()
					ax.set_xlim(d_lst[0], d_lst[-1])
					ax.grid() 
					stock_name = crud.read_tbl_by_df("WHERE stock_id='%s'"%str(cur_id))["stock_name"].values[0]
					ax.set_title('Chart [%s]_%s'%(str(cur_id),stock_name))
					ohlc = np.vstack((date2num(xdate), cur_arr.T)).T
					candlestick_ohlc(ax, ohlc, width=0.7, colorup='r', colordown='b')

					if not(os.path.isdir("./pred_charts/%s"%str(cur_id))):
						os.makedirs("./pred_charts/%s"%str(cur_id))
					plt.savefig(os.path.join("./pred_charts/%s"%str(cur_id), '%s_[%s_%s]_%s.png'%(str(cur_id), str(d_lst[0]), str(d_lst[-1]), str(m))))#画像保存
					plt.close()
				except Exception as e:
					import traceback
					traceback.print_exc()

			m = m + 1

		predict_lst     = predict_lst.reshape(len(self.models), len(id_lst), -1)
		pre_predict_lst = pre_predict_lst.reshape(len(self.models), len(id_lst), -1)

		elapsed_time = time.time() - start
		print ("* get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")

		return predict_lst, pre_predict_lst






class prediction_mgr_for_ii(object):
	total_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
	target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]

	def __init__(self, ii_obj, models):
		self.ii_obj = ii_obj
		self.models = models
		self.d = self.ii_obj.df["date"].max()
		self.predict_price_lst = pd.DataFrame()

	def get_predict_price_by_models(self):
		# try:
		start = time.time()
		# tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		# target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		# predict_price_lst = pd.DataFrame()

		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			for s_n in range(len(self.ii_obj.id_lst)):
				sid = self.ii_obj.id_lst[s_n]
				# print(sid)
				tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid), prediction_mgr_for_ii.total_cols]
				if len(tmp_df) < r:
					continue
				# tmp_df = tmp_ii_obj.df.loc[:, tolal_cols]
				tmp_np = np.array(df_to_array(tmp_df, prediction_mgr_for_ii.target_cols))[:,len(tmp_df)-r:len(tmp_df)]
				max_lst = tmp_np.max(axis=1)
				for i in range(len(max_lst)):
					tmp_np[i, :] = tmp_np[i, :] / max_lst[i]
				tmp_x = tmp_np.reshape(len(prediction_mgr_for_ii.target_cols), r, -1).T
				tmp_predict = model.predict(tmp_x)[0]
				# tmp_pred_lst.append(tmp_predict)
				for i in range(len(max_lst)):
					tmp_predict[i] = tmp_predict[i] * max_lst[i]		

				tmp_predict_df = pd.Series(index= prediction_mgr_for_ii.total_cols, dtype=str)
				tmp_predict_df["stock_id"] = int(sid)
				tmp_predict_df["date"] = self.d + timedelta(days=1)
				for c in range(len(prediction_mgr_for_ii.target_cols)):
					tmp_predict_df[prediction_mgr_for_ii.target_cols[c]] = tmp_predict[c]
				self.predict_price_lst = self.predict_price_lst.append(tmp_predict_df,ignore_index=True)

		elapsed_time = time.time() - start
		print ("* get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		print(self.predict_price_lst)
		self.predict_price_lst = self.predict_price_lst.loc[:,  prediction_mgr_for_ii.total_cols]
		return self.predict_price_lst

	def get_predict_price_with_pre_pred(self):
		if len(self.predict_price_lst) < 1:
			return

		start = time.time()
		# tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		# target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		pred_lst = pd.DataFrame()

		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			for s_n in range(len(self.ii_obj.id_lst)):
				sid = self.ii_obj.id_lst[s_n]
				tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid),  prediction_mgr_for_ii.total_cols]
				if len(tmp_df) < r:
					continue
				tmp_pred_series = self.predict_price_lst.loc[self.predict_price_lst["stock_id"]==int(sid),  prediction_mgr_for_ii.total_cols]
				tmp_pred_series = tmp_pred_series.groupby(["stock_id", "date"]).min()
				tmp_pred_series = tmp_pred_series.reset_index()

				tmp_df = tmp_df.append(tmp_pred_series,ignore_index=True, sort=True).sort_values(by=["date"], ascending=True)

				pred_date = tmp_df["date"].iloc[-1]
				tmp_df = tmp_df.loc[:, prediction_mgr_for_ii.target_cols]
				tmp_np = np.array(df_to_array(tmp_df, prediction_mgr_for_ii.target_cols))[:,len(tmp_df)-r:len(tmp_df)]
				max_lst = tmp_np.max(axis=1)
				for i in range(len(max_lst)):
					tmp_np[i, :] = tmp_np[i, :] / max_lst[i]
				tmp_x = tmp_np.reshape(len(prediction_mgr_for_ii.target_cols), r, -1).T

				tmp_predict = model.predict(tmp_x)[0]
				for i in range(len(max_lst)):
					tmp_predict[i] = tmp_predict[i] * max_lst[i]

				tmp_predict_df = pd.Series(index= prediction_mgr_for_ii.total_cols, dtype=str)
				tmp_predict_df["stock_id"] = int(sid)
				tmp_predict_df["date"] = pred_date + timedelta(days=1)
				for c in range(len(prediction_mgr_for_ii.target_cols)):
					tmp_predict_df[prediction_mgr_for_ii.target_cols[c]] = tmp_predict[c]

				pred_lst = pred_lst.append(tmp_predict_df,ignore_index=True)
		
		elapsed_time = time.time() - start
		print ("* get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		self.pre_pred_lst = pred_lst.loc[:,  prediction_mgr_for_ii.total_cols]
		return self.pre_pred_lst

	def plot_charts(self):

		crud = CRUD_for_STOCK_DETAIL()
		for s_n in range(len(self.ii_obj.id_lst)):
			try:
				sid = self.ii_obj.id_lst[s_n]
				# print(self.ii_obj.id_lst)
				# print(sid)
				cur_ii_df       = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid),  prediction_mgr_for_ii.total_cols]
				cur_ii_df       = cur_ii_df.iloc[len(cur_ii_df)-40:len(cur_ii_df)]
				# print(cur_ii_df)
				cur_pred_lst    = self.predict_price_lst.loc[self.predict_price_lst["stock_id"]==int(sid), :]
				cur_pe_pred_lst = self.pre_pred_lst.loc[self.pre_pred_lst["stock_id"]==int(sid), :]
				# print(cur_pred_lst)
				# print(cur_pe_pred_lst)
				tmp_df = cur_ii_df.append(cur_pred_lst.min(),ignore_index=True)
				tmp_df = tmp_df.append(cur_pe_pred_lst.min(),ignore_index=True)
				# print(tmp_df)
				fig = plt.figure()
				date_lst = tmp_df["date"].drop_duplicates().values.reshape(-1)
				# print(date_lst)
				xdate = [x for x in date_lst]  # 日付
				ax = plt.subplot()
				df_tmp = tmp_df.loc[:, ['open_price', 'high_price','low_price', 'close_price']]

				ax.set_xlim(date_lst[0], date_lst[-1])  # x軸の範囲
				ax.grid()  # グリッド表示
				stock_name = crud.read_tbl_by_df("WHERE stock_id='%s'"%str(sid))["stock_name"].values[0]
				ax.set_title('Chart [%s]_%s'%(str(sid),stock_name))
				ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
				candlestick_ohlc(ax, ochl, width=0.7, colorup='g', colordown='r')

				if not(os.path.isdir("./pred_charts/%s"%str(sid))):
					os.makedirs("./pred_charts/%s"%str(sid))
				plt.savefig(os.path.join("./pred_charts/%s"%str(sid), '%s_[%s_%s].png'%(str(sid), str(date_lst[0]), str(date_lst[-1]))))#画像保存
				plt.close()
				# print([date_lst[0], date_lst[-1]])
				# print(sid)
				# print("***************")
			except Exception:
				print("***Error: %s"%str(sid))
				import traceback
				traceback.print_exc()
				pass


class prediction_mgr_for_hs(object):

	def __init__(self, held_stock_lst, target_date, models):
		self.hs_lst = held_stock_lst
		self.models = models
		self.d = target_date # Date to determine whether to hold or sell
		self.predict_price_lst = pd.DataFrame()

	def add_date(self, delta=1):
		self.d = self.d + timedelta(days=delta)

	def get_predict_price_by_models(self, update_fl=False):
		# try:
		start = time.time()
		tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		s_lst = []

		for hs in self.hs_lst:
			if update_fl:
				dcs.update_stock(hs.stock_id)
				scud.update_charts_stats(hs.stock_id)
				hs.update_ii_obj(self.d)
			s_lst.append(hs.stock_id)

		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			tmp_ii_obj = ii.investing_info(s_lst, self.d-timedelta(days=r*2), self.d-timedelta(days=1))
			for hs_id in range(len(self.hs_lst)):
				hs = self.hs_lst[hs_id]
				sid = hs.stock_id
				tmp_df = tmp_ii_obj.df.loc[tmp_ii_obj.df["stock_id"]==int(sid), target_cols]
				if len(tmp_df) < r:
					continue
				# tmp_df = tmp_ii_obj.df.loc[:, tolal_cols]
				tmp_np = np.array(df_to_array(tmp_df, target_cols))[:,len(tmp_df)-r:len(tmp_df)]
				max_lst = tmp_np.max(axis=1)
				for i in range(len(max_lst)):
					tmp_np[i, :] = tmp_np[i, :] / max_lst[i]
				tmp_x = tmp_np.reshape(len(target_cols), r, -1).T
				tmp_predict = model.predict(tmp_x)[0]
				# tmp_pred_lst.append(tmp_predict)
				for i in range(len(max_lst)):
					tmp_predict[i] = tmp_predict[i] * max_lst[i]

				tmp_predict_df = pd.Series(index=tolal_cols, dtype=str)
				tmp_predict_df["stock_id"] = sid
				tmp_predict_df["date"] = self.d
				for c in range(len(target_cols)):
					tmp_predict_df[target_cols[c]] = tmp_predict[c]
				self.predict_price_lst = self.predict_price_lst.append(tmp_predict_df,ignore_index=True)

		elapsed_time = time.time() - start
		print ("* get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")

		return self.predict_price_lst

		# except Exception as e:
		# 	print(e)
		# 	return 

	# def get_predict_price(self):
	# 	predict_price_lst = []
	# 	for sid in self.s_lst:
	# 		tmp_pred_lst = []
	# 		for m in self.models:
	# 			tmp_pred = self.get_predict_price_by_model(sid, m)
	# 			tmp_pred_lst.append(tmp_pred)
	# 		predict_price_lst.append(tmp_pred_lst)

	# 	return predict_price_lst


	def get_predict_price_with_pre_pred(self):
		if len(self.predict_price_lst) < 1:
			return

		start = time.time()
		tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		pred_lst = pd.DataFrame()

		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			for hs_id in range(len(self.hs_lst)):
				hs = self.hs_lst[hs_id]
				tmp_df = hs.ii_obj.df.loc[:, tolal_cols]
				if len(tmp_df) < r:
					continue
				tmp_pred_series = self.predict_price_lst.loc[:, tolal_cols]
				tmp_pred_series = tmp_pred_series.groupby(["stock_id", "date"]).min()
				tmp_pred_series = tmp_pred_series.reset_index()

				tmp_df = tmp_df.append(tmp_pred_series,ignore_index=True, sort=True).sort_values(by=["date"], ascending=True)

				pred_date = tmp_df["date"].iloc[-1]
				tmp_df = tmp_df.loc[:, target_cols]
				tmp_np = np.array(df_to_array(tmp_df, target_cols))[:,len(tmp_df)-r:len(tmp_df)]
				max_lst = tmp_np.max(axis=1)
				for i in range(len(max_lst)):
					tmp_np[i, :] = tmp_np[i, :] / max_lst[i]
				tmp_x = tmp_np.reshape(len(target_cols), r, -1).T

				tmp_predict = model.predict(tmp_x)[0]
				for i in range(len(max_lst)):
					tmp_predict[i] = tmp_predict[i] * max_lst[i]

				tmp_predict_df = pd.Series(index=tolal_cols, dtype=str)
				tmp_predict_df["stock_id"] = hs.stock_id
				tmp_predict_df["date"] = pred_date + timedelta(days=1)
				for c in range(len(target_cols)):
					tmp_predict_df[target_cols[c]] = tmp_predict[c]

				pred_lst = pred_lst.append(tmp_predict_df,ignore_index=True).loc[:, tolal_cols]
		
		elapsed_time = time.time() - start
		print ("* get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		print(pred_lst)
		return pred_lst



def df_to_array(df, columns):
	array = np.empty((0, len(df)))
	for c_idx in range(len(columns)):
		array = np.append(array, np.array([df[columns[c_idx]].tolist()]), axis=0)
	return array


def test_plot(s_lst, init_date, r):

	import numpy as np
	import pandas as pd
	import investing_info as ii 
	from keras.models import load_model
	from datetime import datetime, timedelta, date
	from mpl_finance import candlestick_ohlc
	from matplotlib.dates import date2num
	import matplotlib.pyplot as plt
	import os
	import download_charts_selenium as dcs
	import stock_charts_updateDB as scud

	for cur_id in s_lst:
		dcs.update_stock(cur_id)
		scud.update_charts_stats(cur_id)

	m1=load_model("./tmp_30/models/full/model.ep50.h5")
	m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")
	m3=load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5")

	pred_price_lst = pd.DataFrame()
	# init_date = datetime(2018,8,5)
	for i in range(r):
		from_d=datetime(2010,1,1)
		to_d=init_date - timedelta(days=r-i)
		ii_obj = ii.investing_info(s_lst, from_d, to_d)
		# ii_obj = ii.get_ii_obj_by_stock_market("東証一部", from_d, to_d)
		# p = prediction_mgr_for_ii(ii_obj, [m1])
		p = prediction_mgr_for_ii(ii_obj, [m1, m2, m3])
		tmp_pred_price_lst = p.get_predict_price_by_models()
		pred_price_lst = pred_price_lst.append(tmp_pred_price_lst)

		id_lst = pred_price_lst["stock_id"].drop_duplicates()

	for cur_id in id_lst:
		full_df_tmp = pred_price_lst.loc[pred_price_lst["stock_id"]==cur_id, :]
		# print(full_df_tmp)

		fig = plt.figure()

		# For pred graph =======
		full_df_tmp = full_df_tmp.groupby("date").mean().sort_values(by=["date"], ascending=True)
		date_lst1 = pred_price_lst["date"].drop_duplicates()
		xdate1 = [x for x in date_lst1]  # 日付
		ax1 = plt.subplot(211)
		df_tmp1 = full_df_tmp.loc[:, ['open_price', 'high_price','low_price', 'close_price']]
		ax1.set_xlim(date_lst1.values[0], date_lst1.values[-1])  # x軸の範囲
		ax1.grid()  # グリッド表示
		ax1.set_title('Predicted_plot')
		ochl1 = np.vstack((date2num(xdate1), df_tmp1.values.T)).T
		candlestick_ohlc(ax1, ochl1, width=0.7, colorup='g', colordown='r')
		# fig.autofmt_xdate()  # x軸のオートフォーマット

		# plt.savefig(os.path.join("./pred_real_charts", str(cur_id) + '_pred.png'))#画像保存


		# fig2 = plt.figure()

		# For real graph =======
		tmp_ii_obj = ii.investing_info([cur_id], date_lst1.values[0], date_lst1.values[-1])
		date_lst2 = tmp_ii_obj.df["date"].drop_duplicates()
		xdate2 = [x for x in date_lst2]  # 日付
		ax2 = plt.subplot(212)
		df_tmp2 = tmp_ii_obj.df.loc[:, ['open_price', 'high_price','low_price', 'close_price']]
		ax2.set_xlim(tmp_ii_obj.df.loc[:,"date"]. values[0], tmp_ii_obj.df.loc[:,"date"]. values[-1])  # x軸の範囲
		ax2.grid()  # グリッド表示
		ax2.set_title('Real_plot')
		ochl2 = np.vstack((date2num(xdate2), df_tmp2.values.T)).T
		candlestick_ohlc(ax2, ochl2, width=0.7, colorup='g', colordown='r')
		# fig.autofmt_xdate()  # x軸のオートフォーマット
		fig.tight_layout() # タイトルとラベルが被るのを解消
		
		plt.savefig(os.path.join("./pred_real_charts", str(cur_id) + '_real.png'))#画像保存

		# print("%s ======="%str(cur_id))
		# print(df_tmp1)
		# print(df_tmp2)









