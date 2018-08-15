import pandas as pd
import numpy as np
import os
import sys
from crud_for_stock_charts import CRUD_for_STOCK_CHARTS

import matplotlib.pyplot as plt
# import matplotlib.finance as mpf
from mpl_finance import candlestick_ohlc
from matplotlib.dates import date2num


base_date = '2018-01-01'

def update_charts_stats(stock_id):
	crud = CRUD_for_STOCK_CHARTS()
	date = base_date

	stock_id = int(stock_id)
	print("======= " + str(stock_id))
	try:
		sql = "WHERE STOCK_ID=%s AND DATE > '%s' ORDER BY DATE" % (stock_id, date)
		chart = crud.read_tbl_by_df(sql)
		chart = chart.rename(columns={'end_price': 'close_price', 'start_price': 'open_price'})

		if len(chart) > 80:
			get_atr(chart)
			get_move_avrg(chart)
			# plt_chart_atr(chart)
			get_rsi(chart)
			# print(chart)
			chart = chart.rename(columns={'close_price': 'end_price', 'open_price': 'start_price'})
			# print(chart)
			crud.upsert_tbl_from_df(chart)
			print("======= saved =======")

	except Exception as e:
		print("error: " + str(e))
	# break



def main():
	crud = CRUD_for_STOCK_CHARTS()
	sql = "SELECT distinct stock_id from stock_charts"
	id_lst = crud.read_tbl(sql, False)
	date = base_date

	for stock_id in id_lst:
		print("======= " + str(stock_id))
		try:
			sql = "WHERE STOCK_ID=%s AND DATE > '%s' ORDER BY DATE" % (stock_id, date)
			chart = crud.read_tbl_by_df(sql)
			chart = chart.rename(columns={'end_price': 'close_price', 'start_price': 'open_price'})

			if len(chart) > 80:
				get_atr(chart)
				get_move_avrg(chart)
				# plt_chart_atr(chart)
				get_rsi(chart)
				# print(chart)
				chart = chart.rename(columns={'close_price': 'end_price', 'open_price': 'start_price'})
				# print(chart)
				crud.upsert_tbl_from_df(chart)
				print("======= saved =======")

		except Exception as e:
			print("error: " + str(e))
		# break



def plt_chart_atr(chart, path=os.path.join(os.getcwd(), "tmp")):
	df_tmp_full = chart.sort_values(by=["date"], ascending=True)
	df_tmp = df_tmp_full.ix[:, ['open_price', 'close_price', 'high_price','low_price']]
	move_avrg_lst = [5, 10, 20, 40, 80]

	fig = plt.figure()
	ax = plt.subplot()

	xdate = [x for x in df_tmp_full.date]  # 日付
	ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
	# mpf.candlestick_ochl(ax, ochl, width=0.7, colorup='g', colordown='r')
	candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
	ax.grid()  # グリッド表示
	ax.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
	fig.autofmt_xdate()  # x軸のオートフォーマット

	plt.plot(df_tmp_full["date"], df_tmp_full["atr"], label="atr")
	plt.legend()

	plt.savefig(os.path.join(path, chart["stock_id"].values[0] + '_chart.png'))#画像保存


def plt_chart_move_avrg(chart, path=os.path.join(os.getcwd(), "tmp")):
	df_tmp_full = chart.sort_values(by=["date"], ascending=True)
	df_tmp = df_tmp_full.ix[:, ['open_price', 'close_price', 'high_price','low_price']]
	move_avrg_lst = [5, 10, 20, 40, 80]

	fig = plt.figure()
	ax = plt.subplot()

	xdate = [x for x in df_tmp_full.date]  # 日付
	ochl = np.vstack((date2num(xdate), df_tmp.values.T)).T
	# mpf.candlestick_ochl(ax, ochl, width=0.7, colorup='g', colordown='r')
	candlestick_ohlc(ax1, ochl, width=0.7, colorup='g', colordown='r')
	ax.grid()  # グリッド表示
	ax.set_xlim(df_tmp_full.iloc[0].date, df_tmp_full.iloc[-1].date)  # x軸の範囲
	fig.autofmt_xdate()  # x軸のオートフォーマット

	for day in move_avrg_lst:
		tmp_chart = chart.loc[:,["date", "move_avrg_" + str(day)]].sort_values(by=["date"], ascending=True).copy()
		print(tmp_chart)
		ax.grid()  # グリッド表示
		ax.set_xlim(tmp_chart["date"].values[0], tmp_chart["date"].values[-1])  # x軸の範囲
		fig.autofmt_xdate()  # x軸のオートフォーマット
		plt.plot(tmp_chart["date"], tmp_chart["move_avrg_" + str(day)], label="day-" + str(day))
	plt.legend()

	plt.savefig(os.path.join(path, chart["stock_id"].values[0] + '_chart.png'))#画像保存


