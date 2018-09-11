from trade_mgr import *
import datetime
import logic_mgr
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL
from trade_func import trade_func
from training_chart_data import *

from logic_mgr import logic_mgr_simulator
import investing_info as ii

if __name__ == '__main__':

	print("### start simulation ...")
	crud = CRUD_for_STOCK_DETAIL()


	budget = 1000000
	lmgr = logic_mgr.logic_mgr_simulator()
	ii_obj = ii.get_ii_obj_by_stock_market("東証一部", datetime.date(2017,1,1), datetime.date(2017,12,31))
	applied_buy_rule_df = lmgr.retrieve_ought_to_buy_items(ii_obj, budget*0.7, 300)
	save_as_pickled_object(applied_buy_rule_df, "./Tosho1bu_buy_lst_20170101-20171231.pkl")
	# applied_buy_rule_df = try_to_load_as_pickled_object_or_None("./Tosho1bu_buy_lst_20180101-20180810.pkl")

	hs_lst = []
	tf = trade_func(budget, hs_lst)
	tmgr = trade_mgr(budget, [], lmgr)
	applied_buy_rule_df = applied_buy_rule_df.sort_values(by=["date"], ascending=True)
	date_lst = applied_buy_rule_df["date"].drop_duplicates().values
	ii_obj = applied_buy_rule_df.loc[:, ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]].drop_duplicates()

	print("########################################")
	print("#########  Start simulation... #########")
	print("########################################")
	for tmp_date_id in range(len(date_lst)):
		tmp_date = date_lst[tmp_date_id]
		print("#########################################")
		print("### Current date   : %s"%str(tmp_date))
		print("#########################################")
		for hs in tmgr.hs_lst:
			hs.update_ii_obj(tmp_date, False)

		print_detail = False
		tmp_ii_obj = ii_obj.loc[ii_obj["date"]==tmp_date, :]
		b_suggest_lst = applied_buy_rule_df.loc[(applied_buy_rule_df["date"]==tmp_date)&(applied_buy_rule_df["condition"]==True), :].sort_values(by=["condition_p"], ascending=False)
		s_suggest_lst = lmgr.apply_sell_rule(hs_lst, tf.budget, tmp_date, applied_buy_rule_df, update_fl=False)

		for bitem_id in range(len(b_suggest_lst)):
			bitem = b_suggest_lst.iloc[bitem_id]
			bid     = bitem["stock_id"]
			b_point = bitem["condition_p"]
			if (str(bid) in tmgr.hs_lst) or (int(bid) in tmgr.hs_lst):
				print("break...")
				break
			tmp_unit = crud.read_tbl_by_df("WHERE stock_id='%s'"%str(bid))["stock_unit"].values[0]
			tmp_price = tmp_ii_obj.loc[tmp_ii_obj["stock_id"]==int(bid), ["close_price"]].iloc[-1].values[0]
			tmp_budget, tmp_hs_lst = tf.buy(bid, tmp_unit, tmp_price, tmp_date)
			tmgr.set_budget(tmp_budget)
			tmgr.set_held_stock(tmp_hs_lst)

		for sid in s_suggest_lst:
			tmp_price = []
			i=0
			while len(tmp_price) < 1:
				i=i+1
				tmp_price = ii_obj.loc[(ii_obj["date"]==date_lst[tmp_date_id-i])&(ii_obj["stock_id"]==int(sid)), ["close_price"]]
			tmp_price = tmp_price.iloc[len(tmp_price)-1].values[0]
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
			print("##### current price : %s"%str(ii_obj.loc[(ii_obj["date"]==tmp_date)&(ii_obj["stock_id"]==hs.stock_id), ["close_price"]]["close_price"].values))
			print("##### ---------------------------------")
			# hs.update_ii_obj(tmp_date)
		print("### -----------------------------------")



