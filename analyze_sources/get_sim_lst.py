import datetime
import investing_info
import numpy as np

from_date = datetime.date(2017,3,1)
to_date = datetime.date(2018,2,27)

l = investing_info.get_similarity(from_date, to_date)

g_lst=[]
g_lstu=[]
g_u_lst=[]
ii_lst = []

thre = 0.9

high_matrix = l.corr()>thre
high_matrix_stack = high_matrix.stack()
high_pairs = list(high_matrix_stack[high_matrix_stack==True].index)

for i in high_pairs:
    f=False
    for g in g_lst:
            if i[0] in g or i[1] in g:
                    g.append(i[0])
                    g.append(i[1])
                    f=True
                    break
    if not f:
            g_lst.append([i[0], i[1]])

for i in g_lst:
	tmp_lst = list(set(i))
	if len(tmp_lst) > 1:
	    g_lstu.append(tmp_lst)

g_lstu = g_lstu[1:len(g_lstu)]


for i in g_lstu:
	ii_obj = investing_info.investing_info(i, from_date, to_date)
	ii_lst.append(ii_obj)

n=0
for i in ii_lst:
	i.plt_chart_all(os.path.join(os.getcwd(), "chart" + str(n)))
	n+=1