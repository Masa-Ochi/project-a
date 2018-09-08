from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import sys
import json
import time
import timeout_decorator

from crud_for_investing_info import CRUD_for_INVESTING_INFO


args = sys.argv # [0]:from page / [1]:to page
cwd = os.getcwd()
driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
DOWNLOADED_URL_PATH = os.path.join(cwd, 'downloaded_url_list')
ERR_URL_PATH = os.path.join(cwd, 'err_url_list')
chromeOptions = webdriver.ChromeOptions()
prefs = {
	"download.default_directory" : os.path.join(cwd, 'sources_invest_csv'),
	"profile.default_content_setting_values.notifications" : 2
	}
chromeOptions.add_experimental_option("prefs",prefs)
# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
driver_main = webdriver.PhantomJS() 


class main_currency_pair_dwnld(object):

	def login(self, base_url):
		mail_str = "masa.ochi.74@gmail.com"
		pswd_str = "12761masa"
		self.driver.get(base_url)
		while True:
			try:
				login_btn = self.driver.find_element_by_css_selector("div.topBarText > a.login.bold")
				login_btn.click()
				login_form = self.driver.find_element_by_css_selector("form#loginPopupform")
				form_mail = login_form.find_element_by_css_selector("input#loginFormUser_email")
				form_mail.send_keys(mail_str)
				form_pswd = login_form.find_element_by_css_selector("input#loginForm_password")
				form_pswd.send_keys(pswd_str)
				form_pswd.send_keys(Keys.RETURN)
				# form_btn = login_form.find_element_by_css_selector("a.newButton.orange")
				# form_btn.click()
				break
			except Exception as e:
				self.driver.save_screenshot('search_results.png') 
				print(e)
				close_btn = self.driver.find_element_by_css_selector("div.signupWrap.js-gen-popup.dark_graph > div.right > i.popupCloseIcon")
				close_btn.click()
				pass


	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		# self.driver = webdriver.PhantomJS() 
		self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
		
		login_url = "https://jp.investing.com/"
		self.login(login_url)

		url = "https://jp.investing.com/currencies/streaming-forex-rates-majors"
		self.driver.get(url)
		self.detail_url_lst = []
		crud = CRUD_for_INVESTING_INFO()

	def get_lst(self):
		# self.detail_url_lst = self.driver.find_elements_by_css_selector("table.genTbl.closedTbl.crossRatesTbl > tbody > tr > a")
		for el in self.driver.find_elements_by_css_selector("table.genTbl > tbody > tr > td > a"):
			self.detail_url_lst.append(el.get_attribute("href"))

	def dwnld_set(self):
		if(len(self.detail_url_lst) < 1):
			print("No url is set....")
			return
		for cur_url in self.detail_url_lst:
			print(cur_url)
			get_historical_items(cur_url, self.driver)


class main_currency_pair_dwnld(object):

	def login(self, base_url):
		mail_str = "masa.ochi.74@gmail.com"
		pswd_str = "12761masa"
		self.driver.get(base_url)
		while True:
			try:
				login_btn = self.driver.find_element_by_css_selector("div.topBarText > a.login.bold")
				login_btn.click()
				login_form = self.driver.find_element_by_css_selector("form#loginPopupform")
				form_mail = login_form.find_element_by_css_selector("input#loginFormUser_email")
				form_mail.send_keys(mail_str)
				form_pswd = login_form.find_element_by_css_selector("input#loginForm_password")
				form_pswd.send_keys(pswd_str)
				form_pswd.send_keys(Keys.RETURN)
				# form_btn = login_form.find_element_by_css_selector("a.newButton.orange")
				# form_btn.click()
				break
			except Exception as e:
				self.driver.save_screenshot('search_results.png') 
				print(e)
				close_btn = self.driver.find_element_by_css_selector("div.signupWrap.js-gen-popup.dark_graph > div.right > i.popupCloseIcon")
				close_btn.click()
				pass


	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		# self.driver = webdriver.PhantomJS() 
		self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
		
		login_url = "https://jp.investing.com/"
		self.login(login_url)

		url = "https://jp.investing.com/currencies/streaming-forex-rates-majors"
		self.driver.get(url)
		self.detail_url_lst = []
		crud = CRUD_for_INVESTING_INFO()

	def get_lst(self):
		# self.detail_url_lst = self.driver.find_elements_by_css_selector("table.genTbl.closedTbl.crossRatesTbl > tbody > tr > a")
		for el in self.driver.find_elements_by_css_selector("table.genTbl > tbody > tr > td > a"):
			self.detail_url_lst.append(el.get_attribute("href"))

	def dwnld_set(self):
		if(len(self.detail_url_lst) < 1):
			print("No url is set....")
			return
		for cur_url in self.detail_url_lst:
			print(cur_url)
			get_historical_items(cur_url, self.driver)



