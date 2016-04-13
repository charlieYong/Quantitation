#!/usr/bin/env python
# coding: utf-8

import sys
import time

import pandas as pd
import tushare as ts

from trade_system import *
from trade_account import *

'''
根据当前资金总额计算股票的tr值和N值（波动值），从而计算应该买入的股数和止损价格
'''

def cal_first_tr_and_n (df):
    total = 0
    i = 0
    tr = 0
    while i < 20:
        # 第一天的数据用于计算TR
        data = df.iloc[i + 1]
        v = cal_tr (data.high, data.low, df.iloc[i].close)
        if 0 == i:
            tr = v
        total += v
        i += 1
    return tr, total/20

def cal_tr_and_n (df):
    # 先计算前20日的TR值以计算出第一个N值
    tuples = df.itertuples()
    # 第一天去掉
    next (tuples)
    first = next (tuples)
    tr, n = cal_first_tr_and_n (df)
    # 计算每日的TR值和N值
    # date, close, tr, n
    data = [[first.Index, first.close, tr, n]]
    for item in tuples:
        tr = cal_tr (item.high, item.low, data[-1][1])
        n = cal_real_n (data[-1][3], tr)
        data.append ([item.Index, item.close, tr, n])
    return data

if __name__ == "__main__":
    if len (sys.argv) < 3:
        print "usage: %s total_asset code price(optional)" % sys.argv[0]
        sys.exit()
    assets = int (sys.argv[1])
    code = sys.argv[2]
    price = 0
    if len (sys.argv) >= 4:
        price = float (sys.argv[3])
    nday = 60
    enddate = time.strftime ("%Y-%m-%d", time.localtime (time.time ()))
    startdate = time.strftime ("%Y-%m-%d", time.localtime (time.time () - nday*86400))
    df = ts.get_hist_data (code, startdate, enddate)
    # 加载数据，按日期重新排序，导出list时为时间升序
    df = df.reindex (index=df.index[::-1])
    # 计算每日的TR值和N值
    data = cal_tr_and_n (df)
    curdate, curprice, tr, n = data[-1]
    position_unit = cal_position_unit (n, assets)
    print "date=%s, tr=%.2f, n=%.2f" % (curdate, tr, n)
    if price <= 0:
        price = curprice
    print "price=%.2f, count=%d, value=%.2f, min_price=%.2f, risk=%.2f" % (curprice, position_unit, curprice*position_unit, curprice-2*n, 2*n * position_unit)
