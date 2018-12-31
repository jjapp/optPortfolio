import mibian as m
from datetime import date

class Option:
    '''The callOption class represents a call on the SPY
    index.'''

    def __init__(self, exDate, volatility, strike, stock, optiontype, interest, direction):
        '''exDate is the expiration date of the option.
        volatility is the implied volatility of the option and
        strike and stock are the strike price and the stock price.'''

        self.exDate=exDate
        self.volatility=volatility
        self.strike=strike
        self.stock=stock
        self.optiontype=optiontype
        self.interest=interest
        self.direction=direction

    def get_greeks(self, today, new_stock, new_vol):
        '''Takes the date for today and the the current strike price
        and returns the greeks as a dictionary'''

        self.stock=new_stock
        self.volatility=new_vol
        days_left=(self.exDate-today).days
        position=self.direction

        c=m.BS([self.stock, self.strike, self.interest, days_left],
                volatility=self.volatility)

        if self.optiontype=="Call":
            price=c.callPrice*position*100
            theta=c.callTheta*position*100
            delta=c.callDelta*position*100
        else:
            price=c.putPrice*position*100
            theta=c.putTheta*position*100
            delta=c.putDelta*position*100

        options_dict={"price": price, "theta": theta, "delta": delta}

        return options_dict


class Position:
    '''The position object holds one or more options to make a position.'''

    def __init__(self, option_list):

        self.option_list=option_list

    def getPosGreeks(self, today, new_stock, new_vol):

        pos_dict={"price": 0, "theta":0, "delta": 0}

        for i in self.option_list:
            y=i.get_greeks(today, new_stock, new_vol)
            pos_dict['price']=pos_dict['price']+y['price']
            pos_dict['theta']=pos_dict['theta']+y['theta']
            pos_dict['delta']=pos_dict['delta']+y['delta']

        return pos_dict

class Inventory:
    '''The inventory class holds positions in options.'''

    def __init__(self):

        self.position_list=[]

    def add_position(self, position):

        self.position_list.append(position)

    def sell_position(self):

        sold_position=self.position_list[0]
        self.position_list.pop(0)

        return sold_position

    def get_inventory_stats(self,date, new_stock, new_vol):

        price=0
        delta=0
        theta=0

        for row in self.position_list:

            pStats=row.getPosGreeks(date, new_stock, new_vol)
            price=pStats['price']+price
            delta=pStats['delta']+delta
            theta=pStats['theta']+theta

        inv_dict={"price": price, "delta": delta, "theta": theta}

        return inv_dict
