#!/usr/bin/env python
# coding: utf-8

import sys

import pandas as pd
import tushare as ts

import trade_system
from trade_account import *

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
    print data_list
    tr, n = cal_first_tr_and_n (data_list)
    # 计算每日的TR值和N值
    # date, open, high, low, close, tr, n
    data = [[first[0], first[1], first[2], first[4], first[3], tr, n]]
    for i in xrange (2, len (data_list)):
        item = data_list[i]
        tr = trade_system.cal_tr (item[2], item[4], data[-1][4])
        n = trade_system.cal_real_n (data[-1][6], tr)
        data.append ([item[0], item[1], item[2], item[4], item[3], tr, n])
    return data

def get_price_list (data, start, end):
    l = []
    for row in data[start:end]:
        l.append (row[4])
    return l

def back_testing (data, nday_break_through=20):
    '''根据历史数据做交易模拟进行回测'''
    # 原始资产
    Code = "11111"
    TotalAssets = 10 * 10000
    account = Account(TotalAssets)
    # 从第n+1日开始遍历，计算突破
    for i in xrange (nday_break_through+1, len (data)):
        xdate, xopen, xhigh, xlow, xclose, xtr, xn = data[i]
        # 参与突破持有中，检查是否需要退出（止损/10日突破退出法）
        if account.has_position (Code):
            while account.current_assets >= (account.unit_value(Code) * xlow) and (xhigh - account.last_buyin_price (Code)) >= (account.n_value (Code)/2):
                # 价格上涨1/2N，加仓
                print 'incr position, date=%s' % xdate
                price = account.last_buyin_price (Code) + account.n_value(Code)/2
                account.buy (xdate, Code, price, account.unit_value (Code))
            # 是否触发止损
            position_list = account.position_detail_list (Code)
            for position in position_list:
                if xlow <= position.loss_price:
                    print 'loss position, date=', xdate
                    account.sell (xdate, Code, position.loss_price, position.count)
            if not account.has_position (Code):
                account.print_assets ()
                account.clear ()
                continue
            # 10日突破退出法
            price_list = get_price_list (data, i-10, i)
            min_price = min (price_list)
            if xlow <= min_price:
                print 'exit all position, date=', xdate
                account.sell_all (xdate, Code, min_price)
                account.print_assets ()
                account.clear ()
        # 空仓中，检查是否有突破发生
        else:
            price_list = get_price_list(data, i-20, i)
            break_through_price = max (price_list)
            if not xhigh > break_through_price:
                continue
            # 突破
            print 'break through: date=%s, price=%f' % (xdate , break_through_price)
            unit = trade_system.cal_position_unit (xn, account.current_assets)
            account.set_market_info (Code, xn, unit)
            account.buy (xdate, Code, break_through_price, unit)
            # 测试只买入一个头寸单位的仓位

if __name__ == "__main__":
    if len (sys.argv) <= 1:
        print "usage: %s datafile" % sys.argv[0]
        sys.exit()
    # 加载数据，按日期重新排序，导出list时为时间升序
    df = pd.read_csv (sys.argv[1]).sort_index (0, None, False)
    # 计算每日的TR值和N值
    data = cal_tr_and_n (df.values.tolist ())
    # 进行回测
    back_testing (data)
