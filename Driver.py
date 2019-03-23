import Market
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from pandas.io import sql

if __name__ == '__main__':
# Part 1: Initialization
    # ToDo : input the parameter
    RecordList = {-2:[100,102,[]],-1:[101,102,[]]}
    time = 10
    #Hflag = input("本次实验是否加入高频参与者？（加入输入True, 否则输入False）")
    market = Market.Market(RecordList,50,5,{},{},{})   #initialize market :RecordList,LFTnum,HFTnum,Chart,Fund,HFT
    market.initTraders(market.ChartTraders,market.FundTraders,market.HTraders,time)  #initialize traders
    prices = []
# Part 1.1: Create the Database
    database = sqlite3.connect('Market.db')
#     database.execute('''CREATE TABLE AskList
#     (PRICE REAL NOT NULL,
#     TIME REAL NOT NULL,
#     AGENTYPE CHAR(10) NOT NULL,
#     AGENTID CHAR(50) NOT NULL,
#     QUANTITY REAL NOT NULL);''')
#     database.execute('''CREATE TABLE BidList
#     (PRICE REAL NOT NULL,
#     TIME REAL NOT NULL,
#     AGENTYPE CHAR(10) NOT NULL,
#     AGENTID CHAR(50) NOT NULL,
#     QUANTITY REAL NOT NULL);''')
#     database.execute('''CREATE TABLE Deals
#     (TIME TEXT NULL,
#     ASKTYEP CHAR(50) NOT NULL,
#     BIDTPE CHAR(50) NOT NULL,
#     PRICE REAL NOT NULL,
#     QUANTITY REAL NOT NULL);''')
# Part 2: Rounds of trade
    for t in range(0,time):
        # gen orders,现在加入高频还要靠手动调整代码
        market.preOrders()
        # gen market price
        market.genMarketQuotes()
        market.AskList.to_sql('AskList',con=database,if_exists='append',index=False)
        market.BidList.to_sql('BidList', con=database, if_exists='append', index=False)
        # temp_round = 'Round' + str(market.time)
        # market.AskList.to_excel(writer,sheet_name = temp_round )
        # market.BidList.to_excel(writer,sheet_name = temp_round,startcol = 8)
        deals = market.genMarketDeals()
        prices.append(market.genMarketPrice(deals))
        # TODO:装换成Dataframe还有问题
        #deals = pd.DataFrame(deals, columns=["AskId", "BidId", "Quantity", "Price","Time"])
        #deals.to_sql('Deals',con=database,if_exists='append',index=False)
        market.time = t + 1
        print(market.time)
    #print(market.RecordList)
    plt.plot(range(0,time),prices)
    plt.xlabel('Time')
    plt.ylabel('Market Price')
    plt.show()
    # market.writer.close()


#==============================================================================
#     for t in range(0,1200):
#
#     print(LowLatencyFactor[0][1])                           #调用方法
#     ChartEpsilon = np.random.normal(0,0.05,[1,10000])
#     FundamentalEpsilon = np.random.normal(0,0.01,[1,10000]) #生成相关的随机数
#==============================================================================
