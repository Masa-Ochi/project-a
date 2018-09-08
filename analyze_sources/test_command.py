fl=1

import datetime
import investing_info as ii
import prediction_mgr as pmgr
models = []
from keras.models import load_model
models.append(load_model("./tmp_30/models/full/model.ep50.h5"))

if fl==1:
	ii_obj1 = ii.get_ii_obj_by_stock_market("東証一部", datetime.date(2018,6,20), datetime.datetime.today(), True)
	pmgr_ii1  = pmgr.prediction_mgr_for_ii(ii_obj1, models)
	pmgr_ii1.get_predict_price_by_models()
	pmgr_ii1.get_predict_price_with_pre_pred()
	pmgr_ii1.plot_charts()

elif fl==2:
	ii_obj2 = ii.get_ii_obj_by_stock_market("東証一部", datetime.date(2018,8,20), datetime.datetime.today())
	pmgr_ii2  = pmgr.prediction_mgr_for_ii(ii_obj2, models)
	pmgr_ii2.get_predict_price_by_models()