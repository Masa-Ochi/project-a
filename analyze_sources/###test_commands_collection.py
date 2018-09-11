from prediction_mgr import prediction_mgr_for_hs_arr
from trade_mgr import held_stock
from keras.models import load_model
from datetime import datetime, timedelta, date
d=datetime.today()-timedelta(days=1)
m1=load_model("./tmp_30/models/full/model.ep50.h5")
m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")
#m2=load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho2bu/model.ep26.h5")
hs_lst = [held_stock(6502,date(2018,7,23),[349,349,342,345],100,100), held_stock(7201,date(2018,4,10),[1115,1129.5,1114.5,1126],100,100)]
p = prediction_mgr_for_hs_arr(hs_lst, d, [m1, m2])
a,b = p.get_predict_price_by_models()


from prediction_mgr import prediction_mgr_for_ii_arr
import investing_info as ii
from keras.models import load_model
from datetime import datetime, timedelta, date
m1=load_model("./tmp_30/models/full/model.ep50.h5")
m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")
m3=load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5")
ii_obj = ii.get_ii_obj_by_stock_market("東証一部", date(2018,5,1), date(2018,8,10))
#for i in range(30):
#	p = prediction_mgr_for_ii_arr(ii_obj, [m1, m2, m3])
#	a,b = p.get_predict_price_by_models()
import datetime
# ii_obj = ii.investing_info([1853, 6502, 1711], datetime.date(2018,5,1),datetime.date(2018,6,23))
p = prediction_mgr_for_ii_arr(ii_obj, [m1, m2, m3])
a = p.get_predict_price_by_models(30)
a.to_pickle("./Tosho1bu_predicted_df.pkl")


from logic_mgr import logic_mgr_simulator
lmgr = logic_mgr_simulator()
import investing_info as ii
import datetime
from training_chart_data import *
# ii_obj = ii.get_ii_obj_by_stock_market("東証二部", datetime.date(2018,1,1), datetime.date(2018,8,10))
# ii_obj = ii.get_ii_obj_by_stock_market("東証一部", datetime.date(2018,1,1), datetime.date(2018,8,10))
# ii_obj = ii.investing_info([1853, 6502, 1711], datetime.date(2018,1,1), datetime.date(2018,6,23))
ii_obj = try_to_load_as_pickled_object_or_None("./Tosho1bu_ii_obj_20180101-20180810.pkl")
p = lmgr.retrieve_ought_to_buy_items(ii_obj, 600000, 300)
# p.to_pickle("./Tosho1bu_apply_buy_rule_20180101-20180810.pkl")
# p, p_raw1, p_raw2 = lmgr.retrieve_ought_to_buy_items(ii_obj, 600000, 50)



import numpy as np
import pandas as pd
import investing_info as ii 
from prediction_mgr import prediction_mgr_for_ii, prediction_mgr_for_hs
from keras.models import load_model
from datetime import datetime, timedelta, date
m1=load_model("./tmp_30/models/full/model.ep50.h5")
#m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")
#m3=load_model("/Volumes/StreamS06_2TB/project_a/tmp_90/models/Tosho1bu/model.ep29.h5")
pred_price_lst = pd.DataFrame()
for i in range(60):
	from_d=datetime(2010,1,1)
	to_d=datetime(2018,5,1) + timedelta(days=i)
#	ii_obj = ii.get_ii_obj_by_stock_market("東証一部", from_d, to_d)
	ii_obj = ii.investing_info([6502, 7201, 2163, 1325, 1333], from_d, to_d)
#	p = prediction_mgr_for_ii(ii_obj, [m1, m2, m3])
	p = prediction_mgr_for_ii(ii_obj, [m1])
	tmp_pred_price_lst = p.get_predict_price_by_models()
	pred_price_lst = pred_price_lst.append(tmp_pred_price_lst)




import investing_info as ii
from keras.models import load_model
from datetime import datetime, timedelta, date
from mpl_finance import candlestick_ohlc
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
import os
import my_utils
init_date = datetime(2018,8,10)
i=0
from_d=datetime(2010,1,1)
to_d=init_date + timedelta(days=i)
s_lst=[6502,7201]
#ii_obj = ii.investing_info(s_lst, from_d, to_d)
ii_obj = ii.get_ii_obj_by_stock_market("東証一部", from_d, to_d)
save_as_pickled_object(ii_obj, "./test_ii_full.pkl")
ii_obj = try_to_load_as_pickled_object_or_None("./test_ii_full.pkl")
import logic_mgr as lmgr
l=lmgr.logic_mgr(ii_obj)
l.apply_buy_rule(5000)

import download_charts_selenium as dcs
import stock_charts_updateDB as scud
m1=load_model("./tmp_30/models/full/model.ep50.h5")
m2=load_model("./tmp_30/models/Tosho1bu/model.ep50.h5")

from prediction_mgr import prediction_mgr_for_ii
p = prediction_mgr_for_ii(ii_obj, [m1, m2])
tmp_pred_price_lst = p.get_predict_price_by_models()
p.get_predict_price_with_pre_pred()







import investing_info as ii
s_lst= [6502, 2163]
from datetime import date
tmp_ii_obj = ii.investing_info(s_lst, date(1900, 1, 1), d)
tolal_cols = ["stock_id", "open_price", "high_price", "low_price", "close_price", "output"]
target_cols = ["open_price", "high_price", "low_price", "close_price", "output"]
# for sid in self.s_lst:
    # tmp_df = tmp_ii_obj.df.loc[tmp_ii_obj.df["stock_id"]==sid, target_cols]
tmp_df = tmp_ii_obj.df.loc[:, tolal_cols]
tmp_l = len(tmp_df)
import numpy as np
from my_utils import *
n=np.array(df_to_array(tmp_df, target_cols))
