from trade_mgr import *
import datetime
import logic_mgr
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL
from trade_func import trade_func


if __name__ == '__main__':

	date_lst = []
	with open(os.path.join('./', 'date_lst'), 'r') as f:
		for line in f:
			date_lst.append(datetime.datetime.strptime(line.replace('\n','').replace('"',''), "%Y-%m-%d"))

	print("### start simulation ...")
	# print("### get held_stock ...")
	# # hs = held_stock(6502, datetime.date(2017,12,1), 309, 1000, 1000)
	print("### get logic_mgr ...")
	lmgr = logic_mgr.logic_mgr()
	update_fl = False


	# ii_obj = ii.get_ii_obj_by_stock_market("東証一部", datetime.datetime.today()-datetime.timedelta(days=10), datetime.datetime.today(), True)
	
	crud = CRUD_for_STOCK_DETAIL()

	# id_lst = [6502]
	# id_lst = [2163]
	# id_lst = ['1553', '1936', '5461', '6623', '7485', '9402']
	# id_lst = [1553, 1936, 5461, 6623, 7485, 9402]
	# id_lst = [1358, 4188, 4319, 2163, 4307, 4337, 5975, 5975, 6758, 6702, 6724, 7012]

	# tmgr = trade_mgr(1000000, [hs], lmgr)
	tmgr = trade_mgr(1000000, [], lmgr)
	tf = trade_func(tmgr.budget, tmgr.hs_lst)

	print("########################################")
	print("#########  Start simulation... #########")
	print("########################################")
	for tmp_date in date_lst:
		print("#########################################")
		print("### Current date   : %s"%str(tmp_date))
		print("#########################################")
		# ii_obj = ii.investing_info(id_lst, tmp_date-datetime.timedelta(days=365), tmp_date, update_fl)
		ii_obj = ii.get_ii_obj_by_stock_market("東証一部", tmp_date-datetime.timedelta(days=365), tmp_date, update_fl)
		tmgr.set_ii_obj(ii_obj)

		print_detail = False

		b_suggest_lst, s_suggest_lst = tmgr.run_daily_check(print_detail)

		b_suggest_lst = sorted(b_suggest_lst, key=lambda x:x['buy_point'], reverse=True) # Sorted by buy_point
		for bitem in b_suggest_lst:
			bid     = bitem["stock_id"]
			b_point = bitem["buy_point"]
			if (str(bid) in tmgr.hs_lst) or (int(bid) in tmgr.hs_lst):
				print("break...")
				break
			tmp_unit = crud.read_tbl_by_df("WHERE stock_id='%s'"%str(bid))["stock_unit"].values[0]
			tmp_price = ii_obj.df.loc[ii_obj.df["stock_id"]==int(bid), ["close_price"]].iloc[-1].values[0]
			tmp_budget, tmp_hs_lst = tf.buy(bid, tmp_unit, tmp_price, tmp_date)
			tmgr.set_budget(tmp_budget)
			tmgr.set_held_stock(tmp_hs_lst)

		for sid in s_suggest_lst:
			tmp_price = ii_obj.df.loc[ii_obj.df["stock_id"]==int(bid), ["close_price"]].iloc[-1].values[0]
			tmp_budget, tmp_hs_lst = tf.sell(sid, tmp_price)
			tmgr.set_budget(tmp_budget)
			tmgr.set_held_stock(tmp_hs_lst)

		print("### -----------------------------------")
		print("### Current budget     : %d"%tmgr.budget)
		print("### Current budget     : %d"%tf.budget)
		print("### Current held_stocks: ")
		for hs in tmgr.hs_lst:
			print("##### hs stock_id: %s"%str(hs.stock_id))
			print("##### hs b_date  : %s"%str(hs.b_date))
			print("##### hs b_price : %s"%str(hs.b_price))
			print("##### hs b_amount: %s"%str(hs.b_amount))
			print("##### ---------------------------------")
			hs.update_ii_obj(tmp_date)
		print("### -----------------------------------")



