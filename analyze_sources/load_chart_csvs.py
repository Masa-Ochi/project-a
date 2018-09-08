import pandas as pd
import my_util as my_util
from crud_for_stock_charts import CRUD_for_STOCK_CHARTS
import datetime


def main():
	l = load_chart_csvs()
	print(l.load_csv_lst())



class load_chart_csvs(object):

	# source_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/sources"
	source_path = "/Volumes/StreamS06_2TB/project_a/sources"
	# source_path = "/Users/masamitsuochiai/Documents/wk/analyze_sources/test"

	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			self.crud = CRUD_for_STOCK_CHARTS(host, database, user)
			self.csv_lst = my_util.get_csvs(self.source_path)

		except Exception as e:
			print(str(e))


	def load_csv_lst(self):
		err_lst = []
		str_to_date = lambda x: datetime.date(datetime.datetime.strptime(x, '%Y-%m-%d').year,
												datetime.datetime.strptime(x, '%Y-%m-%d').month,
												datetime.datetime.strptime(x, '%Y-%m-%d').day)
		for csv in self.csv_lst:
			try:
				stock_id = int(csv[-13:-9]) # Stock ID
				df = pd.read_csv(csv, encoding='cp932', header=1)
				df["ID"] =  [stock_id for i in range(df.shape[0])]
				df = df.ix[:, ['日付', 'ID', '始値', '高値', '安値', '終値', '出来高', '終値調整値']]
				df['日付'].map(str_to_date)
				r = df.values.tolist()
				self.crud.update_tbl_from_lst(r)
			except Exception as e:
				err_lst.append([csv, e])

			print(csv)

		return err_lst

if __name__ == '__main__': 
	main()
