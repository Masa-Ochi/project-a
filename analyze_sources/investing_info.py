
import datetime
import pandas as pd
import copy
import os
import time
import numpy as np
import datetime
from crud_for_investing_info import CRUD_for_INVESTING_INFO
from crud_for_stock_charts import CRUD_for_STOCK_CHARTS
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL

import matplotlib.pyplot as plt
# import matplotlib.finance as mpf
from mpl_finance import candlestick_ohlc
from matplotlib.dates import date2num

from pulp import *

import download_charts_selenium as dcs
import stock_charts_updateDB as scud




def main():
	from_date = datetime.date(2017,4,1)
	to_date = datetime.date(2017,10,1)
	# ii_obj = investing_info(["A7L", "JPM_ph", "IAK_履歴データ"], from_date, to_date)
	# ii_obj = investing_info(["JPM_ph", "NGD", "VLU_履歴データ_(5)", "8362"], from_date, to_date)

	# crud_detail = CRUD_for_STOCK_DETAIL()
	# tmp_sql = "WHERE stock_market='東証一部' and business_type='その他金融'"
	# id_lst = crud_detail.read_tbl_by_df(tmp_sql).loc[:, "stock_id"].values
	id_lst=[3861]
	# print(id_lst)
	ii_obj = investing_info(id_lst, from_date, to_date)
	# ii_obj = investing_info(["ENDP"], from_date, to_date)
	ii_obj.plt_chart_all()
	# ii_obj.plt_chart_w_move_avrg()
	# ii_obj.plt_chart_w_atr()
	# ii_obj.plt_chart_w_rsi()

def get_id_lst():
	sql_str = "SELECT DISTINCT stock_id FROM investing_info"
	# tmp_crud = CRUD_for_INVESTING_INFO()
	tmp_crud = CRUD_for_STOCK_CHARTS()
	id_lst = tmp_crud.read_tbl_by_df(sql_str, False)
	tmp_crud.close_connection()
	return id_lst

def get_similarity(from_date, to_date, id_lst=""):
	# if id_lst=="":
	# 	crud_detail = CRUD_for_STOCK_DETAIL()
	# 	detail_lst = crud_detail.read_tbl_by_df()
	# 	id_lst = detail_lst.loc[:, "stock_id"].values

	ii_obj = investing_info(id_lst, from_date, to_date)
	
	real_id_lst = ii_obj.df["stock_id"].drop_duplicates()
	charts_lst = pd.DataFrame()
	for stock_id in real_id_lst:
		try:
			tmp_lst = []
			tmp_lst.extend(ii_obj.df.loc[ii_obj.df["stock_id"]==stock_id, "open_price"].values)
			tmp_lst.extend(ii_obj.df.loc[ii_obj.df["stock_id"]==stock_id, "high_price"].values)
			tmp_lst.extend(ii_obj.df.loc[ii_obj.df["stock_id"]==stock_id, "low_price"].values)
			tmp_lst.extend(ii_obj.df.loc[ii_obj.df["stock_id"]==stock_id, "close_price"].values)
			charts_lst[str(stock_id)] = tmp_lst / max(tmp_lst)


		except Exception:
			pass

	return charts_lst


def get_ii_obj_by_stock_market(stock_market, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31), do_update=False):
	crud_detail = CRUD_for_STOCK_DETAIL()
	tmp_sql = "WHERE stock_market='%s'"%(stock_market)
	detail_lst = crud_detail.read_tbl_by_df(tmp_sql)
	id_lst = detail_lst.loc[:, "stock_id"].values
	print(id_lst)

	return investing_info(id_lst, from_date, to_date, do_update)

def get_ii_obj_by_category(business_type, from_date, to_date, do_update=False):
	crud_detail = CRUD_for_STOCK_DETAIL()
	tmp_sql = "WHERE business_type='%s'"%(business_type)
	detail_lst = crud_detail.read_tbl_by_df(tmp_sql)
	id_lst = detail_lst.loc[:, "stock_id"].values
	print(id_lst)

	return investing_info(id_lst, from_date, to_date, do_update)


