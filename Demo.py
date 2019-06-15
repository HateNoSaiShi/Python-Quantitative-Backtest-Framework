# -*- coding: utf-8 -*-
"""
Created on Mon May 13 08:42:51 2019

@author: HateNoSaishi
"""

import myBacktest

def Demo():
    '''
    简单的动量策略
    '''
    
    #将封装好的类逐个实例化
    sql_interface = myBacktest.SqlHandler.SqlServerInterface()
    exchange_database = myBacktest.BizHandler.ExchangeDatabase(sql_interface)
    
    #添加可能交易到的标的
    exchange_database.AddUnderlier('510050.SH')
    exchange_database.AddData('t_ETF_data_day', '510050.SH', ['close', 'open'], '20100101', '20181231', 'day')
    date_list = exchange_database.data['510050.SH'].market_data['day'].index
    
    #模拟账户初始化
    rolling_day_len = 80
    start_date = date_list[rolling_day_len]
    exchange = myBacktest.BizHandler.Exchange(start_date, exchange_database)
    account = myBacktest.AccountHandlerNew.Account(exchange)
    account.SetInitialCash(10000000)
    account.Initialize('day')
    account.SetEtfTransactionFee(0, 0)
    position = 0
    
    #逐日检查交易逻辑，80日收益率为正则买入
    for i in range(rolling_day_len + 1, len(date_list)):
        date = date_list[i]
        account.exchange.SetDate(date)
        yesterday = date_list[i - 1]
        momentum_compare_day = date_list[i - 1 - rolling_day_len]
        yesterday_close = exchange_database.GetData('510050.SH', 'day', 'close', yesterday)
        momentum_compare_close = exchange_database.GetData('510050.SH', 'day', 'close', momentum_compare_day)
        if yesterday_close > momentum_compare_close:
            temp_momentum = 1
        else:
            temp_momentum = -1
        if position == 0:
            if temp_momentum == 1:
                account.BuyByPropotion('510050.SH', 'day', 0.9, 'etf', price_type = 'open')
                position = 1
        if position == 1:
            if temp_momentum == -1:
                account.ClosePosition('510050.SH', 'day', 'etf', price_type = 'open')
                position = 0
        
        #每个交易日结束时调用进行结算
        account.OneDayOver('day')
    
    #打印净值
    print(account.record)
        
        
#=====
if __name__ == '__main__':
    Demo()
    