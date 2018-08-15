import os
import pandas as pd
import math
import json
from crud_for_investing_info import CRUD_for_INVESTING_INFO
from datetime import datetime, timedelta

path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/sources_invest_csv"

csv_lst = os.listdir(path)
crud = CRUD_for_INVESTING_INFO()
# col_lst = [
# 		"date", 
# 		"end_price", 
# 		"start_price", 
# 		"high_price", 
# 		"low_price", 
# 		"output"
# 		# "prev_ratio"
# 		]

col_lst = {
		"日付け":  "date",
		"終値":    "end_price",
		"始値":    "start_price",
		"高値":    "high_price",
		"安値":    "low_price",
		"出来高":  "output",
		"前日比%": "prev_ratio"
	}

for csv_f in csv_lst:
	try:
		stock_id_name = csv_f.replace("過去のデータ", "").replace(".csv", "").replace("(1)", "").replace("(2)", "").replace("(3)", "").replace("(4)", "").replace("(5)", "").replace("(6)", "").replace(" ", "_").strip("_")
		# print([csv_f, stock_id_name])
		f_path = os.path.join(path,csv_f)
		r = pd.read_csv(f_path, 
						encoding='utf-8_sig', 
						header=1, 
						names=col_lst, 
						skipinitialspace=True, 
						# index_col=0, 
						parse_dates=True)
		r = r.rename(columns=col_lst)
		if len(r) > 1:
			for i in range(len(r)):
				r_j = json.loads(r.iloc[i].to_json())
				if r_j["date"] is None:
					break

				r_j["output"] = str(r_j["output"]).replace(",", "")
				if str(r_j["output"]).find("K") > -1:
					r_j["output"] = "%f" % float(float(str(r_j["output"]).replace("K", "")) * 1000)
				if str(r_j["output"]).find("M") > -1:
					r_j["output"] = "%f" % float(float(str(r_j["output"]).replace("M", "")) * 1000000)
				if str(r_j["output"]).find("B") > -1:
					r_j["output"] = "%f" % float(float(str(r_j["output"]).replace("M", "")) * 1000000000)

				r_mod = {
					"date": datetime.strptime(r_j["date"], '%Y年%m月%d日'),
					"stock_id": stock_id_name,
					"end_price": float(str(r_j["end_price"]).replace(",", "")),
					"start_price": float(str(r_j["start_price"]).replace(",", "")),
					"high_price": float(str(r_j["high_price"]).replace(",", "")),
					"low_price": float(str(r_j["low_price"]).replace(",", "")),
					"output": float(r_j["output"]),
					# "prev_ratio": 0,
					"prev_ratio": float(r_j["prev_ratio"]),
				}
				# print(r_mod)
				crud.update_tbl_from_json([r_mod])

			# break
	except Exception as e:
		print([csv_f, e])