def get_ii_obj_by_market_category(stock_market, business_type, from_date, to_date, do_update=False):
	crud_detail = CRUD_for_STOCK_DETAIL()
	tmp_sql = "WHERE stock_market='%s' and business_type='%s'"%(stock_market, business_type)
	detail_lst = crud_detail.read_tbl_by_df(tmp_sql)
	id_lst = detail_lst.loc[:, "stock_id"].values
	print(id_lst)

	return investing_info(id_lst, from_date, to_date, do_update)



class investing_info(object):
	id_lst = []
	move_avrg_lst = []
	# crud = CRUD_for_INVESTING_INFO()
	crud = CRUD_for_STOCK_CHARTS()

	def __init__(self, id_lst="", from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2200, 12, 31), do_update=False):
		if len(id_lst) > 0:
			print("Number of stock_id: %s" % len(id_lst))
			self.id_lst = id_lst
			self.from_date = from_date
			self.to_date = to_date
			from_date_str = from_date.strftime("%Y-%m-%d")
			to_date_str = to_date.strftime("%Y-%m-%d")
			sql_str = "WHERE stock_id in (" 
			for id_str in self.id_lst:
				sql_str = sql_str + "" + str(id_str) + "" + ","
			sql_str = sql_str[:-1]
			sql_str = sql_str + ")"
			sql_str = sql_str + " AND date >= '" + from_date_str + "' AND date <= '" + to_date_str + "'"
			sql_str = sql_str + " ORDER BY stock_id, date" # [IMPORTANT]
		else:
			from_date_str = from_date.strftime("%Y-%m-%d")
			to_date_str = to_date.strftime("%Y-%m-%d")
			sql_str = "WHERE date >= '" + from_date_str + "' AND date <= '" + to_date_str + "'"
			sql_str = sql_str + " ORDER BY stock_id, date" # [IMPORTANT]

		if do_update:
			print("Update stock charts...")
			for cur_id in id_lst:
				try:
					start = time.time()	
					dcs.update_stock(str(cur_id))
					scud.update_charts_stats(str(cur_id))
					elapsed_time = time.time() - start
					print ("***** Update time:{0}".format(elapsed_time) + "[sec]")
				except Exception as e:
					print("Error occured >>>>> %s"%str(cur_id))

		self.df = self.crud.read_tbl_by_df(sql_str)
		# Tmp code ----------------------------------
		self.df = self.df.rename(columns={'end_price': 'close_price', 'start_price': 'open_price'})
		# Tmp code ----------------------------------
		self.set_sup_res_line(100)
		self.set_array()
		# self.plt_chart_all()
		# print(self.avrg_lne_param)

	def set_array(self):
		columns = self.df.columns
		self.array = []
		for i in self.id_lst:
			tmp_df = self.df.loc[self.df["stock_id"]==int(i),:]
			tmp_a = []
			for c_idx in range(len(columns)):
				tmp_a.append(tmp_df[columns[c_idx]])
			self.array.append(tmp_a)

	def set_sup_res_line(self, day=""):
		real_id_lst = self.df["stock_id"].drop_duplicates()
		self.line_param = pd.DataFrame()
		for stock_id in real_id_lst:
			# df_tmp_full = self.df.loc[self.df["stock_id"]==stock_id]
			df_tmp_full = self.df.loc[self.df["stock_id"]==stock_id, :]

			m = LpProblem(sense=LpMinimize) # 数理モデル
			a1 = LpVariable('a1', lowBound=0) # 変数
			b1 = LpVariable('b1', lowBound=0) # 変数
			a2 = LpVariable('a2', lowBound=0) # 変数
			b2 = LpVariable('b2', lowBound=0) # 変数

			x_max = len(df_tmp_full)
			x_min = 0 if str(day)=="" else max(x_max-day, 0) 
			m += (((a2*x_min+b2)-(a1*x_min+b1)) + ((a2*x_max+b2)-(a1*x_max+b1))) * x_max   # 目的関数
			for x in range(x_min, x_max):
				m += a2*x+b2 >= df_tmp_full.iloc[x, :].loc[["open_price", "close_price", "high_price", "low_price"]].max()
				m += a1*x+b1 <= df_tmp_full.iloc[x, :].loc[["open_price", "close_price", "high_price", "low_price"]].min()
			m.solve() # ソルバーの実行

			res_j = {"stock_id": stock_id, "res_a": value(a1), "res_b": value(b1), "sup_a": value(a2), "sup_b": value(b2)}
			self.line_param = self.line_param.append(res_j, ignore_index=True)
		self.avrg_lne_param = pd.DataFrame()
		self.avrg_lne_param["res_a"] = self.line_param.loc[:, "res_a"].mean()
		self.avrg_lne_param["sup_a"] = self.line_param.loc[:, "sup_a"].mean()


	def plt_chart_w_slope(self, path=os.path.join(os.getcwd(), "chart")):
		real_id_lst = self.df["stock_id"].drop_duplicates()
		for stock_id in real_id_lst:

			slope_lst = []
			slope_lst.append(0)
			tmp_val_lst = self.df.loc[self.df["stock_id"]==stock_id].min(axis=1).values
			for i in range(1, len(tmp_val_lst)):
				tmp_slope = (tmp_val_lst[i] - tmp_val_lst[i-1])
				slope_lst.append(tmp_slope)


			df_tmp_full = self.df[self.df.stock_id == stock_id]

			df_tmp = df_tmp_full.ix[:, ['open_price', 'high_price','low_price', 'close_price']]
			fig = plt.figure()
			ax1 = plt.subplot(211)
			xdate = [x for x in df_tmp_full.date]  # 日付
			ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T

			# Ref: http://miyakoblue.info/python/matplotlib-finance_modulenotfounderror/
			# mpf.candlestick_ochl(ax1, ochl, width=0.7, colorup='g', colordown='r')
			candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')


			# plt.plot(df_tmp_full["date"].values, df_tmp.min(axis=1).values)
			ax1.grid()  # グリッド表示
			ax1.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット

			x_max = len(df_tmp_full)

			[a1, b1, a2, b2] = self.line_param.loc[self.line_param["stock_id"]==stock_id, ["res_a", "res_b", "sup_a", "sup_b"]].values[0]
			plt.plot(df_tmp_full["date"].values, [a2*x+b2 for x in range(x_max)])
			plt.plot(df_tmp_full["date"].values, [a1*x+b1 for x in range(x_max)])

			ax2 = plt.subplot(212)
			ax2.grid()  # グリッド表示
			ax2.set_xlim(df_tmp_full["date"].values[0], df_tmp_full["date"].values[-1])  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット
			plt.plot(df_tmp_full["date"].values, slope_lst, label="slope")
			plt.legend()
			if not os.path.isdir(path):
				os.makedirs(path) 
			plt.savefig(os.path.join(path, str(stock_id) + '_chart_w_slope.png'))#画像保存





	# def __set_move_avrg(self):
	# 	real_id_lst = self.df["stock_id"].drop_duplicates()
	# 	day_lst = [5, 10, 20]

	# 	for id_str in real_id_lst:
	# 		cur_move_avrg_lst = []
	# 		df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
	# 		date_lst = df_tmp_full["date"].values.flatten()

	# 		xdate = [x for x in df_tmp_full.date]  # 日付
	# 		close_price_lst = df_tmp_full["close_price"].values.flatten()
	# 		move_avrg = np.zeros([len(close_price_lst)])
	# 		for day in day_lst:
	# 			move_avrg = np.zeros([len(close_price_lst)])
	# 			for i in range(len(close_price_lst)):
	# 				if i < day:
	# 					move_avrg[i] = close_price_lst[i]
	# 				else:
	# 					move_avrg[i] = np.sum(close_price_lst[i-day:i]) / day

	# 			cur_move_avrg_lst.append({
	# 					"day"      : day, 
	# 					"move_avrg": move_avrg
	# 					})
	# 		self.move_avrg_lst.append({
	# 			"stock_id"     : id_str,
	# 			"date_lst"     : date_lst, 
	# 			"move_avrg_lst": cur_move_avrg_lst
	# 			})


	def plt_chart_all(self, path=os.path.join(os.getcwd(), "chart")):
		self.plt_chart_w_move_avrg(path)
		self.plt_chart_w_atr(path)
		self.plt_chart_w_rsi(path)
		self.plt_chart_w_slope(path)


	def plt_chart(self, path=os.getcwd()):
		real_id_lst = self.df["stock_id"].drop_duplicates()

		for id_str in real_id_lst:
			df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
			df_tmp = df_tmp_full.ix[:, ['open_price', 'high_price','low_price', 'close_price']]

			fig = plt.figure()
			ax = plt.subplot()

			xdate = [x for x in df_tmp_full.date]  # 日付
			ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
			# mpf.candlestick_ochl(ax, ochl, width=0.7, colorup='g', colordown='r')
			candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
			ax.grid()  # グリッド表示
			ax.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット
			plt.savefig(os.path.join(path, id_str + '_chart.png'))#画像保存


	# def plt_move_avrg(self, path=os.getcwd()):
	# 	real_id_lst = self.df["stock_id"].drop_duplicates()
	# 	day_lst = [5, 10, 20, 40, 80]

	# 	for day in day_lst:

	# 		fig = plt.figure()
	# 		ax = plt.subplot()

	# 		for d_item in item["move_avrg_lst"]:
	# 			ax.grid()  # グリッド表示
	# 			ax.set_xlim(item["date_lst"][0], item["date_lst"][-1])  # x軸の範囲
	# 			fig.autofmt_xdate()  # x軸のオートフォーマット
	# 			plt.plot(item["date_lst"], d_item["move_avrg"], label="day-" + str(d_item["day"]))
	# 		plt.legend()
	# 		plt.savefig(os.path.join(path, item["stock_id"] + '_' + str(d_item["day"]) + '_move_avg.png'))#画像保存


	def plt_chart_w_move_avrg(self, path=os.path.join(os.getcwd(), "chart")):
		real_id_lst = self.df["stock_id"].drop_duplicates()

		for id_str in real_id_lst:
			df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
			df_tmp = df_tmp_full.ix[:, ['open_price', 'high_price','low_price', 'close_price']]


			fig = plt.figure()
			ax = plt.subplot()

			xdate = [x for x in df_tmp_full.date]  # 日付
			ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
			# mpf.candlestick_ochl(ax, ochl, width=0.7, colorup='g', colordown='r')
			candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
			ax.grid()  # グリッド表示
			ax.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット

			close_price_lst = df_tmp_full["close_price"].values.flatten()
			# day_lst = [5, 10, 20, 40, 80]
			day_lst = [5, 10, 20]

			for day in day_lst:
				ax.grid()  # グリッド表示
				ax.set_xlim(df_tmp_full["date"].values[0], df_tmp_full["date"].values[-1])  # x軸の範囲
				fig.autofmt_xdate()  # x軸のオートフォーマット
				plt.plot(df_tmp_full["date"].values, df_tmp_full["move_avrg_" + str(day)].values, label="day-" + str(day))
			plt.legend()
			if not os.path.isdir(path):
				os.makedirs(path) 
			plt.savefig(os.path.join(path, str(id_str) + '_chart_w_move_avrg.png'))#画像保存

	def plt_chart_w_atr(self, path=os.path.join(os.getcwd(), "chart")):
		real_id_lst = self.df["stock_id"].drop_duplicates()

		for id_str in real_id_lst:
			df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
			df_tmp = df_tmp_full.ix[:, ['open_price', 'high_price','low_price', 'close_price']]


			fig = plt.figure()
			ax1 = plt.subplot(211)
			ax2 = plt.subplot(212)

			xdate = [x for x in df_tmp_full.date]  # 日付
			ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
			# mpf.candlestick_ochl(ax1, ochl, width=0.7, colorup='g', colordown='r')
			candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
			ax1.grid()  # グリッド表示
			ax1.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット

			close_price_lst = df_tmp_full["close_price"].values.flatten()
			# day_lst = [5, 10, 20, 40, 80]
			day_lst = [5, 10, 20]

			for day in day_lst:
				ax2.grid()  # グリッド表示
				ax2.set_xlim(df_tmp_full["date"].values[0], df_tmp_full["date"].values[-1])  # x軸の範囲
				fig.autofmt_xdate()  # x軸のオートフォーマット
				plt.plot(df_tmp_full["date"].values, df_tmp_full["atr_" + str(day)].values / df_tmp_full["close_price"], label="day-" + str(day))
			plt.legend()
			if not os.path.isdir(path):
				os.makedirs(path) 
			plt.savefig(os.path.join(path, str(id_str) + '_chart_w_atr.png'))#画像保存


	def plt_chart_w_rsi(self, path=os.path.join(os.getcwd(), "chart")):
		real_id_lst = self.df["stock_id"].drop_duplicates()

		for id_str in real_id_lst:
			df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
			df_tmp = df_tmp_full.ix[:, ['open_price', 'high_price','low_price', 'close_price']]

			fig = plt.figure()
			ax1 = plt.subplot(211)
			ax2 = plt.subplot(212)

			xdate = [x for x in df_tmp_full.date]  # 日付
			ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
			# mpf.candlestick_ochl(ax1, ochl, width=0.7, colorup='g', colordown='r')
			candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
			ax1.grid()  # グリッド表示
			ax1.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット

			close_price_lst = df_tmp_full["close_price"].values.flatten()

			ax2.grid()  # グリッド表示
			ax2.set_xlim(df_tmp_full["date"].values[0], df_tmp_full["date"].values[-1])  # x軸の範囲
			fig.autofmt_xdate()  # x軸のオートフォーマット
			plt.plot(df_tmp_full["date"].values, df_tmp_full["rsi"].values, label="rsi_14")
			plt.legend()
			if not os.path.isdir(path):
				os.makedirs(path) 
			plt.savefig(os.path.join(path, str(id_str) + '_chart_w_rsi.png'))#画像保存


	# def __set_support_point(self, price_lst, date_lst, num=50):
	# 	res_lst = []
	# 	res_date = []

	# 	fl_lst = np.ones(len(price_lst))

	# 	for i in range(num):
	# 		max_price = max(price_lst * fl_lst)
	# 		max_inds = np.where(price_lst == max_price)
	# 		for ind in max_inds[0]:
	# 			res_lst.append(max_price)
	# 			res_date.append(date_lst[ind])
	# 			fl_lst[ind] = 0

	# 	# print([res_lst, res_date])
	# 	return [res_lst, res_date]




	# def test(self, path=os.getcwd()):
	# 	real_id_lst = self.df["stock_id"].drop_duplicates()

	# 	for id_str in real_id_lst:
	# 		df_tmp_full = self.df[self.df.stock_id == id_str].sort_values(by=["date"], ascending=True)
	# 		df_tmp = df_tmp_full.ix[:, ['open_price', 'close_price', 'high_price','low_price']]
	# 		close_price_lst = df_tmp_full["close_price"].values.flatten()
	# 		date_lst = df_tmp_full["date"].values.flatten()

	# 		fig = plt.figure()
	# 		ax = plt.subplot()

	# 		[test_lst, test_date] = self.__set_support_point(close_price_lst, date_lst)

	# 		xdate = [x for x in df_tmp_full.date]  # 日付
	# 		ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
	# 		mpf.candlestick_ochl(ax, ochl, width=0.7, colorup='g', colordown='r')
	# 		ax.grid()  # グリッド表示
	# 		ax.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
	# 		fig.autofmt_xdate()  # x軸のオートフォーマット

	# 		plt.plot(test_date, test_lst, "ro")

	# 		plt.savefig(os.path.join(path, id_str + '_chart_w_move_avrg.png'))#画像保存		


	
if __name__ == '__main__': 
	main()
	