def get_atr(chart, days_lst=[5, 10, 20, 40, 80]):		
	# chart.loc[:, "atr"] = np.zeros(len(chart))
	tmp_chart1 = chart.copy()
	tmp_chart2 = chart.copy()
	tmp_chart2["pre_close_price"] = np.r_[np.zeros(1), np.roll(tmp_chart1["close_price"].values.copy(), 1)[1:len(tmp_chart1["close_price"])]]
	tmp_chart2.iloc[0,:]["pre_close_price"] = tmp_chart1.iloc[0,:]["low_price"].copy()
	# for d in range(1, len(tmp_chart2)):
	# 	tmp_chart2.iloc[d, :]["pre_close_price"] = tmp_chart2.iloc[d-1, :]["close_price"]
	tmp_chart1 = pd.merge(tmp_chart1, tmp_chart2[["stock_id", "date", "pre_close_price"]])
	tmp_chart1["TR_h-c"] = np.absolute(tmp_chart1["high_price"]      - tmp_chart1["pre_close_price"])
	tmp_chart1["TR_c-l"] = np.absolute(tmp_chart1["pre_close_price"] - tmp_chart1["low_price"])
	tmp_chart1["TR_h-l"] = np.absolute(tmp_chart1["high_price"]      - tmp_chart1["low_price"])
	tmp_chart1["TR"] = tmp_chart1.loc[:,["TR_h-c", "TR_c-l", "TR_h-l"]].max(axis=1)
	ATR = tmp_chart1["TR"].values.copy()
	tmp_ATR = tmp_chart1["TR"].values.copy()
	for days in days_lst:
		for d in range(days):
			ATR += np.r_[np.zeros(d), np.roll(tmp_ATR, d)[d:len(tmp_ATR)]]
		ATR = ATR / (days + 1)
		chart.loc[:, "atr_" + str(days)] = ATR

def get_move_avrg(chart):
	day_lst = [5, 10, 20, 40, 80]

	df_tmp_full = chart.sort_values(by=["date"], ascending=True).copy()
	date_lst = df_tmp_full["date"].values.flatten()

	xdate = [x for x in df_tmp_full.date]  # 日付
	close_price_lst = df_tmp_full["close_price"].values.flatten()
	for day in day_lst:
		move_avrg = np.zeros([len(close_price_lst)])
		for i in range(len(close_price_lst)):
			if i < day:
				move_avrg[i] = np.sum(close_price_lst[0:i]) / (i+1)
			else:
				move_avrg[i] = np.sum(close_price_lst[i-day:i]) / day

		chart.loc[:, "move_avrg_" + str(day)] = move_avrg


def get_rsi(chart, day=14):
	df_tmp_full = chart.copy()
	date_lst = df_tmp_full["date"].values.flatten()

	xdate = [x for x in df_tmp_full.date]  # 日付
	close_price_lst = df_tmp_full["close_price"].values.flatten()
	
	for i in range(1, len(date_lst)):
		df_tmp_full.loc[df_tmp_full["date"] == date_lst[i], "diff"] = \
				df_tmp_full.loc[df_tmp_full["date"] == date_lst[i], "close_price"].values[0] - \
				df_tmp_full.loc[df_tmp_full["date"] == date_lst[i-1], "close_price"].values[0]
	

	rsi = np.zeros([len(chart)])
	# chart.loc[:, "rsi"] = np.zeros([len(chart)])
	for i in range(len(chart)):
		if i >= day:
			sum_up_df   = df_tmp_full.iloc[i-day:i].loc[df_tmp_full["diff"] >0, "diff"]
			sum_down_df = df_tmp_full.iloc[i-day:i].loc[df_tmp_full["diff"] <0, "diff"]
			sum_up_avrg   = sum_up_df.sum() / len(sum_up_df)            if len(sum_up_df) != 0 else 0
			sum_down_avrg = sum_down_df.sum() * (-1) / len(sum_down_df) if len(sum_down_df) != 0 else 0
			rsi[i] = sum_up_avrg / (sum_up_avrg + sum_down_avrg) * 100  if (sum_up_avrg + sum_down_avrg) != 0 else 0
	chart.loc[:, "rsi"] = rsi

if __name__ == '__main__': 
	main()