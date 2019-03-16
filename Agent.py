import Orders
import random


# 交易者
# 低频LTrader
marketPrice = 0
fundamentalPrice = 0
lfCount = 100
hfCount = 100
BIDLOB = []  # 限价指令簿 全局变量 order的列表，按照价格优先，时间优先排序。
ASKLOB = []
RECORDS = {}  # {time;record}


# 低频交易者
class LTrader:
    traderId = 'low1'  # ID
    traderType = ''  # 目前分两类，'c'表示图表交易者 ‘f’表示基本面交易者
    totalWealth = 0  # 总财富
    stock = 0  # 股票 初始化为[0,10000]随机数
    cash = 0  # 现金 初始化为[0,10000]随机数

    latencyFactor = 0  # 延迟因子，服从[10,40]的均匀分布
    suspendTime = 0  # 订单最短停留的时间，定值

    epsilon = 0
    priceEps = 0
    ownOrders = []  # 交易者在市场中已经提交过的订单历史记录的，Order

    def __init__(self, initialId, initialType, initialStock, initialCash, initialLatencyFactor, initialSuspendTime,
                 initEps, initPriceEps):
        self.traderId = initialId
        self.traderType = initialType
        self.stock = initialStock
        self.cash = initialCash
        self.totalWealth = initialStock * marketPrice + initialCash
        self.latencyFactor = initialLatencyFactor / 25
        self.suspendTime = initialSuspendTime
        self.epsilon = initEps
        self.priceEps = initPriceEps
        self.ownOrders = []

    def generateOrder(self, market):
        time = market.time
        # calculate the  information of order
        order = Orders.Order('low' + str(self.traderId), 0, 0, 0)
        # latency 判断是否参与交易,latency作为影响参与频率的因素，用于确定概率
        pro = random.random()
        if pro > self.latencyFactor:
            # 此次不参与
            # print('\n',self.traderId, "doesn't submit the deal this round! ")
            return
        if self.suspendTime != 20:
            # 市场中已经有订单，此次不会产生新的交易
            return
        # order suspend time
        order.suspendTime = self.suspendTime
        order.traderType = self.traderType
        # order direction
        if self.traderType == 'c':
            alphac = 0.04
            direction = alphac * (market.RecordList[time - 1][0] - market.RecordList[time - 2][0]) + self.epsilon
        else:
            alphaf = 0.05
            Ft = market.RecordList[time - 1][1] * (1 + 0.0001) * (1 + self.epsilon)
            direction = alphaf * (Ft - market.RecordList[time - 1][0]) + self.epsilon
        if direction > 0:
            order.direction = 0
        else:
            order.direction = 1
            # order price
        order.price = market.RecordList[time - 1][0] * (1 + 0.0001) * (1 + self.priceEps)
        # order quantity
        order.quantity = abs(direction)
        # 与财富相关的判断，卖出的股票数不能多于现在持有的股票数，买入花费的现金数不能超过现有的现金
        if order.direction == 1 and order.quantity > self.stock:
            # 卖出
            order.quantity = self.stock
        elif order.direction == 0:
            # 买入
            if order.quantity * order.price > self.cash:
                order.quantity = self.cash / order.price
        # order time
        order.time = market.time + random.uniform(0, 1)
        # print(order.traderId,order.traderType,order.time,order.direction,order.price,order.quantity,order.suspendTime)
        self.ownOrders.append(order)
        self.suspendTime -= 1
        if self.suspendTime <= 0:
            self.suspendTime = 20
        return order

# 高频HTrader
class HTrader:
    traderId = 0
    wealth = 0
    stock = 0
    cash = 0
    latency = 0
    suspendTime = 0
    priceDis = 0

    ownOrders = []  # 交易者在市场中已经提交过的订单历史记录

    def __init__(self, traderId, stock, cash, suspendTime, threshold, priceDis):
        self.id = traderId  # ID
        self.stock = stock  # Stock
        self.cash = cash  # Cash
        self.suspendTime = suspendTime  # TimeScale, refers to the time that an order stay in the order-book before automatic removal
        self.threshold = threshold  # 决定高频交易者是否加入市场，服从min到max的均匀分布
        self.priceDis = priceDis  # 交易者定价的随机因子[kmin,kmax]之间的均匀分布

    # generateOder main function, using the following four functions
    def generateOrder(self, market):
        time = market.time
        # order judge
        temp = (market.RecordList[time - 1][0] - market.RecordList[time - 2][0]) / market.RecordList[time - 2][0]
        # print(temp,self.threshold)
        if temp <= self.threshold:
            # print("This round this HFT doesn't join the market!")
            return  # don't join the market
        order = Orders.Order('high' + str(self.traderId), 0, 0, 0)
        order.traderType = 'h'
        # order direction
        direction = random.random()
        # print('The direction of this trader is :',direction)
        if direction > 0.5:
            order.direction = 0
            best = market.AskList.sort_values(['price', 'time'], ascending=False)[0:1]['price']
        else:
            order.direction = 1
            best = market.BidList.sort_values(['price', 'time'])[0:1]['price']
        # order suspend time,高频的这个值为1，因此只要当前没有匹配成功，就会撤单并在下一轮重新参与，高频参与者每轮都会参与
        order.suspendTime = self.suspendTime
        # order price
        order.price = float(best) * (1 + self.priceDis)
        # !order quantity
        meanParamater = 0.625
        marketQuantity = market.mes(direction)
        order.quantity = marketQuantity * meanParamater * random.random()
        # 持仓限制
        if order.quantity + self.stock > marketQuantity / 4:
            order.quantity = marketQuantity / 4
        # print(order.traderId,order.traderType,order.direction,order.price,order.quantity,order.suspendTime)
        return order

    # 订单方向判断
    def genHFTDirection(self, ):
        direction = True  # true代表买
        return direction

    # 订单价格判断
    def genHFTPrice(self, direction):
        # 限价单的最优额买卖价格时什么？最高买价和最低卖价？
        # 可能需要一个求出市场最优价格的函数？
        return

        # 订单数量判断

    def genHFTQuantity(self, direction):
        quantity = 0
        # 总持仓限制 ? 这里怎么表示
        inventory = quantity + self.stock
        if inventory > 3000:
            quantity = 3000
        if inventory < -3000:
            quantity = -3000

        return quantity