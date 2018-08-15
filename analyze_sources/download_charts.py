from urllib.parse import urljoin
from robobrowser import RoboBrowser 

def main():
	BASE_URL = 'https://kabuoji3.com/stock/'

def get_list_pages(base_url):
	browser = RoboBrowser(parser='html.parser') 
	browser.open(base_url) 
	url_list = []
	for li in browser.select('ul.pager > li'): 
		a = li.select('a')[0]
		url = urljoin(base_url, a.get('href'))
		url_list.append(url)
	return url_list

def get_stock_id_pages(base_url):
	browser = RoboBrowser(parser='html.parser') 
	browser.open(base_url) 
	url_list = []
	for li in browser.select('tbody > tr'): 
		url = li.get('data-href')
		url_list.append(url)
	return url_list

def get_yearly_pages(base_url):
	browser = RoboBrowser(parser='html.parser') 
	browser.open(base_url)  
	url_list = []
	for li in browser.select('ul.stock_yselect > li'): 
		a = li.select('a')[0]
		url = urljoin(base_url, a.get('href'))
		url_list.append(url)
	return url_list

if __name__ == '__main__': 
	main()


# # 検索 語 を 入力 し て 送信 する。 
# form = browser.get_form(action='/stock') # フォーム を 取得。
# form['q'] = 'Python' # フォーム の q という 名前 の フィールド に 検索 語 を 入力。 
# browser.submit_form(form, list(form.submit_fields.values())[0]) # 一つ 目 の ボタン（ Google 検索） を 押す。 

# # 検索 結果 の タイトル と URL を 抽出 し て 表示 する。 
# # select() メソッド は Beautiful Soup の select() メソッド と 同じ もの で あり、 
# # 引数 の CSS セレクター に マッチ する 要素 に 対応 する Tag オブジェクト の リスト を 取得 できる。 
# for a in browser.select('h3 > a'): 
# 	print(a.text) 
# 	print(a.get('href'))
