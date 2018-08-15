
import os
import sys
import codecs
import re

import numpy as np
from datetime import datetime
import pandas as pd

from crud_for_investing_charts import CRUD_for_INVESTING_CHARTS




def save_contents_into_file(content, f_path):
	f = open(f_path, 'a')
	f.write(str(content) + "\n")
	f.close()

def main():
	source_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/sources_invest_csv"
	file_name_lst = os.listdir(source_path)
	err_file_path = "./load_invest_csv_err"
	crud = CRUD_for_INVESTING_CHARTS()

	i=0
	for cur_file_name in file_name_lst:

		try:
			if i % 1000 == 0:
				print("%d / %d ----" % (i, len(file_name_lst)))
			i=i+1
			# cur_file_name = "BTC EUR BitStamp 過去のデータ (2).csv"
			print("--- open file: " +  cur_file_name)

			stock_id_name = cur_file_name.replace("過去のデータ", "").replace("履歴データ", "").replace(".csv", "").replace("$$$ ", "").replace(" ", "_").strip("_")
			stock_id_name = re.sub(r'\([0-9]\)+', "", stock_id_name)
			stock_id_name = re.sub(r'\_+$', "", stock_id_name)
			# print(stock_id_name)

			open_file_path = os.path.join(source_path, cur_file_name) 
			with codecs.open(open_file_path, "r", "utf-8", "ignore") as file:
				cur_df = pd.read_csv(file, encoding='utf-8', skiprows=1, skipfooter=2, sep=",", engine='python', names=["日付け","終値","始値","高値","安値","出来高","前日比%"])
			# print(cur_df.iloc[0:10])

			if len(cur_df) < 1:
				continue

			cur_df.columns = ["date", "close_price", "open_price", "high_price", "low_price", "output", "change_ratio"]
			cur_df["investing_id"] = stock_id_name
			cur_df = cur_df.fillna(0)
			cur_df["output"] = cur_df["output"].apply(lambda x: 0 if x == "-" else x)
			cur_df["output"] = cur_df["output"].apply(lambda x: 0 if str(x).find("%") > -1 else x)
			cur_df["date"] = cur_df["date"].apply(lambda x: datetime.strftime(datetime.strptime(x, '%Y年%m月%d日'), '%Y-%m-%d'))

			cur_df["close_price"] = cur_df["close_price"].apply(lambda x: float(str(x).replace(",", "")))
			cur_df["open_price"] = cur_df["open_price"].apply(lambda x: float(str(x).replace(",", "")))
			cur_df["high_price"] = cur_df["high_price"].apply(lambda x: float(str(x).replace(",", "")))
			cur_df["low_price"] = cur_df["low_price"].apply(lambda x: float(str(x).replace(",", "")))


			cur_df["output"] = cur_df["output"].apply(lambda x: str(x).replace(",", ""))
			cur_df["output"] = cur_df["output"].apply(lambda x: int(x) if isinstance(x, float) else x)
			cur_df["output"] = cur_df["output"].apply(lambda x: int(float(x.replace("K", ""))*1000) if str(x).find("K") > -1 else x)
			cur_df["output"] = cur_df["output"].apply(lambda x: int(float(x.replace("M", ""))*1000000) if str(x).find("M") > -1 else x)
			cur_df["output"] = cur_df["output"].apply(lambda x: int(float(x.replace("B", ""))*1000000000) if str(x).find("B") > -1 else x)
			cur_df["output"] = cur_df["output"].apply(lambda x: 0 if float(x) - int(float(x)) != 0 else int(float(x)))

			# print(cur_df.iloc[0:10])
			crud.upsert_tbl_from_df(cur_df)
			print("--- Load done...")
		except Exception as e:
			err_info = [e, cur_file_name]
			save_contents_into_file(err_info, err_file_path)
			pass


if __name__ == '__main__': 
	main()