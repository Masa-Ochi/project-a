import psycopg2
import datetime
import pandas as pd

def main():
	crud = CRUD_for_STOCK_CHARTS()
	# create_table(self)
	test_record = {
		"date":  datetime.date(1984,1,4),
		"stock_id":  3000, 
		"start_price":  148, 
		"high_price": 150,
		"low_price":  147,
		"end_price": 150,
		"output":  169000,
		"adjusted_val": 1500,
		}

	# crud.update_tbl([test_record])
	print(crud.read_tbl())
	crud.close_connection()


###################
#  COMPANY_INFO   #
###################
class CRUD_for_COMPANY_INFO(object):
	col_lst = [
		"stock_id",
		"market",
		"head_q",
		"stlmnt_month",
		"name",
		"category"
	]

	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			print(str(e))

	def create_tbl(self):
		cur = self.connection.cursor()
		#証券コード　取引所　所在地　決算期　会社名称　業種分類
		cur.execute("CREATE TABLE company_info (" + 
						"stock_id integer, "
						"market varchar(20), " +
						"head_q varchar(20), " +
						"stlmnt_month varchar(20), " +
						"name varchar(20), " +
						"category varchar(20), " +
						"PRIMARY KEY (stock_id))")
		self.connection.commit()
		cur.close()

	def read_tbl(self, sql="", table_name_fl=True):
		return_list = []
		cur = self.connection.cursor()
		if table_name_fl:
			sql = "SELECT * FROM COMPANY_INFO" + " " + str(sql) + ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list


	# def read_tbl_by_df(self, sql=""):
	# 	sql = "SELECT * FROM stock_charts" + " " + str(sql) + ";"
	# 	try:
	# 		return_list = pd.read_sql(sql=sql, con=self.connection)

	# 	except Exception as e:
	# 		print(e)

	# 	return return_list


	def update_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				# # Chk code ---------
				# chk_sql = "SELECT distinct stock_id from investing_info where stock_id like '" + str(r["stock_id"] + "%';")
				# id_lst = pd.read_sql(sql=chk_sql, con=self.connection)
				# print(id_lst)
				# if len(id_lst) != 1:
				# 	print(str(r["stock_id"]) + " is not appropriate id ############")
				# 	continue
				# # Chk code ---------
				insert_r   = []
				insert_sql = "UPDATE stock_charts SET "
				for tmp_key in r.keys():
					if str(tmp_key) == "stock_id":
						continue
					insert_r.append(str(r[tmp_key]))
					insert_sql += str(tmp_key) + "'%s',"

				insert_sql = insert_sql[:-2] + " WHERE STOCK_ID='" + r["stock_id"] + "'"
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
				insert_sql = "INSERT INTO COMPANY_INFO VALUES ("
				for col in self.col_lst:
					insert_r.append(r[col])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT company_info_pkey " + 
					"DO UPDATE SET maeket=excluded.maeket " + 
					", head_q=excluded.head_q " + 
					", stlmnt_month=excluded.stlmnt_month " + 
					", name=excluded.name " + 
					", category=excluded.category ")
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()



