import numpy as np
import math
import pickle
import _pickle as cPickle
import time
# from time import sleep
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
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras.layers import LSTM
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint

from download_charts_selenium import *
from stock_charts_updateDB import *

import download_rakuten_selenium

import download_charts_selenium as dcs
import stock_charts_updateDB as scud


class held_stock(object):
	def __init__(self, stock_id, bought_date, bought_price, bought_amount, unit, cur_d=datetime.today()):
		self.stock_id = stock_id
		self.b_date   = bought_date
		self.b_price  = bought_price
		self.b_amount = bought_amount
		self.unit     = unit
		self.ii_obj   = ii.investing_info([self.stock_id], cur_d-timedelta(days=365), cur_d)

	def update_ii_obj(self, d=datetime.today()):
		dcs.update_stock(self.stock_id)
		scud.update_charts_stats(self.stock_id)
		self.ii_obj = ii.investing_info([self.stock_id], d-timedelta(days=365), d, True)


class trade_mgr(object):
	def __init__(self, budget, held_stock_lst, logic_mgr):
		print("Init trade_mgr...")
		self.set_budget(budget)
		self.set_held_stock(held_stock_lst)
		self.set_logic_mgr(logic_mgr)

	def set_budget(self, budget):
		self.budget = budget
		
	def set_held_stock(self, held_stock_lst):
		self.available_price = self.budget
		self.hs_lst = held_stock_lst
		if len(self.hs_lst) < 1:
			return self.budget
		for cur_hs in self.hs_lst:
			self.available_price = self.available_price - cur_hs.b_price

	def set_logic_mgr(self, logic_mgr):
		self.l_mgr = logic_mgr

	def set_ii_obj(self, ii_obj):
		self.ii_obj = ii_obj

	def get_hs_ids(self):
		id_lst = []
		for hs in self.hs_lst:
			id_lst.append(hs.stock_id)
		return id_lst

	# Check stock to be bought or sold at a date [check_date].
	# Set [update_fl] to update stock_charts DB.
	def run_daily_check(self, print_detail=False): 
	# def run_daily_check(self, market_name, check_date=datetime.today()+timedelta(days=1), update_fl=False): 
		# ii_obj = ii.get_ii_obj_by_stock_market(market_name, date(2018,1,1), check_date, update_fl)
		cur_date       = self.ii_obj.df["date"].iloc[-1]
		predicted_date = cur_date + timedelta(days=1)
		b_suggest_lst = self.l_mgr.apply_buy_rule(self.ii_obj, self.available_price, print_detail)
		s_suggest_lst = self.l_mgr.apply_sell_rule(self.hs_lst, self.available_price, predicted_date)

		return b_suggest_lst, s_suggest_lst


	def run_check_while_market_open(self, id_lst, update_fl=False):
		# ii_obj = try_to_load_as_pickled_object_or_None("tmp_30/pkls/full/ii_obj.pkl")
		# id_lst = ii_obj.df["stock_id"].drop_duplicates().values
		# id_lst = ii.get_ii_obj_by_stock_market("東証二部", datetime.today()-timedelta(days=2), datetime.today(), update_fl).id_lst

		while 1==1:
			start = time.time()
			cur_datetime = datetime.now()
			print("***** " + cur_datetime.strftime('%Y/%m/%d %H:%M:%s'))
			# if (cur_datetime.hour < 9) & (cur_datetime.hour <= 15):
			if (cur_datetime.hour >= 9) & (cur_datetime.hour <= 15):
				if not((cur_datetime.hour == 11) & (cur_datetime.minute > 30)) | ((cur_datetime.hour == 12) & (cur_datetime.minute < 30)):
					print("*** Current prices are retrieved...")
					drs = download_rakuten_selenium.download_rakuten_selenium()
					drs.get_cur_price(id_lst)
					drs.close()
			elapsed_time = time.time() - start
			time.sleep(max(300-elapsed_time, 0))

















