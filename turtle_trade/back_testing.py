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

class TradeRecord(object):
    '''交易记录'''
    def __init__(self, tradetype, price, positions):
        self._record_list = [(tradetype, price, positions)]

    def set_info(self, n, unit):
        self.n = n
        self.unit = unit
        self.loss_price = self._record_list[0][1] - 2*n

    def add(self, tradetype, price, positions):
        self._record_list.append((tradetype, price, positions))
        if -1 == tradetype:
            self.loss_price += n/2

    def get_record_list(self):
        return self._record_list

    def get_last_buy_in_price(self):
        p = 0
        for (tradetype, price, positions) in self._record_list:
            if 1 == tradetype:
                p = price
        return p

    def get_total_positions(self):
        total = 0
        for (tradetype, price, positions) in self._record_list:
            total += (tradetype * positions)
        return total

    def profit(self):
        total = 0
        for (tradetype, price, positions) in self._record_list:
            total += (tradetype * price * positions)
        return total

    def print_trade(self):
        print "n=%f, position unit=%d" % (self.n, self.unit)
        for record in self._record_list:
            print "type=%d, price=%f, positions=%d" % record
        print "Total Profit:", self.profit ()

def back_testing (data, nday_break_through=20):
    '''根据历史数据做交易模拟进行回测'''
    # 原始资产
    CurrentAssets = TotalAssets = 10 * 10000
    MaxPositions = 4
    trade = None
    # 从第n+1日开始遍历，计算突破
    for i in xrange (nday_break_through+1, len (data)):
        xdate, xopen, xhigh, xlow, xclose, xtr, xn = data[i]
        # 参与突破持有中，检查是否需要退出（止损/10日突破退出法）
        if trade is not None: 
            if MaxPositions > trade.get_total_positions () and (xhigh - trade.get_last_buy_in_price ()) >= (trade.n/2):
                # 价格上涨1/2N，加仓
                while (xhigh - trade.get_last_buy_in_price ()) >= (trade.n/2):
                    price = trade.get_last_buy_in_price () + trade.n/2
                    trade.add (1, price, 1)
                    print 'incr position, date=%s, price=%f, positions=%d' % (xdate, price, trade.get_total_positions ())
                    if trade.get_total_positions ()>= MaxPositions:
                        break
            exit_price = 0
            # 是否触发止损
            if xhigh <= trade.loss_price:
                exit_price = trade.loss_price
                print 'loss to exit trade: date=%s, price=%f' % (xdate, exit_price)
            else:
                # 10日突破退出法
                price_list = get_price_list (data, i-10, i)
                min_price = min (price_list)
                if xlow <= min_price:
                    exit_price = min_price
                    print '10 days exit trade: date=%s, price=%f' % (xdate, exit_price)
            if exit_price > 0:
                trade.print_trade ()
                CurrentAssets += trade.profit ()
                print 'Assets: %.2f(%d)' % (CurrentAssets, TotalAssets)
                trade = None
                continue
        # 空仓中，检查是否有突破发生
        else:
            price_list = get_price_list(data, i-20, i)
            break_through_price = max (price_list)
            if not xhigh > break_through_price:
                continue
            # 突破
            unit = trade_system.cal_position_unit (xn, CurrentAssets)
            trade = TradeRecord (1, break_through_price, 1)
            trade.set_info (xn, unit)
            # 测试只买入一个头寸单位的仓位
            print 'break through: date=%s, price=%f, loss_price=%f unit=%d, n=%f' % (xdate , break_through_price,
            trade.loss_price, unit, xn)


if __name__ == "__main__":
    if len (sys.argv) != 2:
        print "usage: %s datafile" % sys.argv[0]
        sys.exit()
    # 加载数据，按日期重新排序，导出list时为时间升序
    df = pd.read_csv (sys.argv[1]).sort_index (0, None, False)
    # 计算每日的TR值和N值
    data = cal_tr_and_n (df.values.tolist ())
    # 进行回测
    back_testing (data)
