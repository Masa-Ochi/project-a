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
from my_utils import *

import tensorflow as tf
from keras import backend as K
from keras.models import Sequential
from keras.models import load_model

import download_charts_selenium as dcs
import stock_charts_updateDB as scud



class prediction_mgr_for_ii(object):

	def __init__(self, ii_obj, models):
		self.ii_obj = ii_obj
		self.models = models
		self.d = self.ii_obj.df["date"].max()
		self.predict_price_lst = pd.DataFrame()

	def get_predict_price_by_models(self):
		# try:
		start = time.time()
		tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		# predict_price_lst = pd.DataFrame()

		for model in self.models:
			tmp_pred_lst = []
			r = model.input.shape.dims[1].value
			for s_n in range(len(self.ii_obj.id_lst)):
				sid = self.ii_obj.id_lst[s_n]
				tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid), tolal_cols]
				if len(tmp_df) < r:
					continue
				# tmp_df = tmp_ii_obj.df.loc[:, tolal_cols]
				tmp_np = np.array(df_to_array(tmp_df, target_cols))[:,len(tmp_df)-r:len(tmp_df)]
				max_lst = tmp_np.max(axis=1)
				for i in range(len(max_lst)):
					tmp_np[i, :] = tmp_np[i, :] / max_lst[i]
				tmp_x = tmp_np.reshape(len(target_cols), r, -1).T
				tmp_predict = model.predict(tmp_x)[0]
				# print(np.array(df_to_array(tmp_df, target_cols))[:,-r-1:-1].shape)
				# tmp_pred_lst.append(tmp_predict)
				for i in range(len(max_lst)):
					tmp_predict[i] = tmp_predict[i] * max_lst[i]		

				tmp_predict_df = pd.Series(index=tolal_cols, dtype=str)
				tmp_predict_df["stock_id"] = sid
				tmp_predict_df["date"] = self.d + timedelta(days=1)
				for c in range(len(target_cols)):
					tmp_predict_df[target_cols[c]] = tmp_predict[c]
				self.predict_price_lst = self.predict_price_lst.append(tmp_predict_df,ignore_index=True)

		elapsed_time = time.time() - start
		print ("***** get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		return self.predict_price_lst

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
			for s_n in range(len(self.ii_obj.id_lst)):
				sid = self.ii_obj.id_lst[s_n]
				tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid), tolal_cols]
				if len(tmp_df) < r:
					continue
				tmp_pred_series = self.predict_price_lst.loc[self.predict_price_lst["stock_id"]==int(sid), tolal_cols]
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
				tmp_predict_df["stock_id"] = int(sid)
				tmp_predict_df["date"] = pred_date + timedelta(days=1)
				for c in range(len(target_cols)):
					tmp_predict_df[target_cols[c]] = tmp_predict[c]

				pred_lst = pred_lst.append(tmp_predict_df,ignore_index=True)
		
		elapsed_time = time.time() - start
		print ("***** get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		return pred_lst.loc[:, tolal_cols]





class prediction_mgr_for_hs(object):

	def __init__(self, held_stock_lst, target_date, models):
		self.hs_lst = held_stock_lst
		self.models = models
		self.d = target_date # Date to determine whether to hold or sell
		self.predict_price_lst = pd.DataFrame()

	def add_date(self, delta=1):
		self.d = self.d + timedelta(days=delta)

	def get_predict_price_by_models(self):
		# try:
		start = time.time()
		tolal_cols = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
		s_lst = []

		for hs in self.hs_lst:
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
				# print(np.array(df_to_array(tmp_df, target_cols))[:,-r-1:-1].shape)
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
		print ("***** get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")

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
			for s_n in range(len(self.ii_obj.id_lst)):
				sid = self.ii_obj.id_lst[s_n]
				tmp_df = self.ii_obj.df.loc[self.ii_obj.df["stock_id"]==int(sid), tolal_cols]
				if len(tmp_df) < r:
					continue
				tmp_pred_series = self.predict_price_lst.loc[self.predict_price_lst["stock_id"]==int(sid), tolal_cols]
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
				tmp_predict_df["stock_id"] = int(sid)
				tmp_predict_df["date"] = pred_date + timedelta(days=1)
				for c in range(len(target_cols)):
					tmp_predict_df[target_cols[c]] = tmp_predict[c]

				pred_lst = pred_lst.append(tmp_predict_df,ignore_index=True)
		
		elapsed_time = time.time() - start
		print ("***** get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")
		return pred_lst.loc[:, tolal_cols]



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









