from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import json
import time
import datetime
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL

# cwd = os.getcwd()
# driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
# DOWNLOADED_FILE_PATH = os.path.join(cwd, 'downloaded_invest_path_list')
# chromeOptions = webdriver.ChromeOptions()
# prefs = {
# 	"download.default_directory" : os.path.join(cwd, 'sources_invest'),
# 	"profile.default_content_setting_values.notifications" : 2
# 	}
# chromeOptions.add_experimental_option("prefs",prefs)
# driver_main = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
# driver_sub  = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)

driver_main = webdriver.PhantomJS() 
driver_sub  = webdriver.PhantomJS() 

def main():
	save_detail()

def save_detail():
	base_url = "https://jp.kabumap.com/servlets/kabumap/Action?SRC=marketList/base"
	driver_main.get(base_url)
	detail_lst = []

	select_btn = driver_main.find_element_by_css_selector("input#exch_all")
	select_btn.click()

	page_lst = []
	crud = CRUD_for_STOCK_DETAIL()

	# while len(page_lst) < 134:
	while 1==1:
		page_e_lst = driver_main.find_elements_by_css_selector("div.KM_TABLEINDEXANCHOR > a")
		if page_e_lst[-1].get_attribute("href") in page_lst:
			break
		for p_e in page_e_lst:
			if p_e.get_attribute("href") not in page_lst:
				page_lst.append(p_e.get_attribute("href"))
		print(page_lst[-1])
		driver_main.get(page_lst[-1])

		# break

	cur_items = crud.read_tbl_by_df()
	for tmp_url in page_lst:
		driver_main.get(tmp_url)
		tbl_lst = driver_main.find_elements_by_css_selector("div.KM_TABLECONTENT > table > tbody > tr")
		for t in tbl_lst:
			start = time.time()
			# try:
			tmp_td_lst = t.find_elements_by_css_selector("td")
			if len(tmp_td_lst) == 0:
				continue
			tmp_id       = tmp_td_lst[1].text
			tmp_detail_url = tmp_td_lst[1].find_element_by_css_selector("a").get_attribute("href")
			tmp_name       = tmp_td_lst[2].text
			tmp_market     = tmp_td_lst[3].text
			tmp_type       = tmp_td_lst[4].text
			# print(tmp_detail_url)
			driver_sub.get(tmp_detail_url)
			tmp_unit       = driver_sub.find_element_by_css_selector("span#minUnit").text.replace(",","")

			tmp_j = {}
			tmp_j = {
				"stock_id"     : tmp_id,
				"stock_name"   : tmp_name,
				"stock_market" : tmp_market,
				"business_type": tmp_type,
				"stock_unit"   : tmp_unit,
			}

			this_stock_detail = cur_items.loc[cur_items["stock_id"]==str(tmp_id), :]
			if len(this_stock_detail) > 0:
				conditions = []
				for cid in tmp_j:
					conditions.append(str(this_stock_detail[cid].values[0]) == str(tmp_j[cid]))
				if False not in conditions:
					print(str(tmp_j["stock_id"]) + " is not saved -----")
					break

			tmp_j["update_date"] = datetime.datetime.now()
			print(tmp_j)
			crud.upsert_tbl_from_json([tmp_j])
			print(str(tmp_j["stock_id"]) + " is saved *****")
			# except Exception as e:
			# 	print("#### Error ####")
			# 	print(tmp_url)
			# 	print(tmp_detail_url)
			# 	print(e)

			elapsed_time = time.time() - start
			print ("***** get_predict_price_by_models time:{0}".format(elapsed_time) + "[sec]")


	
if __name__ == '__main__': 
	main()

