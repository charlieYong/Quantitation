#!/usr/bin/env python
# conding: utf-8

class TradeRecord(object):
    '''成交记录'''
    def __init__(self, date, price, count, direction):
        self.date = date
        self.price = price
        self.count = count
        self.direction = direction

    def __str__(self):
        return "date=%s, price=%f, count=%d, direction=%d" % (self.date, self.price, self.count, self.direction)

class PositionDetail(object):
    '''仓位明细'''
    def __init__(self, price, count, loss_price):
        self.price = price
        self.count = count
        self.loss_price = loss_price
        
class MakgetInfo(object):
    '''开仓信息'''
    def __init__(self, n, unit):
        self.n = n
        self.unit

class Account(object):
    '''交易账号'''
    def __init__(self, total_assets):
        self.total_assets = total_assets
        self.position_dict = {}
        self.market = {}

    def set_market_info(self, code, n, unit):
        self.market[code] = MarketInfo(n, unit)

    def buy(self, code, price, count):
        info = self.market[code]
        if code not in self.position_dict:
            # 新开仓
            self.position_dict[code] = [PositionDetail (price, count, price - 2*info.n)]
            return
        # 加仓
        # 前面仓位止损价格提高n/2
        for item in self.position_dict[code]:
            item.loss_price += (info.n/2)
        self.position_dict[code].append (PositionDetail (price, count, price - 2*info.n))


