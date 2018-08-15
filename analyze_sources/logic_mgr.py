import pandas as pd
from prediction_mgr import prediction_mgr_for_ii, prediction_mgr_for_hs
from keras.models import load_model
from download_rakuten_selenium import download_rakuten_selenium


class logic_mgr(object):

	def set_model(self):
		m1=load_model("./tmp_30/models/full/model.ep50.h5")
		# m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")
		# m3=load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5")
		# self.models = [m1, m2, m3]
		self.models = [m1]

	def __init__(self):
		self.set_model()
		self.drs = download_rakuten_selenium()
		# self.available_price = available_price # Price which can be invested
		# self.date_to_be_pred = date_to_be_pred # Date to be predicted

	def apply_buy_rule(self, ii_obj, available_price):

		p_mgr_ii = prediction_mgr_for_ii(ii_obj, self.models)

		whole_pred_df = p_mgr_ii.get_predict_price_by_models()
		whole_pred_price_with_pre_pred = p_mgr_ii.get_predict_price_with_pre_pred()
		candidate_deal_lst = pd.DataFrame()
		for cur_id in p_mgr_ii.ii_obj.id_lst:
			try:
				tmp_pred_df = whole_pred_df.loc[whole_pred_df["stock_id"]==cur_id, :]
				tmp_ii_df = p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1]
				volatility = tmp_ii_df["atr_40"]
				low_price  = tmp_ii_df["low_price"]
				weight = 1 - volatility / low_price
				pred_max_high_price = tmp_pred_df["high_price"].max()
				required_budget = pred_max_high_price / weight
				print("*** %s >>> required_budget: %f"%(cur_id, required_budget))
				# print("Last prices-----")
				# print(tmp_ii_df)
				condition1 = required_budget < available_price

				pred_price_with_pre_pred = whole_pred_price_with_pre_pred.loc[whole_pred_price_with_pre_pred["stock_id"]==int(cur_id), :]
				condition2 = (pred_price_with_pre_pred["close_price"].min() > tmp_pred_df["close_price"].max()) & (tmp_pred_df["close_price"].min() > tmp_ii_df["close_price"])
				condition3 = tmp_ii_df["move_avrg_40"] > p_mgr_ii.ii_obj.df.loc[p_mgr_ii.ii_obj.df["stock_id"]==int(cur_id), :].iloc[-1-40]["move_avrg_40"]

				if condition1 & condition2 & condition3:
					print("********** %s is labeled to buy!!!"%cur_id)

			except Exception as e:
				print("***Error:")
				print(cur_id)
				print(e)
				pass

	def apply_hold_rule(self, held_stock_lst, target_date):

		sid_lst = [hs.stock_id for hs in  held_stock_lst]
		p_mgr_hs = prediction_mgr_for_hs(held_stock_lst, target_date, self.models)

		whole_pred_df = p_mgr_ii.get_predict_price_by_models()
		whole_pred_price_with_pre_pred = p_mgr_ii.get_predict_price_with_pre_pred()
		cur_price_df = self.drs.get_cur_price(sid_lst)

		for cur_id in sid_lst:
			tmp_cur_price = cur_price_df.loc[whole_pred_df["stock_id"]==cur_id, :]["price"]

			tmp_pred_df = whole_pred_df.loc[whole_pred_df["stock_id"]==cur_id, :]
			min_low_price = tmp_pred_df["low_price"].min()

			condition1 = tmp_cur_price < min_low_price # Condition to sell

			if condition1:
				print("********** %s is labeled to sell!!!"%cur_id)











