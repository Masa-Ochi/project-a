from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
import os
import sys
import json
from crud_for_stock_charts import  CRUD_for_STOCK_CHARTS
import datetime
import pandas as pd
import time


class download_rakuten_selenium(object):

	def __init__(self):
		#### For test start ---
		args = sys.argv # [0]:from page / [1]:to page
		cwd = os.getcwd()
		driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
		chromeOptions = webdriver.ChromeOptions()
		prefs = {"download.default_directory" : os.path.join(cwd, 'sources')}
		chromeOptions.add_experimental_option("prefs",prefs)
		self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
		#### For test end -----

		# self.driver = webdriver.PhantomJS()

		url = "https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html"
		self.driver.get(url) 
		logid = self.driver.find_element_by_css_selector('input#form-login-id').send_keys("BGYX8479")
		password = self.driver.find_element_by_css_selector('input#form-login-pass').send_keys("masa12761@Ochi")
		login_btn = self.driver.find_element_by_css_selector("button#login-btn").click()

	def close(self):
		self.driver.close()

	def get_cur_price(self, id_lst):

		return_df = pd.DataFrame()
		start = time.time()
		for cur_id in id_lst:
			try:
				id_input = self.driver.find_element_by_css_selector("input.header-text-search").send_keys(str(cur_id))
				login_btn = self.driver.find_element_by_css_selector("button.rc-h-search-btn").click()
				cur_price = self.driver.find_element_by_css_selector("td.price-01").text.replace(",", "")
				cur_time  = self.driver.find_element_by_css_selector("td.time-01").text

				cur_Y = datetime.datetime.today().year
				cur_m = datetime.datetime.today().month
				cur_d = datetime.datetime.today().day
				cur_H = cur_time[1:cur_time.find(":")]
				cur_M = cur_time[cur_time.find(":")+1:cur_time.find(":")+3]
				cur_S = cur_time[cur_time.find(":")+4:cur_time.find(":")+6]
				cur_date_str = str(cur_Y)+"-"+str(cur_m)+"-"+str(cur_d)+" "+str(cur_H)+":"+str(cur_M)+":"+str(cur_S)
				cur_date = datetime.datetime.strptime(cur_date_str, "%Y-%m-%d %H:%M:%S")
				cur_text = str(cur_id) + "," + cur_date_str + "," + cur_price

				with open("./price_records/" + str(cur_id), 'a') as f:
					f.write(cur_text)
					f.write("\n")

				tmp_series = pd.Series()
				tmp_series["stock_id"] = cur_id
				tmp_series["date"]     = cur_date_str
				tmp_series["price"]    = cur_price
				return_df = return_df.append(tmp_series, ignore_index=True)
			except Exception as e:
				print("Error .....")
				print(cur_id)
				print(e)
				pass

		elapsed_time = time.time() - start
		print ("***** get_cur_price time:{0}".format(elapsed_time) + "[sec]")
		return return_df







