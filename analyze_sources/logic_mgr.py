import pandas as pd
from prediction_mgr import prediction_mgr_for_ii, prediction_mgr_for_hs, prediction_mgr_for_ii_arr
from keras.models import load_model
from download_rakuten_selenium import download_rakuten_selenium
import datetime

from crud_for_stock_detail import CRUD_for_STOCK_DETAIL



class logic_mgr_simulator(object):


	def set_model(self):
		self.models = []
		# # 東証一部
		# self.models.append(load_model("./tmp_30/models/full/model.ep50.h5"))
		# self.models.append(load_model("./tmp_30/models/Tosho1bu/model.ep50.h5"))
		# self.models.append(load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5"))
		# 東証二部
		self.models.append(load_model("./tmp_30/models/full/model.ep50.h5"))
		self.models.append(load_model("./tmp_30/models/Tosho2bu/model.ep50.h5"))
		# self.models.append(load_model("./tmp_30/models/Electronics/model.ep50.h5"))



	def __init__(self):
		self.set_model()
		# self.drs = download_rakuten_selenium()
		self.crud = CRUD_for_STOCK_DETAIL()
		# self.available_price = available_price # Price which can be invested
		# self.date_to_be_pred = date_to_be_pred # Date to be predicted


	def retrieve_ought_to_buy_items(self, ii_obj, available_price, d_range, print_detail=False):

		suggest_id_lst = []
		p_mgr_ii = prediction_mgr_for_ii_arr(ii_obj, self.models)
		predicted_df = p_mgr_ii.get_predict_price_by_models(d_range)
		del ii_obj
		del p_mgr_ii

		predicted_df["weight"] = 1 - predicted_df["atr_40"] / predicted_df["low_price"]
		predicted_df["required_budget"] = predicted_df["high_price"] / predicted_df["weight"]
		id_lst_str = str(predicted_df["stock_id"].drop_duplicates().values).replace("[","('").replace("]", "')").replace(" ", "','")
		stock_details = self.crud.read_tbl_by_df("WHERE stock_id in %s"%id_lst_str).loc[:, ["stock_id", "stock_unit"]]
		stock_details["stock_id"] = stock_details["stock_id"].astype(int)
		predicted_df = pd.merge(predicted_df, stock_details, on="stock_id")
		predicted_df["required_budget"] = predicted_df["required_budget"] * predicted_df["stock_unit"]
		
		# Insert [min_predict_prices]
		min_predict_prices = predicted_df.loc[:, ["stock_id", "date", "predict_close_price"]].groupby(["stock_id", "date"], as_index=False).min().sort_values(by=["date", "stock_id"], ascending=True)
		min_predict_prices = min_predict_prices.rename(columns={"predict_close_price":"min_predict_close_price"})
		predicted_df       = pd.merge(predicted_df, min_predict_prices, on=["stock_id", "date"])
		# Insert [min_pre_predict_prices]
		min_pre_predict_prices = predicted_df.loc[:, ["stock_id", "date", "pre_predict_close_price"]].groupby(["stock_id", "date"], as_index=False).min().sort_values(by=["date", "stock_id"], ascending=True)
		min_pre_predict_prices = min_pre_predict_prices.rename(columns={"pre_predict_close_price":"min_pre_predict_close_price"})
		predicted_df           = pd.merge(predicted_df, min_pre_predict_prices, on=["stock_id", "date"])
		# Insert [move_avrg_40_prev]
		prev_lst = predicted_df.loc[:, ["stock_id", "date", "move_avrg_40"]]
		for n in range(10):
			tmp_df = prev_lst.copy()
			tmp_df["date"] = tmp_df["date"] + datetime.timedelta(days=40+n)
			tmp_df = tmp_df.loc[:, ["stock_id", "date", "move_avrg_40"]]
			tmp_df = tmp_df.rename(columns={'move_avrg_40': 'move_avrg_40_prev_'+str(40+n)})
			prev_lst = pd.merge(prev_lst, tmp_df, on=["stock_id", "date"], how="left")
		# #For test ------------------------
		# predicted_df_raw1 = prev_lst.copy()
		# #For test ------------------------
		prev_lst["move_avrg_40_prev"] = prev_lst.loc[:, ["move_avrg_40_prev_40"]]
		for n in range(1,10):
			prev_lst.loc[prev_lst["move_avrg_40_prev"].isnull(), ["move_avrg_40_prev"]] = prev_lst.loc[prev_lst["move_avrg_40_prev"].isnull(), ["move_avrg_40_prev_"+str(40+n)]].values
		prev_lst = prev_lst.loc[:, ["stock_id", "date", "move_avrg_40_prev"]]
		predicted_df = pd.merge(predicted_df, prev_lst, on=["stock_id", "date"])
		# #For test ------------------------
		# predicted_df_raw2 = predicted_df.copy()
		# #For test ------------------------
		predicted_df = predicted_df.dropna(how='any')

		##############
		# 条件の設定  #
		##############
		conditions = []
		buy_point = 0
		# 見込コストが費用の最大の予測値より小さい
		predicted_df["condition1"]   = predicted_df["required_budget"] < available_price
		predicted_df["condition1_p"] = buy_point -1 * (predicted_df["required_budget"] - available_price) / available_price
		# 翌々日の終値の最小の予測値が翌日の終値の最小の予測値より大きい
		predicted_df["condition2"]   = predicted_df["min_predict_close_price"] > predicted_df["min_pre_predict_close_price"]
		predicted_df["condition2_p"] = buy_point +1 * (predicted_df["min_predict_close_price"] - predicted_df["min_pre_predict_close_price"]) / predicted_df["min_pre_predict_close_price"]
		# 翌日の終値の最小の予測値が最後の終値の実測値より大きい
		predicted_df["condition3"]   = predicted_df["min_predict_close_price"] > predicted_df["close_price"]
		predicted_df["condition3_p"] = buy_point +1 * (predicted_df["min_predict_close_price"] - predicted_df["close_price"]) / predicted_df["min_predict_close_price"]
		# 最後の40日移動平均が40日前の40日移動平均より大きい
		predicted_df["condition4"]   = predicted_df["move_avrg_40"] > predicted_df["move_avrg_40_prev"]
		predicted_df["condition4_p"] = buy_point +1 * (predicted_df["move_avrg_40"] - predicted_df["move_avrg_40_prev"]) / predicted_df["move_avrg_40"]
		### 条件の集計 ###
		predicted_df["condition"]    = predicted_df["condition1"]   & predicted_df["condition2"]   & predicted_df["condition3"]   & predicted_df["condition4"]
		predicted_df["condition_p"]  = predicted_df["condition1_p"] + predicted_df["condition2_p"] + predicted_df["condition3_p"] + predicted_df["condition4_p"]
		##############

		col_lst = ["stock_id", "date", "open_price", "high_price", "low_price", "close_price", "output"]
		for i in range(1,5):
			col_lst.append("condition" + str(i))
			col_lst.append("condition" + str(i) + "_p")
		col_lst.append("condition")
		col_lst.append("condition_p")
		predicted_df = predicted_df.loc[:, col_lst]

		# return predicted_df, predicted_df_raw1, predicted_df_raw2
		return predicted_df






