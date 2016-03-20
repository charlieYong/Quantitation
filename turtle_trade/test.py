#!/usr/bin/env python
# coding: utf-8

from trade_system import *

def test ():
    # high, low, close, tr, n
    data = [
        [0.7220, 0.7124, 0.7124, 0.0096, 0.0134],
        [0.7170, 0.7073, 0.7073],
        [0.7099, 0.6923, 0.6923],
        [0.6930, 0.6800, 0.6838],
        [0.6960, 0.6736, 0.6736],
        [0.6820, 0.6706, 0.6706],
        [0.6820, 0.6710, 0.6710],
        [0.6795, 0.6720, 0.6744],
        [0.6760, 0.6550, 0.6616],
        [0.6650, 0.6585, 0.6627],
        [0.6701, 0.6620, 0.6701],
        [0.6965, 0.6750, 0.6965],
        [0.7065, 0.6944, 0.6944],
        [0.7115, 0.6944, 0.7087],
        [0.7168, 0.7100, 0.7124],
        [0.7265, 0.7120, 0.7265],
        [0.7265, 0.7098, 0.7098],
        [0.7184, 0.7110, 0.7184],
        [0.7280, 0.7200, 0.7228],
        [0.7375, 0.7227, 0.7359],
        [0.7447, 0.7310, 0.7389],
        [0.7420, 0.7140, 0.7162]
    ]
    # 计算每日真实波动幅度和N值
    for i in range (1, len(data)):
        yesterday = data[i-1]
        today = data[i]
        tr = cal_tr (today[0], today[1], yesterday[2])
        n = cal_real_n (yesterday[4], tr)
        today.append (tr)
        today.append (n)
    total_assets = 1000000
    unit = 42000
    print "position unit:" , cal_position_unit (data[-1][4], total_assets, unit)
    # 计算20日突破的价格
    price_list = []
    for row in data:
        price_list.append (row[2])
    print "20 days break through price:" , cal_days_break_throught_price (price_list, 20)

if __name__ == "__main__":
    test ()
