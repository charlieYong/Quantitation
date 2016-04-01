#!/usr/bin/env python
# coding: utf-8

'''
1，获取所有股票信息（代码，市值等）
2，遍历选出将要突破的股票（10%之内）列表
3，开市期间实时检测是否在突破
'''
import time
import datetime

import tushare as ts
from config import *
from break_through import *
from back_testing_online import *

class BreakThroughMonitor(object):
    def __init__ (self, code_list=None):
        self.stock_info = ts.get_stock_basics ()
        self.code_list = code_list
        if self.code_list is None:
            self.code_list = self.stock_info.index.tolist()
        self.stoped_set = set ()

    def last_trade_date (self):
        '''找到最近一个交易日期'''
        i = 1
        # 如果当天已经收市，则i＝0
        now = time.localtime (time.time ())
        if now.tm_hour >= A_CLOSE_HOUR:
            i = 0
        last_trade_date = None
        while (True):
            last_trade_date = time.strftime (DATE_FORMAT, time.localtime (time.time () - i*86400))
            i += 1
            if not ts.util.dateu.is_holiday (last_trade_date):
                break
        print 'last trade date:', last_trade_date
        return last_trade_date

    def get_start_date (self, end, nday):
        d = datetime.datetime.strptime (end, DATE_FORMAT)
        return (d + datetime.timedelta (-nday)).strftime (DATE_FORMAT)

    def get_stock_info (self, code, cur_price):
        info = self.stock_info.loc[code]
        return "name=%s, out=%.2f, total=%.2f" % (info.name, info.outstanding*cur_price/10000, info.totals*cur_price/10000) 

    def get_price_list (self, data, start, end):
        l = []
        i = start
        while i < end:
            l.append (data[i][4])
            i += 1
        return l

    def get_max_price (self, df, start, end):
        return max (self.get_price_list (df, start, end))

    def get_min_price (self, df, start, end):
        return min (self.get_price_list (df, start, end))

    def get_break_through_list (self, data):
        l = []
        cur = None
        nday = 20
        for i in xrange (nday+1, len (data)):
            xdate, xopen, xhigh, xlow, xclose, xtr, xn = data[i]
            if cur is None:
                max_price = self.get_max_price (data, i-nday-1, i-1)
                if xhigh >= max_price:
                    cur = BreakThrough (xdate, max_price, max_price-xn/2)
                    l.append (cur)
            else:
                if xlow <= cur.loss_price:
                    cur.complete (cur.loss_price)
                    cur = None
                else:
                    min_price = self.get_min_price (data, i-1-10, i-1)
                    if xlow <= min_price:
                        cur.complete (min_price)
                        cur = None
        return l

    def start (self):
        end = self.last_trade_date ()
        start = self.get_start_date (end, 100)
        for code in self.code_list:
            df = ts.get_hist_data (code, start, end)
            if len (df.index) < 21 or end != df.index[0]:
                continue
            print "check ", code
            # 按日期重新排序，时间升序
            df = df.reindex (index=df.index[::-1])
            data = cal_tr_and_n (df)
            break_list = self.get_break_through_list (data)
            if len (break_list) > 0 and not break_list[-1].is_complete ():
                print "break through ing, ignore:", code, break_list[-1]
                continue
            lastest = len (data) - 1
            max_price = self.get_max_price (data, lastest-20, lastest)
            cur_price = data[-1][4]
            if cur_price < max_price and cur_price*1.08 >= max_price:
                percent = "%.2f%%" % ((max_price - cur_price)/cur_price * 100)
                print "about to break through:", code, cur_price, max_price, percent, self.get_stock_info (code, cur_price) 


if __name__ == "__main__":
    b = BreakThroughMonitor()
    b.start ()
    #df = ts.get_hist_data ("600710", "2016-03-31", "2016-03-31")
    #print len (df.index)