def main():
	url = "https://jp.investing.com/"
	login(url)
	for page in get_list_pages(url)[int(args[1]):int(args[2])]:
		for item in get_whole_items(page['url']):
			while True:
				try:
					target_url = item['url']
					print(target_url)
					get_historical_items(target_url)
					break

				except Exception as e:
					err_r = [target_url, e]
					save_contents_into_file(err_r, ERR_URL_PATH)
					driver.refresh()
					if str(e).find("Cannot navigate to invalid URL"):
						break					
					# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
					pass

			# save_file_as_csv(target_id, get_historical_items(target_url))
			# save_id_into_list(target_id)



def save_contents_into_file(content, f_path):
	f = open(f_path, 'a')
	f.write(str(content) + "\n")
	f.close()

def is_downloaded(target_id):
	downloaded_id_list = []
	with open(DOWNLOADED_URL_PATH, 'r') as f:
		for line in f:
			downloaded_id_list.append(line.replace("\n", ""))
	# print(downloaded_id_list)
	if target_id in downloaded_id_list:
		return True
	else:
		return False

# def is_saved(json, name):
# 	csv = change_to_CSV(json)
# 	with open(os.path.join(cwd, 'sources_invest/' + name + '.csv')) as f:
# 		contents = f.read()
# 	if contents.find(csv):
# 		return True
# 	else:
# 		return False


# def change_to_CSV(json_contents):
# 	csv_contents = []
# 	for json in json_contents:
# 		csv_r = (str(json['invest_id']) + ',' +
# 						str(json['date']) + ',' + 
# 						str(json['start_price']) + ',' + 
# 						str(json['high_price']) + ',' + 
# 						str(json['low_price']) + ',' + 
# 						str(json['end_price']) + ',' + 
# 						str(json['name']))
# 		csv_contents.append(csv_r)
# 	return csv_contents


# def save_file_as_csv(name, contents):
# 	csv_contents = change_to_CSV(contents)
# 	with open(os.path.join(cwd, 'sources_invest/' + name + '.csv'), 'a') as f: 
# 		for csv_content in csv_contents:
# 			f.write(str(csv_content) + "\n")
		

