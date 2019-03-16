import Market
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
# Part 1: Initialization
    #ToDo : input the parameter
    RecordList = {-2:[100,102,[]],-1:[101,102,[]]}
    time = 10
    market = Market.Market(RecordList,10,5,{},{},{})   #initialize market :RecordList,LFTnum,HFTnum,Chart,Fund,HFT
    market.initTraders(market.ChartTraders,market.FundTraders,market.HTraders,time)  #initialize traders
    prices = []
# Part 2: Rounds of trade
    #writer = pd.ExcelWriter("F:/南京大学(备份)/创新项目/开始正经干活啦/Ask-Bid.xlsx",engine = 'xlsxwriter')
    for t in range(0,time):
        # gen orders,现在加入搞屁还要靠手动调整代码
        market.preOrders()
        # gen market price
        market.genMarketQuotes()
        # temp_round = 'Round' + str(market.time)
        # market.AskList.to_excel(writer,sheet_name = temp_round )
        # market.BidList.to_excel(writer,sheet_name = temp_round,startcol = 8)
        deals = market.genMarketDeals()
        prices.append(market.genMarketPrice(deals))
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
