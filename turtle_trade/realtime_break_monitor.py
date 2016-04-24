#!/usr/bin/env python
# coding: utf-8

'''
实时监控股票价格突破
'''

import sys
import time
from collections import namedtuple

import tushare as ts

class RealTimeMonitor(object):
    def __init__(self, monitorlist):
        self.codelist = []
        self.break_price_dict = {}
        for node in monitorlist:
            self.codelist.append (node.code)
            self.break_price_dict[node.code] = node.break_price

    def start(self):
        '''
        每3秒获取一次数据判断是否要突破
        '''
        while True:
            qslist = ts.get_realtime_quotes (self.codelist).itertuples ()
            print "-" * 20
            for qs in qslist:
                price = float(qs.price)
                break_price = self.break_price_dict[qs.code]
                percent = "%.2f%%" % ((break_price - price)/price *  100)
                print "%s, now=%.2f, break=%.2f, need=%s" % (qs.code, price, break_price, percent)
            print "-" * 20
            print "\n"
            sys.stdout.flush ()
            time.sleep (3)

def parse_monitor_file (filename):
    '''
    文件格式：
    股票代码 突破价格
    '''
    Monitor = namedtuple ("Monitor", "code break_price")
    monitorlist = []
    with open (filename) as f:
        for line in f:
            code, break_price = line.split()
            monitorlist.append (Monitor (code, float(break_price)))
    return monitorlist

if __name__ == "__main__":
    if len (sys.argv) != 2:
        print "usage:%s monitorfile" % sys.argv[0]
        sys.exit ()

    monitor = RealTimeMonitor (parse_monitor_file (sys.argv[1]))
    monitor.start ()
