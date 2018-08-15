from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
import os
import sys
import json
from crud_for_stock_charts import  CRUD_for_STOCK_CHARTS



# - Define driverd
# browser = RoboBrowser(parser='html.parser') 
args = sys.argv # [0]:from page / [1]:to page
cwd = os.getcwd()
driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : os.path.join(cwd, 'sources')}
chromeOptions.add_experimental_option("prefs",prefs)
# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
# driver.close()

# - Load downloaded list
downloaded_json_list = []
with open(os.path.join(cwd, 'downloaded_path_list'), 'r') as f:
	for line in f:
		downloaded_json_list.append(json.loads(line))


crud = CRUD_for_STOCK_CHARTS()

# - Main method
def main():
	print("start")
	downloaded_list = []
	for page in get_list_pages('https://kabuoji3.com/stock/'):
		print(page['key'])
		if int(page['key']) not in range(int(args[1]), int(args[2])):
			continue
		print('page:' + page['key'])
		for stock_id in get_stock_id_pages(page['url']):
			print('stockId:' + stock_id['key'])
			# # ===== Temp rule START ======
			# if int(stock_id['key']) < 1366:
			# 	continue
			# # ===== Temp rule END   ======
			for year in get_yearly_pages(stock_id['url']):

				# ==== Check URL to be downloaded START ====
				if year['url'] == stock_id['url']:
					continue
				# Json based on urlparse contents
				downloaded_item = urlparse(year['url'])
				downloaded_path = {
					"scheme"  : downloaded_item.scheme, 
					"netloc"  : downloaded_item.netloc, 
					"path"    : downloaded_item.path, 
					"params"  : downloaded_item.params, 
					"query"   : downloaded_item.query, 
					"fragment": downloaded_item.fragment,
					}
				if is_downloaded(downloaded_path):
					continue
				# ==== Check URL to be downloaded END   ====

				download_csv(year['url'])
				save_file(json.dumps(downloaded_path))


def save_file(content):
	f = open(os.path.join(cwd, 'downloaded_path_list'), 'a')
	f.write(str(content) + "\n")
	f.close()


def is_downloaded(downloaded_path):
	if downloaded_path in downloaded_json_list:
		return True
	else:
		return False

def download_csv(url): 
	try:
		driver.get(url) 
		input_element = driver.find_element_by_name('csv') 
		input_element.click()
		input_element = driver.find_element_by_name('csv') 
		input_element.click()
	except Exception as e:
		print(e)

def get_list_pages(base_url):
	# browser.open(base_url)
	driver.get(base_url)
	url_list = []
	# for li in browser.select('ul.pager > li'):
	for a in driver.find_elements_by_css_selector('ul.pager > li > a'):
		url = {
				'key': a.text,
				'url': urljoin(base_url, a.get_attribute('href')),
			}
		url_list.append(url)
	return url_list

def get_stock_id_pages(base_url):
	# browser.open(base_url) 
	driver.get(base_url)
	url_list = []
	# for li in browser.select('tbody > tr'): 
	for a in driver.find_elements_by_css_selector('tbody > tr > td > a'): 
		url = {
				'key': a.text[0:4],
				'url': a.get_attribute('href'),
			}
		url_list.append(url)
	return url_list

def get_yearly_pages(base_url):
	# browser.open(base_url)  
	driver.get(base_url)
	url_list = []
	# for li in browser.select('ul.stock_yselect > li'): 
	for a in driver.find_elements_by_css_selector('ul.stock_yselect > li > a'): 
		# a = li.select('a')[0]
		url = {
				'key': a.text,
				'url': urljoin(base_url, a.get_attribute('href')),
			}
		url_list.append(url)
	return url_list


def is_saved(json):
	sql = "WHERE stock_id=%s AND date='%s'"%(json['stock_id'], json['date'])
	tmp_lst = crud.read_tbl(sql)
	if len(tmp_lst) > 0:
		return True
	else:
		return False


def update_stock(stock_id):
	update_driver = webdriver.PhantomJS()  # ここがかわった
	stock_url_300days = "https://kabuoji3.com/stock/%s/"%stock_id
	update_driver.get(stock_url_300days)
	item_tbl = update_driver.find_element_by_css_selector("table.stock_table.stock_data_table")
	save_lst = []
	tbody_lst = item_tbl.find_elements_by_css_selector("tbody")

	for tbody in tbody_lst:
		tmp_i = tbody.find_elements_by_css_selector("tr > td")
		tmp_j = {
			"stock_id"     : stock_id,
			"date"         : tmp_i[0].text,
			"start_price"  : tmp_i[1].text,
			"high_price"   : tmp_i[2].text,
			"low_price"    : tmp_i[3].text,
			"end_price"    : tmp_i[4].text,
			"output"       : tmp_i[5].text,
			"adjusted_val" : tmp_i[6].text,
			}

		if not is_saved(tmp_j):
			save_lst.append(tmp_j)
			# print(tmp_j)
		else:
			break

	print("Retrieve done...")
	crud.insert_tbl_by_json(save_lst)
	# print(save_lst)
	# print("is saved...")

def update_charts():
	id_lst = crud.get_id_lst()
	done_lst=[]
	for tmp_id in id_lst:
		try:
			update_stock(tmp_id[0])
			done_lst.append(tmp_id[0])
			print("###" + str(tmp_id[0]) + " is saved..." + str(len(done_lst)) + "/" + str(len(id_lst)) + "###")
		except Exception as e:
			print("################### " + str(tmp_id) + " ERROR ##################")
			print(e)

if __name__ == '__main__': 
	main()





