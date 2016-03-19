#!/usr/bin/env python

import datetime

import tushare as ts

date = datetime.datetime.today ().strftime ("%Y%m%d")
csvfile = "stock_info.%s.csv" % date

df = ts.get_stock_basics ()
df.to_csv (csvfile)

