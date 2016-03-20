#!/usr/bin/env python
# coding: utf-8

import sys

import pandas as pd
import tushare as ts

import trade_system

'''
使用历史数据对海龟交易系统做回测
1) 根据数据文件加载该股票的历史数据
2）遍历计算真实波动值（TR）和N值
3）遍历计算好的数据，按照20日突破法进行交易模拟
'''

def cal_first_tr_and_n (data_list):
    total = 0
    i = 0
    tr = 0
    while i < 20:
        # 第一天的数据用于计算TR
        data = data_list[i + 1]
        v = trade_system.cal_tr (data[2], data[4], data_list[i][3])
        if 0 == i:
            tr = v
        total += v
        i += 1
    return tr, total/20


def cal_tr_and_n (data_list):
    # 先计算前20日的TR值以计算出第一个N值
    first = data_list[1]
    tr, n = cal_first_tr_and_n (data_list)
    # date, open, high, low, close, tr, n
    data = [[first[0], first[1], first[2], first[4], first[3], tr, n]]
    for i in xrange (2, len (data_list)):
        item = data_list[i]
        tr = trade_system.cal_tr (item[2], item[4], data[-1][4])
        n = trade_system.cal_real_n (data[-1][6], tr)
        data.append ([item[0], item[1], item[2], item[4], item[3], tr, n])
    print data

if __name__ == "__main__":
    if len (sys.argv) != 2:
        print "usage: %s datafile" % sys.argv[0]
        sys.exit()
    # 加载数据，按日期重新排序，导出list时为时间升序
    df = pd.read_csv (sys.argv[1]).sort_index (0, None, False)
    data_list = df.values.tolist ()
    cal_tr_and_n (data_list)