###################
#  STOCK_CHARTS   #
###################
class CRUD_for_STOCK_CHARTS(object):
	col_lst = [
			"date", 
			"stock_id", 
			"start_price", 
			"high_price", 
			"low_price", 
			"end_price", 
			"output", 
			"adjusted_val",
			"move_avrg_5",
			"move_avrg_10",
			"move_avrg_20",
			"move_avrg_40",
			"move_avrg_80",
			"atr_5",
			"atr_10",
			"atr_20",
			"atr_40",
			"atr_80",
			"rsi"
			]


	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			print(str(e))


	def read_tbl_by_df(self, sql=""):
		sql = "SELECT * FROM stock_charts" + " " + str(sql) + ";"
		try:
			return_list = pd.read_sql(sql=sql, con=self.connection)
			return return_list

		except Exception as e:
			print(e)


	
	def create_tbl(self):
		cur = self.connection.cursor()
		#日付   始値   高値   安値   終値       出来高  終値調整値
		cur.execute("CREATE TABLE stock_charts (" + 
						"date date, " + 
						"stock_id integer, "
						"start_price bigint, " +
						"high_price bigint, " +
						"low_price bigint, " +
						"end_price bigint, " +
						"output bigint, " +
						"adjusted_val bigint, " +
						"PRIMARY KEY (date, stock_id))")
		self.connection.commit()
		cur.close()
	
	
	def read_tbl(self, sql="", table_name_fl=True):
		return_list = []
		cur = self.connection.cursor()
		if table_name_fl:
			sql = "SELECT * FROM STOCK_CHARTS" + " " + str(sql) + ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list

	def read_tbl_by_df(self, sql="", table_name_fl=True):
		if table_name_fl:
			sql = "SELECT * FROM stock_charts" + " " + str(sql) + ";"
		try:
			return_list = pd.read_sql(sql=sql, con=self.connection)

		except Exception as e:
			print(e)

		return return_list

	def upsert_tbl_from_df(self, df):
		j_records = []
		for index, row in df.iterrows():
			r_j = row
			r_mod = {
				"date": r_j["date"],
				"stock_id": r_j["stock_id"],
				"end_price": float(str(r_j["end_price"]).replace(",", "")),
				"start_price": float(str(r_j["start_price"]).replace(",", "")),
				"high_price": float(str(r_j["high_price"]).replace(",", "")),
				"low_price": float(str(r_j["low_price"]).replace(",", "")),
				"output": float(r_j["output"]),
				# "prev_ratio": 0,
				"adjusted_val": float(r_j["adjusted_val"]),
				"move_avrg_5": float(r_j["move_avrg_5"]),
				"move_avrg_10": float(r_j["move_avrg_10"]),
				"move_avrg_20": float(r_j["move_avrg_20"]),
				"move_avrg_40": float(r_j["move_avrg_40"]),
				"move_avrg_80": float(r_j["move_avrg_80"]),
				"atr_5": float(r_j["atr_5"]),
				"atr_10": float(r_j["atr_10"]),
				"atr_20": float(r_j["atr_20"]),
				"atr_40": float(r_j["atr_40"]),
				"atr_80": float(r_j["atr_80"]),
				"rsi": float(r_j["rsi"]),
			}
			j_records.append(r_mod)
		self.update_tbl_from_json(j_records)


	def get_id_lst(self):
		return_list = []
		cur = self.connection.cursor()
		sql = "SELECT distinct stock_id FROM STOCK_CHARTS"+ ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list

	def update_tbl_from_lst(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO STOCK_CHARTS VALUES ("
				for col_num in range(len(self.col_lst)):
					insert_r.append(r[col_num])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT stock_charts_pkey " + 
					"DO UPDATE SET start_price=excluded.start_price " + 
					", high_price=excluded.high_price " + 
					", low_price=excluded.low_price " + 
					", end_price=excluded.end_price " + 
					", output=excluded.output " + 
					", adjusted_val=excluded.adjusted_val "
					", move_avrg_5=excluded.move_avrg_5 " + 
					", move_avrg_10=excluded.move_avrg_10 " + 
					", move_avrg_20=excluded.move_avrg_20 " + 
					", move_avrg_40=excluded.move_avrg_40 " + 
					", move_avrg_80=excluded.move_avrg_80 " +
					", atr_5=excluded.atr_5 " + 
					", atr_10=excluded.atr_10 " + 
					", atr_20=excluded.atr_20 " + 
					", atr_40=excluded.atr_40 " + 
					", atr_80=excluded.atr_80 " + 
					", rsi=excluded.rsi" 
					)
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()

	def update_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO STOCK_CHARTS VALUES ("
				for col in self.col_lst:
					insert_r.append(r[col])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT stock_charts_pkey " + 
					"DO UPDATE SET start_price=excluded.start_price " + 
					# ", high_price=excluded.high_price " + 
					# ", low_price=excluded.low_price " + 
					# ", end_price=excluded.end_price " + 
					# ", output=excluded.output " + 
					# ", adjusted_val=excluded.adjusted_val " + 
					", move_avrg_5=excluded.move_avrg_5 " + 
					", move_avrg_10=excluded.move_avrg_10 " + 
					", move_avrg_20=excluded.move_avrg_20 " + 
					", move_avrg_40=excluded.move_avrg_40 " + 
					", move_avrg_80=excluded.move_avrg_80 " +
					", atr_5=excluded.atr_5 " + 
					", atr_10=excluded.atr_10 " + 
					", atr_20=excluded.atr_20 " + 
					", atr_40=excluded.atr_40 " + 
					", atr_80=excluded.atr_80 " + 
					", rsi=excluded.rsi" )
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()



	def insert_tbl_by_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql_def = "INSERT INTO STOCK_CHARTS ("
				insert_sql_val = "VALUES ("
				for k in r.keys():
					insert_sql_def += str(k) + ","
					insert_r.append(r[k])
					insert_sql_val += "%s,"
				insert_sql_def = insert_sql_def[:-1] + ") "
				insert_sql_val = insert_sql_val[:-1] + ")"
				insert_sql = insert_sql_def + insert_sql_val

				# print(insert_sql)
				# print(insert_r)
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()


	def close_connection(self):
		self.connection.close()

	
if __name__ == '__main__': 
	main()
	
	