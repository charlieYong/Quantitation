#!/usr/bin/env python
# conding: utf-8

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

class PositionDetail(object):
    '''仓位明细'''
    def __init__(self, price, count, loss_price):
        self.buy_price = price
        self.count = count
        self.loss_price = loss_price

class MakgetInfo(object):
    '''开仓信息'''
    def __init__(self, n, unit):
        self.n = n
        self.unit = unit

class Account(object):
    '''交易账号'''
    def __init__(self, total_assets):
        self.total_assets = total_assets
        self.current_asset = total_assets
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
            self.position_dict[code] = [PositionDetail (price, count, price - 2*info.n)]
            return
        # 加仓
        # 前面仓位止损价格提高n/2
        for item in self.position_dict[code]:
            item.loss_price += (info.n/2)
        self.position_dict[code].append (PositionDetail (price, count, price - 2*info.n))

    def sell(self, date, code, price, count):
        self.trade_history_list.append (TradeRecord (date, code, price, count, -1))
        record = None
        for item in self.position_dict[code]:
            if item.count == count:
                record = item
                break
        if record is None:
            print "cannot find buy in record on sell"
            return
        self.current_assets += (price * count)
        self.position_dict[code].remove (record)
        if len (self.position_dict[code]) <= 0:
            del self.position_dict[code]

    def sell_all (self, date, code, price):
        for position in self.position_dict[code]:
            self.sell (date, code, price, position.count)

    def has_position(self, code):
        return code in self.position_dict

    def position_detail_list(self, code):
        return self.position_dict[code]

    def last_buyin_price(self, code):
        return self.position_dict[code][-1].price

    def print_assets(self):
        print "Account Summary:"
        print "Assets:", self.current_assets
        for record in self.position_dict:
            for item in record:
                print "Position:", code, count


