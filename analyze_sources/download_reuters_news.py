from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import json
import time
from datetime import datetime, timedelta
from crud_for_news import CRUD_for_REUTERS

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
# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
crud = CRUD_for_REUTERS()

driver = webdriver.PhantomJS() 

def main():
	# The oldest link is https://www.reuters.com/resources/archive/jp/20070101.html
	base_url = "https://www.reuters.com/resources/archive/jp/%s.html"

	initial_d_str = args[1] # First news date
	d = datetime.strptime(initial_d_str, '%Y/%m/%d')
	d_str = d.strftime('%Y%m%d')

	while d <= datetime.now():
		try:
			print("***** " + d_str + " *****")
			news_lst = get_news(base_url, d_str)
			d += timedelta(days = 1)
			d_str = d.strftime('%Y%m%d')

		except Exception as e:
			print("Error detected: " + str(e))
			# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
			driver = webdriver.PhantomJS() 


def is_downloaded(url):
	r_lst = crud.read_tbl("WHERE URL='%s'" % (url))
	if len(r_lst) > 0:
		return True
	else:
		return False

def get_news(base_url, d_str):
	li_lts = []
	url_lst = []
	driver.get(base_url % d_str)
	a_lst = driver.find_elements_by_css_selector("div.primaryContent > div.module > div.headlineMed > a")
	for a in a_lst:
		url_lst.append(a.get_attribute("href"))
	for url in url_lst:
		if(is_downloaded(url)):
			print(str(url) + " DOWNLOADED *****" )
			continue
		else:
			try:
				while True:
					try:
						start = time.time()

						driver.get(url)
						id_str = str(url.split("/id")[-1])
						print("...1")
						info_div = driver.find_element_by_css_selector("div#"+id_str)
						head_info_div = info_div.find_element_by_css_selector("div > div > div > div > div > div")
						uploaded_date = head_info_div.find_elements_by_css_selector("div")[1].text
						print("...2")
						title = head_info_div.find_element_by_css_selector("h1").text
						contents_lst = info_div.find_elements_by_css_selector("p")
						contents = ""
						for c in contents_lst:
							contents += str(c.text)
						cur_json = {
							"date": datetime.strptime(d_str, '%Y%m%d'),
							"uploaded_date": uploaded_date.split("/")[1].replace(" ", ""),
							"title": title,
							"contents": contents,
							"url": url,
						}
						# break
						print("...3")			
						li_lts.append(cur_json)
						crud.update_tbl_from_json([cur_json])
						elapsed_time = time.time() - start

						print(url + " load done! Took [" + str(elapsed_time) + "] [STATUS]" + str(len(li_lts)) + "/" + str(len(url_lst)))


						# print(cur_json)
						break
					except IndexError:
						pass
			except Exception as e:
				print(str(url) + " error...")
	return li_lts



if __name__ == '__main__': 
	main()




