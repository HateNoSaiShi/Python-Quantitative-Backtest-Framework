# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 13:28:54 2018

@author: HateNoSaishi
"""

from pandas import DataFrame
import numpy as np

class StatisticContainer(object):
    
    '''
    储存一只个股特定频率下的行情数据
    '''

#=====
   
    def __init__(self, sql_interface, windcode):
        '''
        sql_interface : SqlServerInterface的实例
        '''
        self.sql_interface = sql_interface
        self.windcode = windcode
        self.market_data = {}

#=====
        
    def AddData(self, table_name, data_name, start_time, end_time, frequence):
        '''
        参数与SqlServeInterface.GetFromDataBase一致
        '''
        self.market_data[frequence] = self.sql_interface.GetFromDatabase(table_name, self.windcode, data_name, start_time, end_time)
        
#=====
        
    def GetData(self, windcode, frequence, date, data_name):
        '''
        获取特定频率下的特定时间数据
        '''
        return self.market_data[frequence][data_name][date]
    
#=====
        
    def Apply(self, frequence, row_to_use, new_row_name_list, func, *args):
        #TODO->
        pass

#=====
            
    @staticmethod
    def CalculatePercentChange(df, row_to_use):
        #TODO->
        pass
    

#==============
if __name__ == '__main__':
    '''
    DEMO
    '''
    import myBacktest
    sql_interface = myBacktest.SqlHandler.SqlServerInterface()
    container = StatisticContainer(sql_interface, '000985.CSI')
    container.AddData('index_date_day', ['close', 'low', 'pct_chg_b'], '20100101', '20180101', 'day')
    #container.Apply('day', ['close'], ['pct'], StatisticContainer.CalculatePercentChange)