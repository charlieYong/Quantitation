#!/usr/bin/env python
# coding: utf-8

'''
1，获取所有股票信息（代码，市值等）
2，遍历选出将要突破的股票（10%之内）列表
3，开市期间实时检测是否在突破
'''
import os
import sys
import time
import datetime
import multiprocessing as mp

import tushare as ts
from config import *
from break_through import *
from back_testing_online import *

lock = mp.Lock ()

def delete_break_file ():
    filename = "break_%s.txt" % time.strftime ("%Y%m%d", time.localtime (time.time ()))
    if os.path.exists (filename):
        os.remove (filename)

def write_break_node (node):
    filename = "break_%s.txt" % time.strftime ("%Y%m%d", time.localtime (time.time ()))
    f = open (filename, "a")
    f.write ("%s\n" % node)
    f.flush ()

class AboutToBreakNode(object):
    def __init__(self, code, price, break_price, trend):
        self.code = code
        self.price = price
        self.break_price = break_price
        self.trend = trend

    def __str__(self):
        percent_to_break = "%.2f%%" % ((self.break_price- self.price)/self.price * 100)
        return "%s price=%.2f, break_price=%2.f, percent_to_break=%s, recent_trend=%.2f" % (self.code, self.price, self.break_price, percent_to_break, self.trend)


class Monitor(mp.Process):
    def __init__ (self, task_queue, progress, start_date, end_date):
        mp.Process.__init__ (self)
        self.task_queue = task_queue 
        self.progress = progress
        self.start_date = start_date
        self.end_date = end_date

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
                    cur = BreakThrough (xdate, max_price, max_price-xn*2)
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

    def check_trend (self, data, nday=5):
        check = len (data) - nday
        return data[-1][4] > data[check][4]

    def get_trend (self, data, nday=20):
        count = len (data)
        max_price = self.get_max_price (data, count-20, count)
        min_price = self.get_min_price (data, count-20, count)
        return (max_price-min_price)/min_price

    def continueous_fall (self, data, nday=3, percent=0.05):
        l = len (data)
        idx = l - nday
        total_fall = 0
        for i in xrange (idx, l):
            last_close = data[i-1][4]
            cur_close = data[i][4]
            if cur_close < last_close:
                total_fall += (last_close - cur_close)
                if ((i-idx+1) >= nday) and (total_fall/cur_close >= percent):
                    return True

            else:
                break
        return False

    def myprint (self, s):
        print "\n", self.name, s
        sys.stdout.flush ()

    def task_done (self):
        with self.progress.get_lock ():
            self.progress.value += 1

    def check_code (self, code):
        global lock
        try:
            df = ts.get_h_data (code, self.start_date, self.end_date, retry_count=5)
        except:
            sys.stderr.write ("exception: get_h_data (%s, %s, %s)" % (code, self.start_date, self.end_date))
            sys.stderr.flush ()
            return
        if df is None:
            #print "fail to get history data:", code
            return
        if len (df.index) < 21 or self.end_date != df.index[0].strftime ("%Y-%m-%d"):
            #print "not enough data"
            return
        # 按日期重新排序，时间升序
        df = df.sort_index (ascending=True)
        data = cal_tr_and_n (df)
        break_list = self.get_break_through_list (data)
        if len (break_list) > 0:
            last = break_list[-1]
            if not last.is_complete ():
                #print "break through ing, ignore:", code, last
                return
            elif last.is_profitable ():
                #print "last break is profit, ignore:", code, last
                return
        '''
        趋势判断：
            最近五天趋势为向上
            排除连续三天下跌的
        '''
        if not self.check_trend (data):
            #print "not a up trend:", code
            return
        if self.continueous_fall (data):
            #print "continueous fall:", code
            return
        count = len (data) - 1
        max_price = self.get_max_price (data, count-20, count)
        cur_price = data[-1][4]
        if cur_price < max_price and cur_price*1.055 >= max_price:
            break_node = AboutToBreakNode(code, cur_price, max_price, self.get_trend(data))
            self.myprint (break_node)
            lock.acquire ()
            write_break_node (break_node)
            lock.release ()

    def run (self):
        while True:
            code = self.task_queue.get ()
            if code is None:
                break
            self.check_code (code)
            self.task_done ()
        self.myprint ("Exit")

class BreakThroughMonitor(object):
    def __init__ (self, code_list=None):
        self.stock_info = ts.get_stock_basics ()
        self.code_list = code_list
        if self.code_list is None:
            self.code_list = self.stock_info.index.tolist()

    def last_trade_date (self):
        '''找到最近一个交易日期'''
        i = 1
        # 如果当天已经收市，则i＝0
        now = time.localtime (time.time ())
        if now.tm_hour >= A_CLOSE_HOUR:
            i = 0
        last_trade_date = None
        # 由于tushare的代码有bug，这里先自己实现
        cal = ts.util.dateu.trade_cal ()
        # 格式为 2016/4/4
        cal = cal[cal.isOpen == 1]['calendarDate'].values
        while (True):
            t = time.localtime (time.time () - i*86400)
            d = "%d/%d/%d" % (t.tm_year, t.tm_mon, t.tm_mday)
            i += 1
            if d in cal:
                last_trade_date = time.strftime (DATE_FORMAT, t)
                break
        print 'last trade date:', last_trade_date
        return last_trade_date

    def get_start_date (self, end, nday):
        d = datetime.datetime.strptime (end, DATE_FORMAT)
        return (d + datetime.timedelta (-nday)).strftime (DATE_FORMAT)

    def start (self):
        delete_break_file ()
        enddate = self.last_trade_date ()
        startdate = self.get_start_date (enddate, 100)
        # 分配每个线程的代码任务列表
        worker_count = mp.cpu_count () * 5
        task_queue = mp.Queue ()
        # 创建和启动工作进程
        progress = mp.Value ('i', 0)
        workers = []
        for i in xrange (worker_count):
            w = Monitor (task_queue, progress, startdate, enddate)
            workers.append (w)
            w.start ()
        print "start %d workers to run" % len (workers)
        sys.stdout.flush ()
        # 往任务队列添加任务
        for code in self.code_list:
            task_queue.put (code)
        for i in xrange (worker_count + 10):
            task_queue.put (None)
        # 等待执行完毕
        while progress.value < len (self.code_list):
            time.sleep (10)
            print "-------->workers(%d) progress:%d => %d <---------" % (len (mp.active_children ()), progress.value, len (self.code_list))
            sys.stdout.flush ()
            if len (mp.active_children ()) <= 0:
                print "All Workers Exits"
                sys.stdout.flush ()
                break


if __name__ == "__main__":
    b = BreakThroughMonitor()
    b.start ()
    #df = ts.get_h_data ("300029", "2016-03-31", "2016-04-01")
    #print df
