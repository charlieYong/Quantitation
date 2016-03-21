#!/usr/bin/env python
# coding: utf-8

def cal_tr (high, low, pdc):
    '''
    high: 当日最高价
    low: 当日最低价
    pdc: 前一日收盘价
    return: 当日真实波动幅度
    '''
    return max (high - low, high - pdc, pdc - low)

def cal_first_n (trlist):
    '''
    由于N值计算公式需要使用前一日的N值，因此第一次计算N值时只能计算真实波动幅度的20日简单平均值
    trlist: 20日的真实波动幅度值列表
    return: 首次计算的N值（价格波动性）
    '''
    i=0
    total = 0
    for tr in trlist:
        total += tr
        i += 1
        if i >= 20:
            break
    return total / i

def cal_real_n (pdn, tr):
    '''
    pdn: 前一日的N值
    tr: 当日的真实波动幅度
    return: 价格波动性
    '''
    return (19 * pdn + tr) / 20

def cal_position_unit (n, total_assets, n_unit=1, percent=0.01):
    '''
    n: N值
    n_unit: 每一点N值代表的价值
    total_assets: 总资产
    percent: 账户占比
    '''
    return (total_assets * percent) / (n * n_unit)

