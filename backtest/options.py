import mibian as m
from datetime import date

class Option:
    '''The callOption class represents a call on the SPY
    index.'''

    def __init__(self, exDate, volatility, strike, stock,
                type, interest):
        '''exDate is the expiration date of the optionself.
        volatility is the implied volatility of the option and
        strike and stock are the strike price and the stock price.'''

        self.exDate=exDate
        self.volatility=volatility
        self.strike=strike
        self.stock=stock
        self.type=type
        self.interest=interest

    def get_greeks(self, today, new_stock):
        '''Takes the date for today and the the current strike price
        and returns the greeks as a dictionary'''
        
        self.stock=new_stock
        days_left=(self.exDate-today).days

        c=m.BS([self.stock, self.strike, self.interest, days_left],
                volatility=self.volatility)

        if type=="Call":
            price=c.callPrice
            theta=c.callTheta
            delta=c.callDelta
        else:
            price=c.putPrice
            theta=c.putTheta
            delta=c.putDelta

        options_dict={"price": price, "theta": theta, "delta": delta}

        return options_dict
