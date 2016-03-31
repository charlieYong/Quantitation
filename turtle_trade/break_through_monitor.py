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

class BreakThroughMonitor(object):
    def __init__ (self, code_list=None):
        self.stock_info = ts.get_stock_basics ()
        self.code_list = code_list
        if self.code_list is None:
            self.code_list = self.stock_info.index.tolist()
        self.stoped_set = set ()
        #self.load_stoped_stock ()

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

    def load_stoped_stock (self):
        d = self.last_trade_date ()
        for code in self.code_list:
            df = ts.get_hist_data (code, d, d)
            if len (df.index) <= 0:
                print "stoped:", code
                self.stoped_set.add (code)

    def start (self):
        end = self.last_trade_date ()
        start = self.get_start_date (end, 100)
        print end, start
        #for code in self.code_list:

if __name__ == "__main__":
    b = BreakThroughMonitor()
    b.start ()
    #df = ts.get_hist_data ("600710", "2016-03-31", "2016-03-31")
    #print len (df.index)
