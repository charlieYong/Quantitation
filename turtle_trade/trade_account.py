#!/usr/bin/env python
# coding: utf-8

class TradeRecord(object):
    '''成交记录'''
    def __init__(self, date, code, price, count, direction):
        self.date = date
        self.code = code
        self.price = price
        self.count = count
        self.direction = direction

    def __str__(self):
        return "date=%s, price=%f, count=%d, direction=%d" % (self.date, self.price, self.count, self.direction)

class TurtleTradeNode(object):
    '''海龟交易系统交易节点'''
    def __init__(self, price, count, loss_price):
        self.buy_price = price
        self.count = count
        self.loss_price = loss_price
        self.sell_price = 0

    def sell(self, sell_price):
        self.sell_price = sell_price

    def is_complete(self):
        return self.sell_price > 0

    def get_profit(self):
        return self.count * (self.sell_price - self.buy_price)

    def __str__(self):
        profit = 0
        if self.is_complete ():
            profit = self.get_profit ()
        return "buy_price=%f, count=%d, loss_price=%f, sell_price=%f, profit=%f" % (self.buy_price, self.count, self.loss_price, self.sell_price, profit)

class MarketInfo(object):
    '''开仓信息'''
    def __init__(self, n, unit):
        self.n = n
        self.unit = unit

class Account(object):
    '''交易账号'''
    def __init__(self, total_assets):
        self.total_assets = total_assets
        self.current_assets = total_assets
        self.position_dict = {}
        self.market = {}
        self.trade_history_list = []

    def set_market_info(self, code, n, unit):
        self.market[code] = MarketInfo(n, unit)

    def n_value(self, code):
        return self.market[code].n

    def unit_value(self, code):
        return self.market[code].unit

    def buy(self, date, code, price, count):
        self.trade_history_list.append (TradeRecord (date, code, price, count, 1))
        self.current_assets -= (price * count)
        info = self.market[code]
        if code not in self.position_dict:
            # 新开仓
            self.position_dict[code] = [TurtleTradeNode(price, count, price - 2*info.n)]
            print "buy, date=%s, price=%f, count=%d, loss_price=%f" % (date, price, count, price - 2*info.n)
            return
        # 加仓
        # 前面仓位止损价格提高n/2
        for item in self.position_dict[code]:
            item.loss_price += (info.n/2)
            print "incr loss_price:", item.buy_price, item.loss_price
        self.position_dict[code].append (TurtleTradeNode(price, count, price - 2*info.n))
        print "buy, date=%s, price=%f, count=%d, loss_price=%f" % (date, price, count, price - 2*info.n)

    def sell(self, code, date, node, price):
        self.trade_history_list.append (TradeRecord (date, code, price, node.count, -1))
        node.sell (price)
        self.current_assets += (node.count * price)
        print "sell, date=%s, price=%f, count=%d, profit=%f" % (date, price, node.count, node.get_profit())

    def sell_all (self, date, code, price):
        for trade in self.position_dict[code]:
            if not trade.is_complete ():
                self.sell (code, date, trade, price)
        print "sell all positions:", date, code, price

    def has_position(self, code):
        if code not in self.position_dict:
            return False
        for trade in self.position_dict[code]:
            if not trade.is_complete ():
                return True
        return False

    def last_buyin_price(self, code):
        return self.position_dict[code][-1].buy_price

    def first_buyin_price(self, code):
        return self.position_dict[code][0].buy_price

    def get_trade_profit(self, code):
        if code not in self.position_dict:
            return 0
        total = 0
        for trade in self.position_dict[code]:
            total += trade.get_profit ()
        return total

    def clear(self):
        self.position_dict = {}
        self.market = {}
        self.trade_history_list = []

    def print_assets(self):
        print "Account Summary:"
        print "Assets:", self.current_assets
        print "Trade Record:"
        for code, record in self.position_dict.items ():
            for item in record:
                print item
        print "Trade History:"
        for trade in self.trade_history_list:
            print trade
        print "-" * 50
