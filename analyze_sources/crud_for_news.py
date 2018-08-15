import psycopg2
import datetime


def main():
	crud = CRUD_for_REUTERS()
	crud.create_tbl()
	test_record = {
		"date":  datetime.date(1984,1,4),
		"number":  1, 
		"title": "テストタイトル",
		"contents":  "これはテスト用のニュース記事です。",
		"url":  "",
		}
	# crud.update_tbl_from_json([test_record])
	# print(crud.read_tbl())
	# crud.close_connection()


###################
#  KLUG FX NEWS   #
###################
class CRUD_for_KLUG_FX(object):
	col_lst = [
		{"name": "date",    "type": "date"},
		{"name": "uploaded_date",  "type": "varchar(255)"},
		{"name": "title",   "type": "varchar(200)"},
		{"name": "contents","type": "varchar(10000)"},
		{"name": "url",     "type": "varchar(255)"},
	]

	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			print(str(e))

	def create_tbl(self):
		cur = self.connection.cursor()
		sql = "CREATE TABLE klug_fx_news (";
		for col in self.col_lst:
			sql = sql + col["name"] + " " + col["type"] + ", "
		sql = sql + "PRIMARY KEY (date, uploaded_date))"
		print(sql)
		cur.execute(sql)
		self.connection.commit()
		cur.close()

	def read_tbl(self, sql="", table_name_fl=True):
		return_list = []
		cur = self.connection.cursor()
		if table_name_fl:
			sql = "SELECT * FROM KLUG_FX_NEWS" + " " + str(sql) + ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list

	def update_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO KLUG_FX_NEWS VALUES ("
				for col in self.col_lst:
					insert_r.append(r[col["name"]])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT klug_fx_news_pkey " + 
					"DO UPDATE SET date=excluded.date " + 
					", uploaded_date=excluded.uploaded_date " + 
					", title=excluded.title " + 
					", contents=excluded.contents " + 
					", url=excluded.url ")
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()



###################
#  REUTERS NEWS   #
###################
class CRUD_for_REUTERS(object):
	col_lst = [
		{"name": "date",    "type": "date"},
		{"name": "uploaded_date",  "type": "varchar(255)"},
		{"name": "title",   "type": "varchar(200)"},
		{"name": "contents","type": "varchar(10000)"},
		{"name": "url",     "type": "varchar(255)"},
	]

	def __init__(self, host="localhost", database="project_a", user="masamitsuochiai"):
		try:
			dburl = "dbname=%s host=%s user=%s" % (database, host, user)
			self.connection = psycopg2.connect(dburl)
		except Exception as e:
			print(str(e))

	def create_tbl(self):
		cur = self.connection.cursor()
		sql = "CREATE TABLE reuters_news (";
		for col in self.col_lst:
			sql = sql + col["name"] + " " + col["type"] + ", "
		sql = sql + "PRIMARY KEY (date, uploaded_date))"
		print(sql)
		cur.execute(sql)
		self.connection.commit()
		cur.close()

	def read_tbl(self, sql="", table_name_fl=True):
		return_list = []
		cur = self.connection.cursor()
		if table_name_fl:
			sql = "SELECT * FROM REUTERS_NEWS" + " " + str(sql) + ";"
		try:
			cur.execute(sql)
			return_list = cur.fetchall()
			cur.close()
		except Exception as e:
			print(e)

		return return_list

	def update_tbl_from_json(self, records):
		error_list = []
		cur = self.connection.cursor()
		for r in records:
			try:
				insert_r   = []
				insert_sql = "INSERT INTO REUTERS_NEWS VALUES ("
				for col in self.col_lst:
					insert_r.append(r[col["name"]])
					insert_sql = insert_sql + "%s, "
				insert_sql = (insert_sql[:-2] + 
					") ON CONFLICT ON CONSTRAINT reuters_news_pkey " + 
					"DO UPDATE SET date=excluded.date " + 
					", uploaded_date=excluded.uploaded_date " + 
					", title=excluded.title " + 
					", contents=excluded.contents " + 
					", url=excluded.url ")
				cur.execute(insert_sql, insert_r)

			except Exception as e:
				print([r, e])
		self.connection.commit()
		cur.close()

if __name__ == '__main__': 
	main()