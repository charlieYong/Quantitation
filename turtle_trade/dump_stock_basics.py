#!/usr/bin/env python
# coding: utf-8

import sys
import datetime

import tushare as ts

'''
# 获取所有的股票基本信息
date = datetime.datetime.today ().strftime ("%Y%m%d")
csvfile = "stock_info.%s.csv" % date

df = ts.get_stock_basics ()
df.to_csv (csvfile)
'''

def dump_history_data (code, startdate, enddate, filename):
    '''获取某个股票的日线历史数据'''
    print "正在获取 %s 从 %s 到 %s 的日线历史数据" % (code, startdate, enddate)
    df = ts.get_hist_data (code, startdate, enddate, "D")
    print df.values
    df.to_csv (filename)

def help ():
    print "\t获取某个股票的历史数据：dump $code $startdate(YYYY-MM-DD) $enddate(YYYY-MM-DD) $filename"
    sys.exit ()

if __name__ == "__main__":
    if len (sys.argv) <= 1:
        help ()
    cmd = sys.argv[1]
    if cmd == "dump" and len (sys.argv) == 6:
        code, start, end, filename = sys.argv[2:]
        dump_history_data (code, start, end, filename)
    else:
        help ()

