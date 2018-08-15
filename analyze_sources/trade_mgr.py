import numpy as np
import math
import pickle
import _pickle as cPickle
import time
# from time import sleep
import os
import sys
from datetime import datetime, timedelta
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


class held_stock(object):
	def __init__(self, stock_id, bought_date, bought_prices, cur_d=datetime.today()):
		self.stock_id = stock_id
		self.b_date   = bought_date
		self.b_prices = bought_prices
		self.ii_obj = ii.investing_info([self.stock_id], self.b_date, cur_d)

	def update_ii_obj(self, d=datetime.today()):
		self.ii_obj = ii.investing_info([self.stock_id], self.b_date, d, True)		


class trade_mgr(object):

	def __init__(self):
		print("Init trade_mgr...")


	def start_simulation(self):
		# ii_obj = try_to_load_as_pickled_object_or_None("tmp_30/pkls/full/ii_obj.pkl")
		# id_lst = ii_obj.df["stock_id"].drop_duplicates().values
		id_lst = [6502, 7502, 1357, 3402, 4208]
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

















