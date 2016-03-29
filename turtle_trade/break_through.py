# coding: utf-8

class BreakThrough(object):
    def __init__(self, buy_price, loss_price):
        self.buy_price = buy_price
        self.loss_price = loss_price
        self.complete_price = 0

    def complete(self, price):
        self.complete_price = price

    def is_complete(self):
        return self.complete_price > 0

    def is_profitable(self):
        return self.is_complete() and (self.complete_price > self.buy_price)
