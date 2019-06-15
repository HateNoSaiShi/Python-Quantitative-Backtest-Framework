# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 12:07:09 2018

@author: HateNoSaishi
"""

'''
数据库接口
'''


import pymssql
import datetime
import decimal
from pandas import DataFrame

class SqlServerInterface(object):
    '''
    Attributes:
  
    '''
      
#=====
    
    def __init__(self, host = '127.0.0.1', username = 'username', 
                       password = 'pasw', default_database = 'database'):
        self.SetHost(host)
        self.SetUsername(username)
        self.SetPassword(password)
        self.SetDatabase(default_database)
        self.SqlConnect()

#=====
        
    def __del__(self):
        #向服务器提交数据
        self.connect.commit() 
        #关闭光标
        self.cur.close() 
        #断开连接
        self.connect.close()
        
#=====
    
    def SetHost(self, host):
        '''
        type(host) = string
        '''
        self.host = host
        
#=====
        
    def SetUsername(self, username):
        '''
        type(username) = string
        '''
        self.username = username
        
#=====
    
    def SetPassword(self, password):
        '''
        type(password) = string
        '''
        self.password = password
    
#=====
    
    def SetDatabase(self, database):
        '''
        type(database) = string
        '''
        self.database = database
        
#=====
        
    def SqlConnect(self):
        #登陆
        self.connect = pymssql.connect(
                        host = self.host, 
                        user = self.username, 
                        password = self.password,
                        database = self.database)
        #启动模拟光标
        self.cur=self.connect.cursor()
        
#=====
        
    def ChangeDatabase(self, new_database):
        temp_exe = """use %s""" % new_database
        self.cur.execute(temp_exe)

#=====
        
    def GetFromDatabase(self, table_name, windcode, data_name, start_time, end_time):
        '''
        从数据库中获取数据
        type(windcode) = string
        type(data_name) = string(单个数据) or list(多个数据),不包含date
        start_time\end_time类型要求满足pymssql接口需求即可
        '''
        
        query_exe = """select date,""" #查询语句
        if type(data_name) == type(''):
            query_exe += """[""" + data_name + """]"""
            data_name = [data_name]
        else:
            for item in data_name[:-1]:
                query_exe += """[""" + item + """],"""
            query_exe += """[""" + data_name[-1] +"""]"""
        query_exe += """ from """ + table_name + """ where windcode = '""" + windcode + """' and"""
        query_exe += """ date >= '""" + start_time + """'""" + """ and"""
        query_exe += """ date <= '""" + end_time + """'""" + """ order by date"""
 
        self.cur.execute(query_exe)
        temp_data = self.cur.fetchall()
        check_type = type(decimal.Decimal(0))
        for i in range(len(temp_data)):
            temp_data[i] = list(temp_data[i])
            for j in range(len(temp_data[i])):
                if type(temp_data[i][j]) == check_type:
                    temp_data[i][j] = float(temp_data[i][j])
        
        data = DataFrame(temp_data)
        date = data[0]
        data = DataFrame(data.loc[:,1:])
        data.columns = data_name
        date = [str(i) for i in date]
        if ':' not in date[0]:
            date = [i + ' 00:00:00' for i in date]
        date = [datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in date]
            
        data.index = date

        return data
    
#============

if __name__ == '__main__':
    """
    DEMO
    """
    sql_interface = SqlServerInterface()
    df = sql_interface.GetFromDatabase('t_future_data_day', 'IH00.CFE', ['close','open'], '20150901', '20180101')
    del sql_interface
        