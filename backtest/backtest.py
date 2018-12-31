import pandas as pd
import options
from datetime import timedelta, date
import datetime


#read in data set

df=pd.read_csv('time_series.csv')

#set initial portfolio size

port=100000

#add a volumn for portfolio size

df['portfolio']=''

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
    while i < (tgt)/100:

        #create the options
        call=options.Option(exDate, vol, strike, stock, "Call", interest, 1)
        put=options.Option(exDate, vol, strike, stock, "Put", interest, -1)

        #build the position
        pos_list=[call, put]

        pos=options.Position(pos_list)

        #add the position to Inventory

        inventory.add_position(pos)
        i=i+1

    return inventory

def launch_sim(df):
    stock=df.iloc[0]['Close']
    vol=df.iloc[0]['Settle']
    interest=df.iloc[0]['Value']
    today=df.iloc[0]['Date']

    today=getDate(today)

    #get first expiration date
    exDate=getExpDate(today)

    #get target
    delta=port/stock
    tgt=getTargetDelta(delta)
    print (tgt)

    #get strike
    strike=getStrike(stock)

    #build the portfolio
    inventory=getSynthStock(tgt, today,200, vol, interest, strike, stock)

    print (inventory.get_inventory_stats(today, stock, vol))

if __name__=='__main__':
    launch_sim(df)
