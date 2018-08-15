from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import json
import time
from crud_for_stock_charts import CRUD_for_STOCK_CHARTS, CRUD_for_COMPANY_INFO


# - Define driverd
# browser = RoboBrowser(parser='html.parser') 
args = sys.argv # [0]:from page / [1]:to page
cwd = os.getcwd()
driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
DOWNLOADED_FILE_PATH = os.path.join(cwd, 'downloaded_invest_path_list')
chromeOptions = webdriver.ChromeOptions()
prefs = {
	"download.default_directory" : os.path.join(cwd, 'sources_invest'),
	"profile.default_content_setting_values.notifications" : 2
	}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)




def main():
	crud_for_ST = CRUD_for_STOCK_CHARTS()
	crud_for_CI = CRUD_for_COMPANY_INFO()
	stock_id_lst = crud_for_ST.get_id_lst()
	
	# crud_for_CI.create_tbl()
	start = time.time()

	err_lst = []
	for item in stock_id_lst:
		try:
			stock_id = item[0] # item is style as (stock_id, ), so we have to retrieve first val in it.
			print(stock_id)
			if is_saved(str(stock_id)):
				continue
			c_json = get_company_info(stock_id)
			crud_for_CI.update_tbl_from_json([c_json])
			# break
		except Exception as e:
			print([stock_id, e])
			err_lst.append([stock_id, e])

	print(err_lst)




def is_saved(stock_id):
	crud_for_CI = CRUD_for_COMPANY_INFO()
	r = crud_for_CI.read_tbl("WHERE STOCK_ID=" + str(stock_id))
	if len(r) > 0:
		return True
	else:
		return False


def get_company_info(stock_id):

	driver.get("http://www2.tse.or.jp/tseHpFront/JJK010030Action.do")

	tr_lst = driver.find_elements_by_css_selector("table.tableStyle01 > tbody > tr")
	input_itm = tr_lst[3].find_elements_by_css_selector("td > span > input")
	input_itm[0].send_keys(str(stock_id))

	input_btn = driver.find_element_by_css_selector("input.activeButton")
	input_btn.click()

	info_tbl = driver.find_element_by_css_selector("table.tableStyle01.fontsizeS") 
	info_tr_lst = info_tbl.find_elements_by_css_selector("tr")

	c_json = {
		"stock_id"      : str(stock_id),
		"market"        : info_tr_lst[3].find_elements_by_css_selector("td")[1].text,
		"head_q"        : info_tr_lst[3].find_elements_by_css_selector("td")[2].text,
		"stlmnt_month"  : info_tr_lst[3].find_elements_by_css_selector("td")[3].text,
		"name"          : info_tr_lst[4].find_elements_by_css_selector("td")[0].text,
		"category"      : info_tr_lst[4].find_elements_by_css_selector("td")[1].text,
	}

	return c_json



if __name__ == '__main__': 
	main()
	