# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 17:06:07 2019

@author: HateNoSaishi
"""

class Account(object):
    
    '''
    模拟账户
    '''
    
#=====
    
    def __init__(self, exchange):
        '''
        unsellable = {'000001.SH':{'amount':10000, 'type': 'stock'},}
        '''
        self.cash = 100000000000
        self.unsellable = {}
        self.record = []
        self.max_drawback = 0
        self.exchange = exchange
        self.sellable = {}
        self.trade_log = []
        self.transaction_fee = {'buy':{}, 'sell':{}}
        self.date_list = []
        self.holding_asset_list = []
#=====
        
    def SetInitialCash(self, cash):
        self.cash = cash
        
#=====
        
    def SetInitialAsset(self, asset):
        self.sellable = asset
        
#=====
    
    def SetStockTransactionFee(self, buy_fee, sell_fee):
        self.transaction_fee['buy']['stock'] = buy_fee
        self.transaction_fee['sell']['stock'] = sell_fee

#=====
        
    def SetOptionTransactionFee(self, buy_fee, sell_fee):
        self.transaction_fee['buy']['option'] = buy_fee
        self.transaction_fee['sell']['option'] = sell_fee
        
#=====
        
    def SetFutureTransactionFee(self, buy_fee, sell_fee):
        self.transaction_fee['buy']['future'] = buy_fee
        self.transaction_fee['sell']['future'] = sell_fee
        
#=====
    
    def SetEtfTransactionFee(self, buy_fee, sell_fee):
        self.transaction_fee['buy']['etf'] = buy_fee
        self.transaction_fee['sell']['etf'] = sell_fee
        
#=====
        
    def CalculateNetValue(self, frequence, price_type = 'close', **kwargs):
        '''
        计算调用函数时账户的净值
        '''
        value  = self.cash
        
        '''当日可卖出资产'''
        for windcode in self.sellable.keys():
            #print(windcode)
            temp_amount = self.sellable[windcode]['amount']
            if price_type == 'close':
                temp_price = self.exchange.GetClosePrice(windcode, frequence)
            elif price_type == 'open':
                temp_price = self.exchange.GetOpenPrice(windcode, frequence)
            elif price_type == 'given':
                temp_price = kwargs['price']
            else:
                raise KeyError('Invalid Price Type')
            value += temp_amount * temp_price
        
        '''当日不可卖出资产'''
        for windcode in self.unsellable.keys():
            #print(windcode)
            temp_amount = self.sellable[windcode]['amount']
            if price_type == 'close':
                temp_price = self.exchange.GetClosePrice(windcode, frequence)
            elif price_type == 'open':
                temp_price = self.exchange.GetOpenPrice(windcode, frequence)
            elif price_type == 'given':
                temp_price = kwargs['price']
            else:
                raise KeyError('Invalid Price Type')
            value += temp_amount * temp_price        
    
        return value
    
#=====
        
    def Initialize(self, frequence):
        '''
        账户初始化
        '''
        self.record.append(self.CalculateNetValue(frequence))
        self.date_list.append(self.exchange.date)
        self.holding_asset_list.append((self.exchange.date,{}))
        
#=====
      
    def CalculateMaxDrawback(self):
        '''
        计算最大回撤，每个交易日结算当日净值后调用
        '''
        try:
            #current_drawback = self.record[-1] / max(self.record) - 1
            current_drawback = self.record[-1] - max(self.record)
        except:
            current_drawback = 0
        if current_drawback < self.max_drawback:
            self.max_drawback = current_drawback
            
#=====
            
    def GetProfit(self):
        '''
        获取收益率
        '''
        return self.net[-1] / self.net[0] - 1
    
#=====
        
    def GetMaxDrawback(self):
        '''
        获取最大回撤
        '''
        return self.max_drawback
    
#=====
        
    def GetSharpe(self, benchmark_profit = 0):
        '''
        回测结束后使用，返回夏普比率
        '''
        annulize_excess = (self.GetProfit() - benchmark_profit) / len(self.net) * 252
        pct = [self.record[i] / self.record[i - 1] - 1 for i in range(1, len(self.record))]
        mean_pct = sum(pct) / len(pct)
        pct = [(i - mean_pct) ** 2 for  i in pct]
        daily_std = sum(pct) / len(pct) ** (1 / 2)
        annulize_std = daily_std * (252 ** (1 / 2))
        return annulize_excess / annulize_std
    
#=====
    
    def OneDayOver(self, frequence):
        '''
        结算函数
        '''
        
        #调整可卖出标的的清单
        for windcode in self.unsellable.keys():
            if windcode in self.sellable.keys():
                self.sellable[windcode]['amount'] += self.unsellable[windcode]['amount']
            else:
                self.sellable[windcode] = self.unsellable[windcode]
        self.unsellable = {}
        self.record.append(self.CalculateNetValue(frequence))
        self.date_list.append(self.exchange.date)
        self.CalculateMaxDrawback()
        
        temp_dic = {}
        for windcode in self.sellable.keys():
            if windcode in temp_dic.keys():
                temp_dic[windcode] += self.sellable[windcode]['amount']
            else:
                temp_dic[windcode] = self.sellable[windcode]['amount']
        
        for windcode in self.unsellable.keys():
            if windcode in temp_dic.keys():
                temp_dic[windcode] += self.sellable[windcode]['amount']
            else:
                temp_dic[windcode] = self.sellable[windcode]['amount']
                    
        
        self.holding_asset_list.append((self.exchange.date, temp_dic))
        
#=====
        
    def DeleteSold(self):
        '''
        移除持有数量为0的资产
        '''
        delete = []
        for windcode in self.sellable.keys():
            if self.sellable[windcode]['amount'] == 0:
                delete.append(windcode)
        for windcode in delete:
            del(self.sellable[windcode])
            
#=====
    
    def BuyByShare(self, windcode, frequence, share, underlier_type, price_type = 'close', **kwargs):
        '''
        按数量买
        '''
        
        if price_type == 'close':
            price = self.exchange.GetClosePrice(windcode, frequence)
        elif price_type == 'open':
            price = self.exchange.GetOpenPrice(windcode, frequence)
        elif price_type == 'given':
            price = kwargs['price']
        
        if underlier_type == 'option':
            title_num = share / 10000
            cost = price * share + title_num * self.transaction_fee['buy'][underlier_type]
        else:
            transaction_ratio = self.transaction_fee['buy'][underlier_type]
            cost = price * share * (1 + transaction_ratio)
        self.cash -= cost
        self.trade_log.append((self.exchange.date, windcode, 'long', cost, share))
        if underlier_type == 'stock' or underlier_type == 'etf':
            if windcode in self.sellable.keys():
                self.sellable[windcode]['amount'] += share
            else:
                self.unsellable[windcode] = {'amount': share, 'type': underlier_type}
        else:
            if windcode in self.sellable.keys():
                self.sellable[windcode]['amount'] += share
            else:
                self.sellable[windcode] = {'amount': share, 'type': underlier_type}
#=====
            
    """def BuyByShare1(self, windcode, frequence, share, underlier_type, price_type = 'close', **kwargs):
        '''
        按数量买
        '''
        if price_type == 'close':
            price = self.exchange.GetClosePrice(windcode, frequence)
        elif price_type == 'open':
            price = self.exchange.GetOpenPrice(windcode, frequence)
        elif price_type == 'given':
            price = kwargs['price']
        transaction_ratio = self.transaction_fee['buy'][underlier_type]
        cost = (1 + transaction_ratio) * price * share
        
        if self.cash < cost:
            print('账户现金不足，无法购买')
        else:
            self.cash -= cost
            self.trade_log.append(self.exchange.date, windcode, 'long', (1+ transaction_ratio) * price, share)
            if underlier_type == 'stock' or underlier_type == 'etf':
                if windcode in self.sellable.keys():
                    self.sellable[windcode] += share
                else:
                    self.unsellable[windcode] = share
            else:
                if windcode in self.sellable.keys():
                    self.sellable[windcode] += share
                else:
                    self.sellable[windcode] = share"""
                        
#=====
                    
    def BuyByPropotion(self, windcode, frequence, propotion, underlier_type, price_type = 'close', **kwargs):
        '''
        按占当前现金的比例买
        '''
        if price_type == 'close':
            price = self.exchange.GetClosePrice(windcode, frequence)
        elif price_type == 'open':
            price = self.exchange.GetOpenPrice(windcode, frequence)
        elif price_type == 'given':
            price = kwargs['price']
        transaction_cost = self.transaction_fee['buy'][underlier_type]
        usable_cash = self.cash / (1 + transaction_cost) * propotion
        to_buy_share = int(usable_cash / price)
        self.BuyByShare(windcode, frequence, to_buy_share, underlier_type, price_type, **kwargs)
        
#=====
        
    def BuyByMoney(self, windcode, frequence, money, underlier_type, price_type = 'close', **kwargs):
        '''
        买入固定金额
        '''
        propotion = money / self.cash
        self.BuyByPropotion(windcode, frequence, propotion, underlier_type, price_type, **kwargs)

#=====
      
    def SellByShare(self, windcode, frequence, share, underlier_type, price_type = 'close', **kwargs):
        '''
        卖出固定数量
        '''
        
        if price_type == 'close':
            price = self.exchange.GetClosePrice(windcode, frequence)
        elif price_type == 'open':
            price = self.exchange.GetOpenPrice(windcode, frequence)
        elif price_type == 'given':
            price = kwargs['price']
        
        if underlier_type == 'option':
            title_num = share / 10000
            if 'sell_open' in kwargs.keys():
                transaction_fee = 0
            else:
                transaction_fee = self.transaction_fee['buy'][underlier_type]
            cash_add = price * share - title_num * transaction_fee
        else:
            transaction_ratio = self.transaction_fee['sell'][underlier_type]
            cash_add = price * share * (1 - transaction_ratio)
        self.cash += cash_add
        self.trade_log.append((self.exchange.date, windcode, 'short', cash_add, share))
        if windcode in self.sellable.keys():
            self.sellable[windcode]['amount'] -= share
        else:
            self.sellable[windcode] = {'amount': -share, 'type': underlier_type}
        self.DeleteSold()
        
        
#=====
        
    """def SellByShare1(self, windcode, frequence, share, underlier_type, price_type = 'close', **kwargs):
        '''
        卖出固定数量
        '''
        if windcode not in self.sellable.keys() and underlier_type == 'stock':
            print('未持有该资产，无法卖出')
        elif self.sellable[windcode]['amount'] < share and underlier_type == 'stock':
            print('数量不足，无法卖出')
        else:
            if price_type == 'close':
                price = self.exchange.GetClosePrice(windcode, frequence)
            elif price_type == 'open':
                price = self.exchange.GetOpenPrice(windcode, frequence)
            elif price_type == 'given':
                price = kwargs['price']
            transaction_ratio = self.transaction_fee['sell'][underlier_type]
            cash_add = price * share * (1 - transaction_ratio)
            self.cash += cash_add
            self.trade_log.append(self.exchange.date, windcode, 'short', (1+ transaction_ratio) * price, share)
            self.sellable[windcode]['amount'] -= share
        self.DeleteSold()"""

#=====
    
    def ClosePosition(self, windcode, frequence, underlier_type, price_type = 'close', **kwargs):
        if underlier_type == 'stock' or underlier_type == 'etf':
            if windcode not in self.sellable.keys():
                print('未持有，无法平仓')
            else:
                to_sell_share = self.sellable[windcode]['amount']
                if to_sell_share > 0:
                    self.SellByShare(windcode, frequence, to_sell_share, underlier_type, price_type, **kwargs)
                elif to_sell_share < 0:
                    self.BuyByShare(windcode, frequence, -to_sell_share, underlier_type, price_type, **kwargs)
                else:
                    print('无需平仓')
                    pass
        else:
            if windcode not in self.sellable.keys():
                print('未持有，无法平仓')
            elif self.sellable[windcode]['amount'] == 0:
                print('未持有，无法平仓')
            elif self.sellable[windcode]['amount'] > 0:
                self.SellByShare(windcode, frequence, self.sellable[windcode]['amount'], underlier_type, price_type, **kwargs)
            else:
                self.BuyByShare(windcode, frequence, -self.sellable[windcode]['amount'], underlier_type, price_type, **kwargs)
        self.DeleteSold()
        
#=====
        
    
    