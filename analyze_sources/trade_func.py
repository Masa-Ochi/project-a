from trade_mgr import *
from crud_for_stock_detail import CRUD_for_STOCK_DETAIL




class trade_func(object):
	def __init__(self, budget, hs_lst, buy_amap=False):
		self.budget   = budget
		self.buy_amap = buy_amap
		self.hs_lst   = hs_lst

	def buy(self, stock_id, amount, price, date):
		if self.budget > amount * price:
			self.budget = self.budget - amount * price
			self.crud = CRUD_for_STOCK_DETAIL()
			unit = self.crud.read_tbl_by_df("WHERE stock_id='%s'"%str(stock_id))["stock_unit"].values[0]
			hs = held_stock(stock_id, date, price, amount, unit, date)
			self.hs_lst.append(hs)
			return self.budget, self.hs_lst
		else:
			if self.buy_amap:
				return self.budget, self.hs_lst
			else:
				return self.budget, self.hs_lst

	def sell(self, stock_id, cur_price):
		fl = False
		for hs in self.hs_lst:
			if hs.stock_id == stock_id:
				fl = True
				break
		if not fl:
			return self.budget, self.hs_lst

		self.budget = self.budget + hs.b_amount * cur_price
		print("The profit is: %d"%(hs.b_amount * cur_price - hs.b_amount * hs.b_price))
		self.hs_lst.remove(hs)
		
		return self.budget, self.hs_lst





