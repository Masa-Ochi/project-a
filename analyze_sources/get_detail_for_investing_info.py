from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import json
import time
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL

cwd = os.getcwd()
# driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
# DOWNLOADED_FILE_PATH = os.path.join(cwd, 'downloaded_invest_path_list')
# chromeOptions = webdriver.ChromeOptions()
# prefs = {
# 	"download.default_directory" : os.path.join(cwd, 'sources_invest'),
# 	"profile.default_content_setting_values.notifications" : 2
# 	}
# chromeOptions.add_experimental_option("prefs",prefs)
# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
driver = webdriver.PhantomJS() 

def main():
	save_detail()


def save_detail():
	base_url = "https://jp.kabumap.com/servlets/kabumap/Action?SRC=marketList/base"
	driver.get(base_url)
	detail_lst = []

	select_btn = driver.find_element_by_css_selector("input#exch_all")
	select_btn.click()

	page_lst = []
	crud = CRUD_for_STOCK_DETAIL()

	# while len(page_lst) < 134:
	while len(page_lst) < 600:
		page_e_lst = driver.find_elements_by_css_selector("div.KM_TABLEINDEXANCHOR > a")
		for p_e in page_e_lst:
			page_lst.append(p_e.get_attribute("href"))
		print(page_lst[-1])
		driver.get(page_lst[-1])

		# break



	for tmp_url in page_lst[300:len(page_lst)]:
		driver.get(tmp_url)
		tbl_lst = driver.find_elements_by_css_selector("div.KM_TABLECONTENT > table > tbody > tr")
		for t in tbl_lst:
			tmp_td_lst = t.find_elements_by_css_selector("td")
			if len(tmp_td_lst) == 0:
				continue
			tmp_code   = tmp_td_lst[1].text
			tmp_name   = tmp_td_lst[2].text
			tmp_market = tmp_td_lst[3].text
			tmp_type   = tmp_td_lst[4].text
			tmp_j = {
				"stock_id":  tmp_code,
				"stock_name": tmp_name,
				"stock_market": tmp_market,
				"business_type": tmp_type,
			}
			print(tmp_j)
			crud.upsert_tbl_from_json([tmp_j])
			print(str(tmp_j["stock_id"]) + " is saved *****")


	
if __name__ == '__main__': 
	main()

