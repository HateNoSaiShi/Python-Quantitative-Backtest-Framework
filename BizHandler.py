# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:46:36 2018

@author: HateNoSaishi
"""

from myBacktest.StatisticHandler import StatisticContainer

class ExchangeDatabase(object):
    
    '''
    模拟交易所数据库
    '''
    
#=====    
    
    def __init__(self, sql_interface):
        self.data = {}
        self.sql_interface = sql_interface
        
#=====
        
    def AddUnderlier(self, windcode):
        '''
        增加一只标的
        '''
        self.data[windcode] = StatisticContainer(self.sql_interface, windcode)
        
#=====
        
    def AddData(self, table_name, windcode, data_name, start_time, end_time, frequence):
        '''
        增加给定标的的数据
        '''
        self.data[windcode].AddData(table_name, data_name, start_time, end_time, frequence)
        
#=====
        
    def GetData(self, windcode, frequence, data_name, date):
        '''
        获取特定标的给定频率给定时间节点的数据
        '''
        return self.data[windcode].GetData(windcode, frequence, date, data_name)
    
#=====
        
    def Apply(self):
        #TODO->
        pass

#=============
        
class Exchange(object):
    
    '''
    模拟交易所
    '''
    
#=====
    
    def __init__(self, date, database):
        self.SetDate(date)
        self.database = database
        
#=====
        
    def SetDate(self, date):
        self.date = date
        
#=====
        
    def GetData(self, windcode, frequence, data_name, **kwargs):
        if 'date' in kwargs.keys():
            target_date = kwargs['date']
        else:
            target_date = self.date
        return self.database.GetData(windcode, frequence, data_name, target_date)

#=====
        
    def GetClosePrice(self, windcode ,frequence, ** kwargs):
        if 'date' in kwargs.keys():
            target_date = kwargs['date']
        else:
            target_date = self.date
        return self.GetData(windcode, frequence, 'close' , date = target_date)
    
#=====
        
    def GetOpenPrice(self, windcode ,frequence, ** kwargs):
        if 'date' in kwargs.keys():
            target_date = kwargs['date']
        else:
            target_date = self.date
        return self.GetData(windcode, frequence, 'open' , date = target_date)
    
#=====
        
    def GetVolume(self, windcode ,frequence, ** kwargs):
        if 'date' in kwargs.keys():
            target_date = kwargs['date']
        else:
            target_date = self.date
        return self.GetData(windcode, frequence, 'volume' , date = target_date)


#=============
if __name__ == '__main__':
    '''
    DEMO
    '''
    import myBacktest
    sql_interface = myBacktest.SqlHandler.SqlServerInterface()
    exchange_database = ExchangeDatabase(sql_interface)
    exchange_database.AddUnderlier('000985.CSI')
    exchange_database.AddData('index_date_day', '000985.CSI', ['close','open','volume','amt'], '20100101', '20180101', 'day')
    #print(exchange_database.GetData('000985.CSI', 'day', 'close' , '20100104'))
    exchange = Exchange('20100105', exchange_database)
    print(exchange.GetData('000985.CSI','day','close', date = '20100104'))
    print(exchange.GetClosePrice('000985.CSI', 'day', date = '20100104'))
    print(exchange.GetOpenPrice('000985.CSI', 'day', date = '20100104'))
    print(exchange.GetVolume('000985.CSI', 'day', date = '20100104'))
    