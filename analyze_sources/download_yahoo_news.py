from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import json
import time
from datetime import datetime

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



#http://klug-fx.jp/fxnews/daily.php?ymd=2008-02-01


def main():
	# The oldest link is https://news.yahoo.co.jp/list/?c=economy&d=20080804
	base_url = "https://news.yahoo.co.jp/list/?c=%(c)s&d=%(d)s&p=%(p)s"
	category = [
			"economy",
			"world",
			"domestic",
			"computer",
			"science"
		]
	
	string_date = '2008/08/08'
	date = datetime.strptime(string_date, '%Y/%m/%d')
	d_str = date.strftime('%Y%m%d')
	p_num = 1

	news_lst = get_news(base_url, category[0], d_str)
	print(news_lst)



def get_news(base_url, category, d_str):
	li_lts = []
	for p_num in range(1,200000): # max page is less than 200000
		driver.get(base_url % dict(c=category, d=d_str, p=str(p_num)))
		cur_li = driver.find_elements_by_css_selector("dl.title > dt")
		if len(cur_li) == 0:
			break
		for item in cur_li:
			li_lts.append(item.text)

	return li_lts



if __name__ == '__main__': 
	main()














