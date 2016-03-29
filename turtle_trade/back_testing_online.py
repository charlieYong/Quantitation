#!/usr/bin/env python
# coding: utf-8

import sys

import pandas as pd
import tushare as ts

import trade_system
from trade_account import *
from break_through import *

'''
使用历史数据对海龟交易系统做回测
1) 根据输入的代码，开始日期和结束日期获取历史数据
2）遍历计算真实波动值（TR）和N值
3）遍历计算好的数据，按照20日突破法进行交易模拟
'''

def cal_first_tr_and_n (df):
    total = 0
    i = 0
    tr = 0
    while i < 20:
        # 第一天的数据用于计算TR
        data = df.iloc[i + 1]
        v = trade_system.cal_tr (data.high, data.low, df.iloc[i].close)
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
    # date, open, high, low, close, tr, n
    data = [[first.Index, first.open, first.high, first.low, first.close, tr, n]]
    for item in tuples:
        tr = trade_system.cal_tr (item.high, item.low, data[-1][4])
        n = trade_system.cal_real_n (data[-1][6], tr)
        data.append ([item.Index, item.open, item.high, item.low, item.close, tr, n])
    return data

def get_price_list (data, start, end):
    l = []
    for row in data[start:end]:
        l.append (row[4])
    return l

def back_testing (Code, data, nday_break_through=20):
    '''根据历史数据做交易模拟进行回测'''
    no_trade_break = None
    is_last_break_profit = False
    # 原始资产
    TotalAssets = 10 * 10000
    account = Account(TotalAssets)
    # 从第n+1日开始遍历，计算突破
    for i in xrange (nday_break_through+1, len (data)):
        xdate, xopen, xhigh, xlow, xclose, xtr, xn = data[i]
        # 如果有被忽略的突破，则先计算
        if no_trade_break is not None:
            # 处理退出和止损
            if xlow <= no_trade_break.loss_price:
                no_trade_break.complete(no_trade_break.loss_price)
                is_last_break_profit = no_trade_break.is_profitable ()
                no_trade_break = None
            else:
                price_list = get_price_list (data, i-10, i)
                min_price = min (price_list)
                if xlow <= min_price:
                    no_trade_break.complete(min_price)
                    is_last_break_profit = no_trade_break.is_profitable ()
                    no_trade_break = None
            if no_trade_break is None:
                print '*'*8, 'complete no-trade-break, result:', is_last_break_profit, '*'*8
                continue
            # 处理50日突破
            if i > 50:
                price_list = get_price_list(data, i-50, i)
                break_through_price = max (price_list)
                if xhigh > break_through_price:
                    print '50s break through: date=%s, price=%f' % (xdate , break_through_price)
                    unit = trade_system.cal_position_unit (xn, account.current_assets)
                    account.set_market_info (Code, xn, unit)
                    account.buy (xdate, Code, break_through_price, unit)
                    no_trade_break = None
            continue

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
                is_last_break_profit = False
                no_trade_break = None
                continue
            # 10日突破退出法
            price_list = get_price_list (data, i-10, i)
            min_price = min (price_list)
            if xlow <= min_price:
                print 'exit all position, date=', xdate
                is_last_break_profit = min_price > account.first_buyin_price(Code) 
                no_trade_break = None
                account.sell_all (xdate, Code, min_price)
                account.print_assets ()
                account.clear ()
        # 空仓中，检查是否有突破发生
        else:
            price_list = get_price_list(data, i-20, i)
            break_through_price = max (price_list)
            if xhigh <= break_through_price:
                continue
            # 突破
            print '20s break through: date=%s, price=%f' % (xdate , break_through_price)
            if is_last_break_profit:
                print 'last break is profitable, ignore this break'
                no_trade_break = BreakThrough(break_through_price, break_through_price - 2*xn)
                continue
            unit = trade_system.cal_position_unit (xn, account.current_assets)
            account.set_market_info (Code, xn, unit)
            account.buy (xdate, Code, break_through_price, unit)

if __name__ == "__main__":
    if len (sys.argv) != 4:
        print "usage: %s code startdate enddate" % sys.argv[0]
        sys.exit()
    code, start, end = sys.argv[1:4]
    df = ts.get_hist_data (code, start, end)
    # 加载数据，按日期重新排序，导出list时为时间升序
    df = df.reindex (index=df.index[::-1])
    # 计算每日的TR值和N值
    data = cal_tr_and_n (df)
    # 进行回测
    back_testing (code, data)