class logic_mgr(object):

	def set_model(self):
		self.models = []
		# 東証一部
		# self.models.append(load_model("./tmp_30/models/full/model.ep50.h5"))
		# self.models.append(load_model("./tmp_30/models/Tosho1bu/model.ep50.h5"))
		# self.models.append(load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5"))
		# 東証二部
		self.models.append(load_model("./tmp_30/models/full/model.ep50.h5"))
		self.models.append(load_model("./tmp_30/models/Tosho2bu/model.ep50.h5"))
		# self.models.append(load_model("./tmp_30/models/Electronics/model.ep50.h5"))



	def __init__(self):
		self.set_model()
		self.drs = download_rakuten_selenium()
		self.crud = CRUD_for_STOCK_DETAIL()
		# self.available_price = available_price # Price which can be invested
		# self.date_to_be_pred = date_to_be_pred # Date to be predicted

	def apply_buy_rule(self, ii_obj, available_price, print_detail=False):

		suggest_id_lst = []
		p_mgr_ii = prediction_mgr_for_ii(ii_obj, self.models)

		whole_pred_df = p_mgr_ii.get_predict_price_by_models()
		whole_pred_price_with_pre_pred = p_mgr_ii.get_predict_price_with_pre_pred()
		candidate_deal_lst = pd.DataFrame()
		for cur_id in p_mgr_ii.ii_obj.id_lst:
			try:
				tmp_pred_df = whole_pred_df.loc[whole_pred_df["stock_id"]==int(cur_id), :]
				tmp_ii_df = p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1]
				volatility = tmp_ii_df["atr_40"]
				low_price  = tmp_ii_df["low_price"]
				weight = 1 - volatility / low_price
				pred_max_high_price = tmp_pred_df["high_price"].max()
				required_budget = pred_max_high_price / weight
				unit_price = self.crud.read_tbl_by_df("WHERE stock_id='%s'"%str(cur_id))["stock_unit"].values[0]
				required_budget = required_budget * int(unit_price)
				pred_price_with_pre_pred = whole_pred_price_with_pre_pred.loc[whole_pred_price_with_pre_pred["stock_id"]==int(cur_id), :]


				##############
				# 条件の定義  #
				##############
				conditions = []
				buy_point = 0
				# 見込コストが費用の最大の予測値より小さい
				conditions.append(required_budget < available_price)
				buy_point = buy_point -1 * (required_budget - available_price) / available_price
				# 翌々日の終値の最小の予測値が翌日の終値の最小の予測値より大きい
				conditions.append(pred_price_with_pre_pred["close_price"].min() > tmp_pred_df["close_price"].min())
				buy_point = buy_point +1 * (pred_price_with_pre_pred["close_price"].min() - tmp_pred_df["close_price"].min()) / pred_price_with_pre_pred["close_price"].min()
				# 翌日の終値の最小の予測値が最後の終値の実測値より大きい
				conditions.append(tmp_pred_df["close_price"].min() > tmp_ii_df["close_price"])
				buy_point = buy_point +1 * (tmp_pred_df["close_price"].min() - tmp_ii_df["close_price"]) / tmp_pred_df["close_price"].min()
				# 最後の40日移動平均が40日前の40日移動平均より大きい
				conditions.append(tmp_ii_df["move_avrg_40"] > p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1-40]["move_avrg_40"])
				buy_point = buy_point +1 * (tmp_ii_df["move_avrg_40"] - p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1-40]["move_avrg_40"]) / tmp_ii_df["move_avrg_40"]
				##############

				if False not in conditions:
					print("********** %s is labeled to buy!!!"%cur_id)
					cur_item = {"stock_id": cur_id, "buy_point": buy_point}
					suggest_id_lst.append(cur_item)

				if print_detail:
					print("##############")
					print("# 条件の定義  #")
					print("##############")
					print("# 1. 見込コストが費用の最大の予測値より小さい")
					print("# 2. 翌々日の終値の最小の予測値が翌日の終値の最小の予測値より大きい")
					print("# 3. 翌日の終値の最小の予測値が最後の終値の実測値より大きい")
					print("# 4. 最後の40日移動平均が40日前の40日移動平均より大きい")
					print("##############")

					print(conditions)
					print("*** %s >>> required_budget: %f"%(cur_id, required_budget))
					print("*** Latest price")
					print(tmp_ii_df)
					print("*** Prediction price")
					print(tmp_pred_df)
					print("*** Next Prediction price")
					print(pred_price_with_pre_pred)
					print("*** 40days back price")
					print(p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1-40])

			except Exception as e:
				print("***Error: %s"%str(cur_id))
				# print(whole_pred_df)
				# import traceback
				# traceback.print_exc()
				pass
				
		p_mgr_ii.plot_charts()

		return suggest_id_lst

	def apply_sell_rule(self, held_stock_lst, available_price, target_date, update_fl=False):

		suggest_id_lst = []
		if len(held_stock_lst) == 0:
			return suggest_id_lst

		sid_lst = [hs.stock_id for hs in  held_stock_lst]
		p_mgr_hs = prediction_mgr_for_hs(held_stock_lst, target_date, self.models)
		# print("*** prediction_mgr_for_hs")
		whole_pred_df = p_mgr_hs.get_predict_price_by_models()
		# print("*** get_predict_price_by_models")
		whole_pred_price_with_pre_pred = p_mgr_hs.get_predict_price_with_pre_pred()
		# print("*** get_predict_price_with_pre_pred")
		# cur_price_df = self.drs.get_cur_price(sid_lst)
		# print("*** get_cur_price")

		whole_required_budget_lst = []
		current_price_lst = []
		sell_point_lst = []

		for cur_hid in range(len(held_stock_lst)):
			cur_hs = held_stock_lst[cur_hid]
			if update_fl:
				cur_hs.update_ii_obj()

			cur_id = cur_hs.stock_id
			tmp_pred_df = whole_pred_df.loc[whole_pred_df["stock_id"]==int(cur_id), :]
			tmp_ii_df = cur_hs.ii_obj.df
			latest_item = tmp_ii_df.iloc[-1]
			print("####### Latest info of hs #######")
			print(latest_item)
			volatility = latest_item["atr_40"]
			low_price  = latest_item["low_price"]
			weight = 1 - volatility / low_price
			pred_min_high_price = tmp_pred_df["high_price"].min()
			required_budget = pred_min_high_price / weight
			required_budget = required_budget * int(cur_hs.b_amount)
			current_actual_price   = latest_item["close_price"] * int(cur_hs.b_amount)
			print("*** %s >>> required_budget: %f"%(cur_id, float(required_budget)))
			pred_price_with_pre_pred = whole_pred_price_with_pre_pred.loc[whole_pred_price_with_pre_pred["stock_id"]==int(cur_id), :]

			##############
			# 条件の定義  #
			##############
			conditions = []
			sell_point = 0
			# 翌々日の終値の最小の予測値が翌日の終値の最小の予測値より小さい
			conditions.append(pred_price_with_pre_pred["close_price"].min() < tmp_pred_df["close_price"].min())
			sell_point = sell_point-1 * (pred_price_with_pre_pred["close_price"].max() - tmp_pred_df["close_price"].min())
			# 翌日の終値の最大の予測値が最後の終値の実測値より小さい
			conditions.append(tmp_pred_df["close_price"].max() < latest_item["close_price"])
			sell_point = sell_point-1 * (tmp_pred_df["close_price"].max() - latest_item["close_price"])
			# 最後の40日移動平均が40日前の40日移動平均より小さい
			conditions.append(latest_item["move_avrg_40"] < tmp_ii_df.iloc[-1-40]["move_avrg_40"])
			sell_point = sell_point-1 * (latest_item["move_avrg_40"] - tmp_ii_df.iloc[-1-40]["move_avrg_40"])
			##############
			print(conditions)
			if False not in conditions:
				print("********** %s is labeled to sell!!!"%str(cur_hs.stock_id))
				suggest_id_lst.append(cur_hs.stock_id)

			else:
				whole_required_budget_lst.append(required_budget)
				current_price_lst.append(current_actual_price)
				sell_point_lst.append(sell_point)

		# 見込コストが予算の残高を超える
		if sum(whole_required_budget_lst) < (sum(current_price_lst) + available_price):

			should_be_sold = held_stock_lst[sell_point_lst.index(max(sell_point_lst))]
			print("********** %s is labeled to sell!!!"%str(should_be_sold.stock_id))
			suggest_id_lst.append(should_be_sold.stock_id)

		return suggest_id_lst




	def apply_hold_rule_while_market_open(self, held_stock_lst, target_date):

		sid_lst = [hs.stock_id for hs in  held_stock_lst]
		p_mgr_hs = prediction_mgr_for_hs(held_stock_lst, target_date, self.models)
		print("*** prediction_mgr_for_hs")

		whole_pred_df = p_mgr_hs.get_predict_price_by_models()
		print("*** get_predict_price_by_models")
		whole_pred_price_with_pre_pred = p_mgr_hs.get_predict_price_with_pre_pred()
		print("*** get_predict_price_with_pre_pred")
		cur_price_df = self.drs.get_cur_price(sid_lst)
		print("*** get_cur_price")

		for cur_id in sid_lst:
			tmp_cur_price = cur_price_df.loc[cur_price_df["stock_id"]==cur_id, :]["price"]

			tmp_pred_df = whole_pred_df.loc[whole_pred_df["stock_id"]==cur_id, :]
			min_low_price = tmp_pred_df["low_price"].min()
			##############
			# 条件の定義  #
			##############
			conditions = []	
			# 現在の実測値が昨日からの最安値の最小の予測値より小さい
			conditions.append(int(tmp_cur_price) < int(min_low_price))
			##############
			print("cur: %d / pred: %d"%(int(tmp_cur_price), int(min_low_price)))

			if condition1:
				print("********** %s is labeled to sell!!!"%cur_id)











