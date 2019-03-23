import pandas as pd
import numpy as np
import random
import datetime
import Agent
import Orders
import xlsxwriter

# 市场结构
class Market:
    marketPrice = 0
    fundamentalPrice = 0
    LFTnum = 0
    HFTnum = 0
    ChartTraders = {}
    # Chartnum = 0
    FundTraders = {}
    # Fundnum = 0
    HTraders = {}
    # total sell quantity
    # total buy quantity
    sellquantity = 0
    buyquantity = 0

    # 手续费
    tax = 0
    # TODO :fee of cancel

    # 历史记录
    RecordList = {}

    #初始化市场结构
    def __init__(self, RecordList, LFTnum, HFTnum, ChartTraders, FundTraders, HTraders):
        self.RecordList = RecordList
        self.LFTnum = LFTnum
        self.HFTnum = HFTnum
        self.ChartTraders = ChartTraders
        self.FundTraders = FundTraders
        self.HTraders = HTraders
        # 指令簿,用于订单匹配计算
        self.AskList = pd.DataFrame(columns=['price', 'time', 'traderType', 'traderId', 'quantity', 'suspendTime'])
        self.BidList = pd.DataFrame(columns=['price', 'time', 'traderType', 'traderId', 'quantity', 'suspendTime'])
        self.time = 0
        self.askOrders = 0
        self.bidOrders = 0
        #self.writer = pd.ExcelWriter("./MarketRecords.xlsx", engine='xlsxwriter')

    # 初始化交易者
    def initTraders(self, ChartTraders, FundTraders, HTraders, time):
        # 低频交易者
        lownum = self.LFTnum
        initstock = 100
        initcash = 10000
        LowLatencyFactor = np.random.randint(10, 40, [1, lownum])  # numpy.ndarray
        chartnum = random.randint(0, lownum)
        fundnum = lownum - chartnum
        # df1 = pd.DataFrame({'Time': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 'LFT-Num': [self.LFTnum],
        #                     'HFT-Num': [self.HFTnum], 'Round': [time], 'Chart-Num': [chartnum], 'Fund-Num': [fundnum]})
        # print(df1)
        # df1.to_excel(self.writer, sheet_name='MarketMessage')
        ChartEpsilon = np.random.normal(0, 1, [1, chartnum])
        FundamentalEpsilon = np.random.normal(0, 0.5, [1, lownum - chartnum])
        PriceEps = np.random.normal(0, 0.01, [1, lownum])
        # df21 = pd.DataFrame(LowLatencyFactor.T, columns=['LatencyFactor'])
        # df22 = pd.DataFrame(ChartEpsilon.T, columns=['ChartEps'])
        # df23 = pd.DataFrame(FundamentalEpsilon.T, columns=['FundEps'])
        # df24 = pd.DataFrame(PriceEps.T, columns=['PriceEps'])
        # df2 = pd.concat([df21, df22, df23, df24], axis=1)
        # df2.to_excel(self.writer, sheet_name="LowTradersMessage")
        print("The chart num is ", chartnum)
        for chart in range(0, chartnum):
            # 初始化图表交易者
            ChartTraders['low' + str(chart)] = Agent.LTrader(chart, 'c', random.randint(1, initstock),
                                                       random.randint(1, initcash), LowLatencyFactor[0][chart], 20,
                                                       ChartEpsilon[0][chart], PriceEps[0][chart])
        for fund in range(chartnum, lownum):
            # 初始化基本面交易者
            FundTraders['low' + str(fund)] = Agent.LTrader(fund, 'f', random.randint(1, initstock),
                                                     random.randint(1, initcash), LowLatencyFactor[0][fund], 20,
                                                     FundamentalEpsilon[0][fund - chartnum], PriceEps[0][fund])
        # 高频交易者
        threshold = np.random.uniform(0, 0.01, [1, self.HFTnum])  # 激活因子
        priceDis = np.random.uniform(0, 0.01, [1, self.HFTnum])  # 价格波动
        # df31 = pd.DataFrame(threshold.T, columns=['Threshold'])
        # df32 = pd.DataFrame(priceDis.T, columns=['PriceDis'])
        # df3 = pd.concat([df31, df32], axis=1)
        # df3.to_excel(self.writer, sheet_name='HighTradersMessage')
        # self.writer.save()

        print('The high frequancy num is: ', self.HFTnum)
        for hf in range(0, self.HFTnum):
            HTraders['high' + str(hf)] = Agent.HTrader(hf, random.randint(1, initstock), random.randint(1, initcash), 1,
                                                 threshold[0][hf], priceDis[0][hf])
        # print(HTraders)

    # 交易准备
    def preOrders(self):
        self.AskList['suspendTime'] -= 1
        self.BidList['suspendTime'] -= 1
        for c in self.ChartTraders.values():
            order = c.generateOrder(self)
            if order == None:
                continue
            if order.direction == 0:
                self.AskList.loc[self.askOrders] = [order.price, order.time, order.traderType, order.traderId,order.quantity, order.suspendTime]
                self.askOrders += 1
            else:
                self.BidList.loc[self.bidOrders] = [order.price, order.time, order.traderType, order.traderId,order.quantity, order.suspendTime]
                self.bidOrders += 1
            # break   #debug
        for f in self.FundTraders.values():
            order = f.generateOrder(self)
            if order == None:
                continue
            if order.direction == 0:
                self.AskList.loc[self.askOrders] = [order.price, order.time, order.traderType, order.traderId,order.quantity, order.suspendTime]
                self.askOrders += 1
            else:
                self.BidList.loc[self.bidOrders] = [order.price, order.time, order.traderType, order.traderId,order.quantity, order.suspendTime]
                self.bidOrders += 1
            # break   #debug
            # self.HFTpreOrders()
        for hf in self.HTraders.values():
            order = hf.generateOrder(self)
            if order == None:
                continue
            if order.direction == 0:
                self.AskList.loc[self.askOrders] = [order.price, order.time, order.traderType, order.traderId,
                                                    order.quantity, order.suspendTime]
                self.askOrders += 1
            else:
                self.BidList.loc[self.bidOrders] = [order.price, order.time, order.traderType, order.traderId,
                                                    order.quantity, order.suspendTime]
                self.bidOrders += 1
            # break   #debug
        self.time += 1

    def HFTpreOrders(self):
        for hf in self.HTraders.values():
            order = hf.generateOrder(self)
            if order == None:
                continue
            if order.direction == 0:
                self.AskList.loc[self.askOrders] = [order.price, order.time, order.traderType, order.traderId,
                                                    order.quantity, order.suspendTime]
                self.askOrders += 1
            else:
                self.BidList.loc[self.bidOrders] = [order.price, order.time, order.traderType, order.traderId,
                                                    order.quantity, order.suspendTime]
                self.bidOrders += 1
            # break   #debug

    # 报价单生成
    def genMarketQuotes(self):
        print('A round begin! ')
        self.AskList = self.AskList.sort_values(['price', 'time'], ascending=False)
        self.BidList = self.BidList.sort_values(['price', 'time'])
        for bid in self.BidList.iterrows():
            if bid[1][5] <= 0:
                self.cancelOrder(bid)
                self.BidList = self.BidList.drop(bid[0])
        for ask in self.AskList.iterrows():
            if ask[1][5] <= 0:
                self.cancelOrder(ask)
                self.AskList = self.AskList.drop(ask[0])
        print('AskList\n',self.AskList)
        print('BidList\n',self.BidList)

    # 市场订单生成函数
    def genMarketDeals(self):
        deals = []
        if len(self.AskList) == 0:
            return deals
        elif len(self.BidList) == 0:
            return deals
        for ask in self.AskList.iterrows():
            for bid in self.BidList.iterrows():
                # print('AskList\n',self.AskList)
                # print('BidList\n',self.BidList)
                # print(ask[1][0])
                if ask[1][0] >= bid[1][0]:
                    # 成交，加入到历史记录中
                    price = (ask[1][0] + bid[1][0]) / 2
                    quantity = min(ask[1][4], bid[1][4])
                    deal = Orders.Deal(ask[1][3], bid[1][3], quantity, price,self.time)
                    deals.append(deal)
                    # print('The price of this deal is :',price)
                    # 订单变化，交易者财富更新
                    self.updateWealth(ask, bid, quantity)
                    if ask[1][4] > bid[1][4]:
                        self.cancelOrder(bid)  # 撤单，订单消失的交易者的suspend返回为原来的常数
                        self.BidList = self.BidList.drop(bid[0])
                        rest = ask[1][4] - quantity
                        self.AskList.loc[ask[0], 'quantity'] = rest
                        # print('AskList\n',self.AskList)
                        # print('BidList\n',self.BidList)
                        continue
                    elif ask[1][4] < bid[1][4]:
                        self.cancelOrder(ask)
                        self.AskList = self.AskList.drop(ask[0])
                        rest = bid[1][4] - quantity
                        self.BidList.loc[bid[0], 'quantity'] = rest
                        break
                    else:
                        self.cancelOrder(ask)
                        self.cancelOrder(bid)
                        self.BidList = self.BidList.drop(bid[0])
                        self.AskList = self.AskList.drop(ask[0])
                        break
                else:
                    print('No more deals! \n')
                    return deals
            continue
        return deals

    # 撤单操作，在用户处更新信息
    def cancelOrder(self, order):
        if order[1][2] == 'c':
            self.ChartTraders[order[1][3]].suspendTime = 20
        elif order[1][2] == 'f':
            self.FundTraders[order[1][3]].suspendTime = 20
            # 高频一轮以后订单自动取消，不需要考虑撤单的问题

    # 交易者财富更新
    def updateWealth(self, ask, bid, quantity):
        price = (ask[1][0] + bid[1][0]) / 2
        if ask[1][2] == 'c':
            self.ChartTraders[ask[1][3]].cash = + price * quantity
            self.ChartTraders[ask[1][3]].stock = - quantity
        elif ask[1][2] == 'f':
            self.FundTraders[ask[1][3]].cash = + price * quantity
            self.FundTraders[ask[1][3]].stock = - quantity
        elif ask[1][2] == 'h':
            self.HTraders[ask[1][3]].cash = + price * quantity
            self.HTraders[ask[1][3]].stock = - quantity
        if bid[1][2] == 'c':
            self.ChartTraders[bid[1][3]].stock = + quantity
            self.ChartTraders[bid[1][3]].cash = - price * quantity
        elif bid[1][2] == 'f':
            self.FundTraders[bid[1][3]].stock = + quantity
            self.FundTraders[bid[1][3]].cahs = - price * quantity
        elif bid[1][2] == 'hf':
            self.HTraders[ask[1][3]].stock = + quantity
            self.HTraders[ask[1][3]].cash = - price * quantity
        return

    # 市场价格生成函数
    def genMarketPrice(self, deals):
        t = self.time-1
        if len(deals) == 0:
            print('There is no deals in this round!')
            self.RecordList[t] = [self.RecordList[t - 1][0], self.RecordList[t - 1][1], []]
            return (self.RecordList[t - 1][0])
        else:
            price = 0
            records = []
            for deal in deals:
                price += deal.price
                # print(t,deal.sellerName,deal.buyerName,deal.quantity,deal.price)
                records.append([deal.sellerName, deal.buyerName, deal.quantity, deal.price])
            price = price / len(deals)
            print("The market price of this round is ", price)
            self.RecordList[t] = [price, self.RecordList[t - 1][1], records]
            return price

    # 统计信息
    def mes(self, direction):
        temp = 0
        if direction == 1:
            for ask in self.AskList.iterrows():
                temp = + ask[1][4]
            temp = temp / len(self.AskList)
        else:
            for bid in self.BidList.iterrows():
                temp = + bid[1][4]
            temp = temp / len(self.BidList)
        return temp

    # 参与者数量转化函数
    def genTraders(self, ):
        return