import psycopg2
import datetime
import pandas as pd
from datetime import datetime, timedelta


def main():
	crud = CRUD_for_INVESTING_INFO()
	# crud.create_tbl()
	# test_record = {
	# 	"date":  datetime.date(1984,1,4),
	# 	"stock_id":  3000, 
	# 	"start_price":  148, 
	# 	"high_price": 150,
	# 	"low_price":  147,
	# 	"end_price": 150,
	# 	"output":  169000,
	# 	"adjusted_val": 1500,
	# 	}

	# # crud.update_tbl([test_record])
	print(crud.read_tbl())
	crud.close_connection()


###################
#  COMPANY_INFO   #
###################
class CRUD_for_INVESTING_INFO(object):
	col_lst = [
		{"name": "date", "type": "date"}, 
		{"name": "investing_id", "type": "varchar(255)"}, 
		{"name": "end_price", "type": "double precision"}, 
		{"name": "start_price", "type": "double precision"}, 
		{"name": "high_price", "type": "double precision"}, 
		{"name": "low_price", "type": "double precision"}, 
		{"name": "output", "type": "double precision"}, 
		{"name": "prev_ratio", "type": "double precision"},
		{"name": "move_avrg_5", "type": "double precision"}, 
		{"name": "move_avrg_10", "type": "double precision"}, 
		{"name": "move_avrg_20", "type": "double precision"}, 
		{"name": "move_avrg_40", "type": "double precision"}, 
		{"name": "move_avrg_80", "type": "double precision"}, 
		{"name": "atr_5", "type": "double precision"}, 
		{"name": "atr_10", "type": "double precision"}, 
		{"name": "atr_20", "type": "double precision"}, 
		{"name": "atr_40", "type": "double precision"}, 
		{"name": "atr_80", "type": "double precision"}, 
		{"name": "rsi", "type": "double precision"},
	]

	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			print(str(e))

	def create_tbl(self):
		cur = self.connection.cursor()
		sql = "CREATE TABLE investing_info (";
		for col in self.col_lst:
			sql = sql + col["name"] + " " + col["type"] + ", "
		sql = sql + "PRIMARY KEY (date, stock_id))"
		print(sql)
		cur.execute(sql)
		self.connection.commit()
		cur.close()

	def read_tbl(self, sql="", table_name_fl=True):
		return_list = []
		cur = self.connection.cursor()
		if table_name_fl:
			sql = "SELECT * FROM investing_info" + " " + str(sql) + ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list

	def read_tbl_by_df(self, sql="", table_name_fl=True):
		if table_name_fl:
			sql = "SELECT * FROM investing_info" + " " + str(sql) + ";"
		try:
			return_list = pd.read_sql(sql=sql, con=self.connection)

		except Exception as e:
			print(e)

		return return_list


	def upsert_tbl_from_df(self, df):

		df.to_sql(df,"investing_info", self.connection, if_exist="replace", index=False)


		# j_records = []
		# for index, row in df.iterrows():
		# 	r_j = row
		# 	r_mod = {
		# 		"date": r_j["date"],
		# 		"stock_id": r_j["investing_id"],
		# 		"end_price": float(str(r_j["end_price"]).replace(",", "")),
		# 		"start_price": float(str(r_j["start_price"]).replace(",", "")),
		# 		"high_price": float(str(r_j["high_price"]).replace(",", "")),
		# 		"low_price": float(str(r_j["low_price"]).replace(",", "")),
		# 		"output": float(r_j["output"]),
		# 		# "prev_ratio": 0,
		# 		"prev_ratio": float(r_j["prev_ratio"]),
		# 		"move_avrg_5": float(r_j["move_avrg_5"]),
		# 		"move_avrg_10": float(r_j["move_avrg_10"]),
		# 		"move_avrg_20": float(r_j["move_avrg_20"]),
		# 		"move_avrg_40": float(r_j["move_avrg_40"]),
		# 		"move_avrg_80": float(r_j["move_avrg_80"]),
		# 		"atr_5": float(r_j["atr_5"]),
		# 		"atr_10": float(r_j["atr_10"]),
		# 		"atr_20": float(r_j["atr_20"]),
		# 		"atr_40": float(r_j["atr_40"]),
		# 		"atr_80": float(r_j["atr_80"]),
		# 		"rsi": float(r_j["rsi"]),
		# 	}
		# 	j_records.append(r_mod)
		# self.update_tbl_from_json(j_records)

	def update_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				# Chk code ---------
				chk_sql = "SELECT distinct investing_id from investing_info where stock_id like '" + str(r["stock_id"] + "%';")
				id_lst = pd.read_sql(sql=chk_sql, con=self.connection)
				print(id_lst)
				if len(id_lst) != 1:
					print(str(r["stock_id"]) + " is not appropriate id ############")
					continue
				# Chk code ---------
				insert_r   = []
				insert_sql = "UPDATE investing_info SET "
				for tmp_key in r.keys():
					if str(tmp_key) == "stock_id":
						continue
					insert_r.append(str(r[tmp_key]))
					insert_sql += str(tmp_key) + "'%s',"

				insert_sql = insert_sql[:-2] + " WHERE STOCK_ID like '" + r["stock_id"] + "%'"
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
				insert_sql = "INSERT INTO investing_info VALUES ("
				for col in self.col_lst:
					insert_r.append(str(r[col["name"]]))
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT investing_info_pkey " + 
					"DO UPDATE SET start_price=excluded.start_price " + 
					", high_price=excluded.high_price " + 
					", low_price=excluded.low_price " + 
					", end_price=excluded.end_price " + 
					", output=excluded.output " + 
					", prev_ratio=excluded.prev_ratio " + 
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

	def close_connection(self):
		self.connection.close()

	
if __name__ == '__main__': 
	main()
	
	