@timeout_decorator.timeout(120)
def get_historical_items(base_url, driver=driver_main):
	start = time.time()

	driver.get(base_url)
	url_list = []
	a_lst = driver.find_elements_by_css_selector("ul.arial_12 > li > a")
	invest_id = driver.find_element_by_css_selector("h1.float_lang_base_1").text
	historical_url = ""
	for a in a_lst:
		if a.get_attribute("href").find("historical") > 0:
			historical_url = a.get_attribute("href")
			break
	isNotOpened = True # Not to open url before check "is_downloaded"

	# for cur_oldest_date in [["1980/01/01", "1997/12/31"], ["1998/01/01", "2015/12/31"], ["2016/01/01", "2019/01/01"]]:
	for cur_oldest_date in [["2018/01/01", "2019/01/01"]]:
		if is_downloaded(str([historical_url, cur_oldest_date])):
			print("--- " + str([historical_url, cur_oldest_date]) + " DOWNLOADED ---")
			continue
		else:
			if isNotOpened:
				driver.get(historical_url)
				isNotOpened = False

		print("***** " + str([historical_url, cur_oldest_date]) + " DOWNLOADING")
		while True:
			calender_btn = driver.find_element_by_css_selector("div.float_lang_base_1#widget")
			try:
				calender_btn.click()
				driver.implicitly_wait(10)
				start_date_input = driver.find_element_by_css_selector("input.newInput#startDate")
				start_date_input.clear()
				start_date_input.send_keys(cur_oldest_date[0])
				end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
				end_date_input.clear()
				end_date_input.send_keys(cur_oldest_date[1])
				break

			except Exception as e:
				driver.save_screenshot('search_results.png') 
				pass

		while True:
			try:
				end_date_input.send_keys(Keys.RETURN)
				driver.implicitly_wait(30)
				# WebDriverWait(driver, 10).until(
				# 	EC.title_contains("Google")
				# )

				# dwnld_btn = driver.find_element_by_css_selector("a.newBtn.LightGray.downloadBlueIcon.js-download-hist-data")
				dwnld_btn = driver.find_element_by_css_selector("a.newBtn.LightGray.downloadBlueIcon.js-download-data")
				dwnld_btn.click()
				break
			except:
				end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
				pass


		# while True:
		# 	try:
		# 		end_date_input.send_keys(Keys.RETURN)
		# 		driver.implicitly_wait(10)
		# 		historical_item_lst = driver.find_elements_by_css_selector("div#results_box > table#curr_table > tbody > tr")
		# 		print("enter clicked")
		# 		break
		# 	except:
		# 		driver.save_screenshot('search_results.png') 
		# 		end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
		# 		pass
		# for historical_item in historical_item_lst:
		# 	try:
		# 		historical_item_val = historical_item.find_elements_by_css_selector("td")
		# 		url = {
		# 				# 'date': historical_item_val[0].text,
		# 				# 'invest_id': base_url.split("/")[-1],
		# 				# 'name': invest_id,
		# 				# 'end_price': historical_item_val[1].text,
		# 				# 'start_price': historical_item_val[2].text,
		# 				# 'high_price': historical_item_val[3].text,
		# 				# 'low_price': historical_item_val[4].text,
		# 				'date': historical_item_val[0].text,
		# 				'invest_id': base_url.split("/")[-1],
		# 				'name': invest_id,
		# 				'end_price': historical_item_val[1].get_attribute("data-real-value"),
		# 				'start_price': historical_item_val[2].get_attribute("data-real-value"),
		# 				'high_price': historical_item_val[3].get_attribute("data-real-value"),
		# 				'low_price': historical_item_val[4].get_attribute("data-real-value"),
		# 				# 'output': historical_item_val[5].text,
		# 				# 'preb_change': historical_item_val[6].text,
		# 			}
		# 		# if is_saved([url], invest_id):
		# 		# 	continue  # On the assumption that the items is in order of its date
		# 		url_list.append(url)
		# 		# print(str(len(url_list)) + "/" + str(len(historical_item_lst)) + " has done...")
		# 	except Exception as e:
		# 		print(e)
		# 		pass
		# print("hist_lst: " + str(len(historical_item_lst)))
		save_contents_into_file(str([historical_url, cur_oldest_date]), DOWNLOADED_URL_PATH)
		elapsed_time = time.time() - start
		print ("Download_time:{0}".format(elapsed_time) + "[sec] *****")
	return url_list	


def get_whole_items(base_url):
	start = time.time()
	driver.get(base_url)
	url_list = []
	for a in driver.find_elements_by_css_selector("tbody > tr > td > a"):
		if a.get_attribute('href') == "javascript:void(0);":
			continue
		url = {
				'key': a.text,
				'url': a.get_attribute('href'),
			}
		url_list.append(url)
	elapsed_time = time.time() - start
	print ("*** [get_whole_items]elapsed_time:{0}".format(elapsed_time) + "[sec]")
	return url_list	


def get_list_pages(base_url):
	start = time.time()
	driver.get(base_url)
	url_list = []
	for a in driver.find_elements_by_css_selector("ul.subMenuNav > li > div > ul > li > a"):
		url = {
				'key': a.text,
				'url': a.get_attribute('href'),
			}
		url_list.append(url)
		# break # For test
	elapsed_time = time.time() - start
	print ("*** [get_list_pages]elapsed_time:{0}".format(elapsed_time) + "[sec]")
	return url_list


def login(base_url):
	mail_str = "masa.ochi.74@gmail.com"
	pswd_str = "12761masa"
	driver.get(base_url)
	while True:
		try:
			login_btn = driver.find_element_by_css_selector("div.topBarText > a.login.bold")
			login_btn.click()
			login_form = driver.find_element_by_css_selector("form#loginPopupform")
			form_mail = login_form.find_element_by_css_selector("input#loginFormUser_email")
			form_mail.send_keys(mail_str)
			form_pswd = login_form.find_element_by_css_selector("input#loginForm_password")
			form_pswd.send_keys(pswd_str)
			form_pswd.send_keys(Keys.RETURN)
			# form_btn = login_form.find_element_by_css_selector("a.newButton.orange")
			# form_btn.click()
			break
		except Exception as e:
			driver.save_screenshot('search_results.png') 
			print(e)
			close_btn = driver.find_element_by_css_selector("div.signupWrap.js-gen-popup.dark_graph > div.right > i.popupCloseIcon")
			close_btn.click()
			pass




if __name__ == '__main__': 
	main()
	# test_main()

