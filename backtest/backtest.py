import pandas as pd
import options
from datetime import timedelta, date
import datetime

####Note:  system status 1 means you're using puts and calls
system_status=0

#read in data set

df=pd.read_csv('time_series.csv')
#df=df.head(150)

#set initial portfolio size

port=100000

#add a volumn for portfolio size, cash, options

df['portfolio']=''
df['options']=''
df['cash']=0
df['delta']=''
df['tgtdelta']=''

#set initial value for portfolio size
df.at[0,'portfolio']=port



#get initial delta target
spy_price=df.iloc[0]['Close']
init_delta = port/spy_price

#helper functions
def getStrike(x, base=5):
    '''rounds current stock price to nearest $5 dollar increment'''
    return int(base * round(float(x)/base))

def getTargetDelta(x, base=100):
    '''rounds current stock price to nearest 100 share increment'''
    return int(base * round(float(x)/base))

def getExpDate(x):
    '''returns the targeted expiration date for a new option.'''
    #Defaults to 200 days for first pass.  Need to refine
    exDate=x+timedelta(200)

    return exDate

def getDate(x):
    today=datetime.datetime.strptime(x, '%Y-%m-%d').date()
    return today
#build the initial options portfolio using a synthetic stock(long call, short put)

def getSynthStock(tgt, date, dte, vol, interest, strike, stock):
    '''Sets up iterative process to build the inventory up to initial levels'''
    #get exDate
    exDate=getExpDate(date)

    #create the inventory object
    inventory=options.Inventory()
    i=0
    if system_status==1:
        tgt_factor=(tgt)/100
    else:
        tgt_factor=tgt/50

    while i < tgt_factor:

        #create the options
        call=options.Option(exDate, vol, strike, stock, "Call", interest, 1)
        put=options.Option(exDate, vol, strike, stock, "Put", interest, -1)
        #build the position
        if system_status==1:
            pos_list=[call, put]
        else:
            pos_list=[call]

        pos=options.Position(pos_list)

        #add the position to Inventory

        inventory.add_position(pos)
        i=i+1

    return inventory


def initiate_sim(df):
    stock=df.iloc[0]['Close']
    vol=df.iloc[0]['Settle']
    interest=df.iloc[0]['Value']
    today=df.iloc[0]['Date']

    today=getDate(today)

    #get first expirtoday=df.iloc[0]['Date']ation date
    exDate=getExpDate(today)

    #get target
    delta=port/stock
    tgt=getTargetDelta(delta)


    #get strike
    strike=getStrike(stock)

    #build the portfolio
    inventory=getSynthStock(tgt, today,200, vol, interest, strike, stock)

    return (inventory)

def run_sim(df):
    stock=df.iloc[0]['Close']
    vol=df.iloc[0]['Settle']
    today=df.iloc[0]['Date']
    df.at[0,'tgtdelta']=float(port)/float(stock)
    today=getDate(today)
    y=initiate_sim(df)
    price=y.get_inventory_stats(today, stock, vol)


    value=price['price']
    pDelta=price['delta']
    #initiate initial values
    df.at[0, 'options']=value
    df.at[0, 'delta']=pDelta
    df.at[0, 'cash']=float(df.iloc[0]['portfolio']-df.iloc[0]['options'])

    #cycle through by day

    for i in range(1, len(df)-1):
        stock=df.iloc[i]['Close']
        vol=df.iloc[i]['Settle']
        today=df.iloc[i]['Date']
        today=getDate(today)
        interest=df.iloc[i]['Value']
        daily_interest=interest/36500


        #get new cash value and delta
        price=y.get_inventory_stats(today, stock, vol)

        total_cash=df.iloc[i-1]['cash']

        total_cash=float(total_cash)*(1+daily_interest)
        df.at[i, 'cash']=total_cash

        #update df value
        df.at[i,'options']=price['price']
        #get rid of expiring contracts
        y.sellExpirContracts(today)

        delta=price['delta']
        value=price['price']

        ###Issue with rolling up cash portfolio...need to checl


        df.at[i, 'portfolio']=total_cash+price['price']


        #get new target delta
        tgtdelta=df.iloc[i]['portfolio']/stock

        tgt=getTargetDelta(tgtdelta)
        df.at[i, 'tgtdelta']=tgt
        df.at[i, 'delta']=delta

        gap=tgt-delta

        #set up portfolio rebalance

        exDate=getExpDate(today)
        strike=getStrike(stock)


        if gap>100:

            call=options.Option(exDate, vol, strike, stock, "Call", interest, 1)
            #uncomment if using puts too
            put=options.Option(exDate, vol, strike, stock, "Put", interest, -1)
            if system_status==1:
                pos_list=[call, put]
            else:
                pos_list=[call]

            pos=options.Position(pos_list)

            #add the position to Inventory

            y.add_position(pos)
        elif gap<-100:
            y.sell_position()
        else:
            continue

        #get new options price
        price=y.get_inventory_stats(today, stock, vol)
        value= price['price']
        df.at[i, 'options']=value
        df.at[i, 'cash']=df.iloc[i]['portfolio']-value

    if system_status==1:
        df.to_csv('synth.csv')
    else:
        df.to_csv('call.csv')


if __name__=='__main__':
    run_sim(df)
