import psycopg2
import datetime
import pandas as pd

class CRUD_for_STOCK_DETAIL(object):
	col_lst = [ 
			"stock_id", 
			"stock_name", 
			"stock_market", 
			"business_type",
			"stock_unit",
			"update_date",
			]


	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			import traceback
			traceback.print_exc()

	def read_tbl_by_df(self, sql=""):
		sql = "SELECT * FROM STOCK_DETAIL" + " " + str(sql) + ";"
		try:
			return_list = pd.read_sql(sql=sql, con=self.connection)
			return return_list

		except Exception as e:
			import traceback
			traceback.print_exc()


	def get_business_type_lst(self):
		sql = "SELECT distinct business_type FROM STOCK_DETAIL;"
		try:
			print(sql)
			return_list = pd.read_sql(sql=sql, con=self.connection)
			return return_list.values

		except Exception as e:
			import traceback
			traceback.print_exc()

	def get_stock_market_lst(self):
		sql = "SELECT distinct stock_market FROM STOCK_DETAIL;"
		try:
			print(sql)
			return_list = pd.read_sql(sql=sql, con=self.connection)
			return return_list.values

		except Exception as e:
			import traceback
			traceback.print_exc()



	def upsert_tbl_from_lst(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO STOCK_DETAIL VALUES ("
				for col_num in range(len(self.col_lst)):
					insert_r.append(r[col_num])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT stock_detail_stock_id_key " + 
					"DO UPDATE SET stock_id=excluded.stock_id ")
				for col_num in range(1, len(self.col_lst)):
					insert_sql += ", " + self.col_lst[col_num] + "=excluded." + self.col_lst[col_num] + " " 
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()

	def upsert_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO STOCK_DETAIL VALUES ("
				for col in self.col_lst:
					insert_r.append(r[col])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT stock_detail_stock_id_key " + 
					"DO UPDATE SET stock_id=excluded.stock_id ")
				for col in self.col_lst[1:len(self.col_lst)]:
					insert_sql += ", " + col + "=excluded." + col + " " 
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()


	def close_connection(self):
		self.connection.close()