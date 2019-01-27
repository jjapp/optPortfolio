# LEAPS and T-Bill Portfolio Simulation

## Overview

In "Options as a Strategic Investment" Lawrence McMillan proposes replicating a long portfolio of the S&P using LEAPS and then using the remaining cash balance to invest in T-bills.  His goal is to replicate the potential upside performance of the market while putting a floor on negative returns.  Additionally this portfolio could potentially achieve slightly higher returns than the S&P due to the impact of interest rates from the T-bills on the overall performance of the investment. 

To simulate this portfolio we need to decide on how to build and manage the option inventory and how to allocate percentages of capital to either the options portion of the portfolio or the t-bills portion of the portfolio.  McMillan's approach to these two decisions seems arbitrary.  For example, he allocates 10% of the cash value of the portfolio to options and 90% of the portfolio to bonds.  But this will result in varying exposure to the market as implied volatility rises and falls.  Also, his scheme for managing the inventory of options focuses on a concept of diversification across expirations and arbitrary decisions for turns.  

If we want to compare this portfolio's returns to the returns of a long only S&P investment we need to modify the rules for portfolio construction outlined by McMillan.  In particular, we maintain an inventory of options based on minimizing cost per delta exposure and we allocate capital to the options portfolio to achieve a targeted leverage of the S&P.  For example, if we want a 1X leveraged portfolio we purchase enough calls to match the delta we would have buying the SPY.  If we want a 2X portfolio we would buy enough calls to match a 100% leveraged portfolio in the SPY.

## Data

We need a time series that includes estimates of S&P daily returns, S&P daily levels, short-term interest rates and S&P implied volatility levels.  I constructed a dataset from May of 2007 through November of 2018.  The set was limited by the availability of VIX futures data.

S&P data was purchased from Quotemedia which provides professional grade end of day stock market quotes.  The returns data was calculated using adjusted closing prices to account for dividends.  Levels were captured using unadjusted closing prices.

Short term interest rate data was sourced from the St Louis Federal Reserve data.  It includes short-term interest rates by day for the period of interest.

VIX data was purchased from Stevens Continuous Futures Data, a provider of professional grade chained futures contracts.  The data used for estimating volatility was the front month contract, un-smoothed futures.

These three data sources were combined to form a single time series with the following arrays: S&P Close, S&P daily return, VIX end of day settlement price, Short term interest rates.

## Selecting Options Contracts to Purchase

There are two components of holding costs associated with a long option contract.  The first is time decay.  The second is the lost interest from holding a T-Bill instead of a more expensive option.  In general, the cost from time decay is higher than the opportunity cost of holding an option.  The chart below shows holding costs by days until expiration for a representative call option.

![holdingCost](/home/appertjt/Documents/Grad School/Thesis/Chap2LeveragedPortfolio/code/holdingCost.png)

We will plan on purchasing options that are 400 days until expiration to mimic the long S&P portion of the portfolio.  We will sell any option that reaches 50 days to expiration and is still in inventory.

## Managing the Portfolio

### Step 1

Calculate total portfolio value.  This will be the combined value of the T-Bill portion and the current value of the options.  The combined value times the desired leverage equals "targetDelta".

Returns:  targetDelta

### Step 2a:  Non rebalance days

Save total value of portfolio.  Calculate daily returns.  Calculate options statistics.

### Step 2b:  Rebalance days

Compare current option inventory delta to targetDelta.  If option delta is too high we sell the oldest option/s until the actual delta is less than 50 delta from targetDelta.

If option inventory delta is more than 50 delta below targetDelta purchase at the money calls at least 400 days out until actual delta is less than 50 delta from targetDelta.

Save total value of portfolio.  Calculate daily returns.  Calculate options statistics.

## System Design

### Position Class

Description:  Object that holds multiple options objects to form a position (ex: long call short put.)

#### Methods

* getPosEx()
  * Returns expiration date of the position



### Option Class

Description:  Creates an option object (Call or put)

#### Methods

* get_greeks
  * Returns price, theta, delta
* get_exDate
  * Returns expiration date.

### Inventory

Description:  Object that holds all options positions in the portfolio.

#### Methods

* add_position
* sell_position
* get_inventory_stats
* sellExpirContracts

# Performance Estimates for Leveraged Options Portfolio

## Overview:

This script measures the performance of a buy and hold strategy on the SPY ETF versus a portflio that replicates the exposure to the SPY through LEAPS and invests the remaining cash in short term government bonds.

- System 1:  

A 3x leveraged portfolio is tested using synthetic long positions in the ETF.  The synthetic long position is created using a short put and a long call.  The position is sized so that the option delta is equal to 3X the delta implied by a 100% allocation to the SPY.  Delta is adjusted a maximum of once per day if the position moves more than 100 delta from its targeted level.

- System 2:

A 1x portfolio is tested using synthetic long positions in the ETF.  The synthetic long position is created using a short put and a long call.  The position is sized so that the option delta is equal to 1X the delta implied by a 100% allocation to the SPY.  Delta is adjusted a maximum of once per day if the position moves more than 100 delta from its targeted level.

- System 3:

A 1x portfolio is tested using long call positions in the ETF.  The position is sized so that the option delta is equal to 1X the delta implied by a 100% allocation to the SPY.  Delta is adjusted a maximum of once per day if the position moves more than 100 delta from its targeted level.

```python
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyfolio as pf
%matplotlib inline  

import warnings; warnings.simplefilter('ignore')

pd.options.display.latex.repr = True

```

## Helper method for getting system stats and benchmarks.

```python

def get_system_stats(df):
    df['pret']=np.log(df['portfolio']/df['portfolio'].shift(1))
    df=df.dropna()
    #pf.create_returns_tear_sheet(df[['Date','pret']])

    system_ret=df[['Date', 'pret']]
    benchmark_ret=df[['Date', 'return']]

    system_ret['Date'] = pd.to_datetime(system_ret['Date'])
    system_ret.set_index('Date', inplace=True)
    
    benchmark_ret['Date'] = pd.to_datetime(benchmark_ret['Date'])
    benchmark_ret.set_index('Date', inplace=True)

    series1=system_ret.iloc[:,0]
    benchmark=benchmark_ret.iloc[:,0]
    x=pf.create_returns_tear_sheet(series1, benchmark_rets=benchmark, bootstrap=None)
    return x
    
```

## System 1

```python
import warnings; warnings.simplefilter('ignore')
df=pd.read_csv('backtest/synthlev.csv')
tear1=get_system_stats(df)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;"><th>Start date</th><td colspan=2>2007-05-22</td></tr>
    <tr style="text-align: right;"><th>End date</th><td colspan=2>2016-10-06</td></tr>
    <tr style="text-align: right;"><th>Total months</th><td colspan=2>112</td></tr>
    <tr style="text-align: right;">
      <th></th>
      <th>Backtest</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual return</th>
      <td>-9.7%</td>
    </tr>
    <tr>
      <th>Cumulative returns</th>
      <td>-61.5%</td>
    </tr>
    <tr>
      <th>Annual volatility</th>
      <td>53.7%</td>
    </tr>
    <tr>
      <th>Sharpe ratio</th>
      <td>0.08</td>
    </tr>
    <tr>
      <th>Calmar ratio</th>
      <td>-0.10</td>
    </tr>
    <tr>
      <th>Stability</th>
      <td>0.00</td>
    </tr>
    <tr>
      <th>Max drawdown</th>
      <td>-94.7%</td>
    </tr>
    <tr>
      <th>Omega ratio</th>
      <td>1.02</td>
    </tr>
    <tr>
      <th>Sortino ratio</th>
      <td>0.12</td>
    </tr>
    <tr>
      <th>Skew</th>
      <td>-0.28</td>
    </tr>
    <tr>
      <th>Kurtosis</th>
      <td>24.89</td>
    </tr>
    <tr>
      <th>Tail ratio</th>
      <td>0.89</td>
    </tr>
    <tr>
      <th>Daily value at risk</th>
      <td>-6.8%</td>
    </tr>
    <tr>
      <th>Alpha</th>
      <td>-0.07</td>
    </tr>
    <tr>
      <th>Beta</th>
      <td>2.40</td>
    </tr>
  </tbody>
</table>



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Worst drawdown periods</th>
      <th>Net drawdown in %</th>
      <th>Peak date</th>
      <th>Valley date</th>
      <th>Recovery date</th>
      <th>Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>94.67</td>
      <td>2007-06-01</td>
      <td>2009-03-09</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2.79</td>
      <td>2007-05-23</td>
      <td>2007-05-24</td>
      <td>2007-05-30</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.34</td>
      <td>2007-05-30</td>
      <td>2007-05-31</td>
      <td>2007-06-01</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.00</td>
      <td>2007-05-22</td>
      <td>2007-05-22</td>
      <td>2007-05-22</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.00</td>
      <td>2007-05-22</td>
      <td>2007-05-22</td>
      <td>2007-05-22</td>
      <td>1</td>
    </tr>
  </tbody>
</table>



![png](/home/appertjt/Documents/Grad%20School/Thesis/Chap2LeveragedPortfolio/performance/output_5_2.png)

## System 2

```python
import warnings; warnings.simplefilter('ignore')
df=pd.read_csv('backtest/synth.csv')
tear1=get_system_stats(df)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;"><th>Start date</th><td colspan=2>2007-05-22</td></tr>
    <tr style="text-align: right;"><th>End date</th><td colspan=2>2016-10-06</td></tr>
    <tr style="text-align: right;"><th>Total months</th><td colspan=2>112</td></tr>
    <tr style="text-align: right;">
      <th></th>
      <th>Backtest</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual return</th>
      <td>1.1%</td>
    </tr>
    <tr>
      <th>Cumulative returns</th>
      <td>10.4%</td>
    </tr>
    <tr>
      <th>Annual volatility</th>
      <td>4.4%</td>
    </tr>
    <tr>
      <th>Sharpe ratio</th>
      <td>0.26</td>
    </tr>
    <tr>
      <th>Calmar ratio</th>
      <td>0.11</td>
    </tr>
    <tr>
      <th>Stability</th>
      <td>0.86</td>
    </tr>
    <tr>
      <th>Max drawdown</th>
      <td>-9.4%</td>
    </tr>
    <tr>
      <th>Omega ratio</th>
      <td>1.06</td>
    </tr>
    <tr>
      <th>Sortino ratio</th>
      <td>0.35</td>
    </tr>
    <tr>
      <th>Skew</th>
      <td>-1.14</td>
    </tr>
    <tr>
      <th>Kurtosis</th>
      <td>30.58</td>
    </tr>
    <tr>
      <th>Tail ratio</th>
      <td>0.97</td>
    </tr>
    <tr>
      <th>Daily value at risk</th>
      <td>-0.6%</td>
    </tr>
    <tr>
      <th>Alpha</th>
      <td>0.00</td>
    </tr>
    <tr>
      <th>Beta</th>
      <td>0.14</td>
    </tr>
  </tbody>
</table>



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Worst drawdown periods</th>
      <th>Net drawdown in %</th>
      <th>Peak date</th>
      <th>Valley date</th>
      <th>Recovery date</th>
      <th>Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>9.37</td>
      <td>2007-07-19</td>
      <td>2007-08-15</td>
      <td>2007-10-09</td>
      <td>59</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7.69</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2012-02-17</td>
      <td>1139</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3.95</td>
      <td>2007-06-01</td>
      <td>2007-06-26</td>
      <td>2007-07-13</td>
      <td>31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.80</td>
      <td>2015-05-21</td>
      <td>2016-02-11</td>
      <td>2016-06-08</td>
      <td>275</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1.49</td>
      <td>2014-09-18</td>
      <td>2014-10-16</td>
      <td>2014-10-31</td>
      <td>32</td>
    </tr>
  </tbody>
</table>



![png](/home/appertjt/Documents/Grad%20School/Thesis/Chap2LeveragedPortfolio/performance/output_7_2.png)

## System 3

```python
import warnings; warnings.simplefilter('ignore')
df=pd.read_csv('backtest/call.csv')
tear1=get_system_stats(df)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;"><th>Start date</th><td colspan=2>2007-05-22</td></tr>
    <tr style="text-align: right;"><th>End date</th><td colspan=2>2016-10-06</td></tr>
    <tr style="text-align: right;"><th>Total months</th><td colspan=2>112</td></tr>
    <tr style="text-align: right;">
      <th></th>
      <th>Backtest</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual return</th>
      <td>-3.0%</td>
    </tr>
    <tr>
      <th>Cumulative returns</th>
      <td>-24.7%</td>
    </tr>
    <tr>
      <th>Annual volatility</th>
      <td>10.2%</td>
    </tr>
    <tr>
      <th>Sharpe ratio</th>
      <td>-0.25</td>
    </tr>
    <tr>
      <th>Calmar ratio</th>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>Stability</th>
      <td>0.01</td>
    </tr>
    <tr>
      <th>Max drawdown</th>
      <td>-37.9%</td>
    </tr>
    <tr>
      <th>Omega ratio</th>
      <td>0.96</td>
    </tr>
    <tr>
      <th>Sortino ratio</th>
      <td>-0.35</td>
    </tr>
    <tr>
      <th>Skew</th>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>Kurtosis</th>
      <td>1.31</td>
    </tr>
    <tr>
      <th>Tail ratio</th>
      <td>0.95</td>
    </tr>
    <tr>
      <th>Daily value at risk</th>
      <td>-1.3%</td>
    </tr>
    <tr>
      <th>Alpha</th>
      <td>-0.04</td>
    </tr>
    <tr>
      <th>Beta</th>
      <td>0.40</td>
    </tr>
  </tbody>
</table>



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Worst drawdown periods</th>
      <th>Net drawdown in %</th>
      <th>Peak date</th>
      <th>Valley date</th>
      <th>Recovery date</th>
      <th>Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>37.85</td>
      <td>2007-07-19</td>
      <td>2009-03-09</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3.62</td>
      <td>2007-06-01</td>
      <td>2007-06-26</td>
      <td>2007-07-13</td>
      <td>31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.99</td>
      <td>2007-05-22</td>
      <td>2007-05-24</td>
      <td>2007-05-30</td>
      <td>7</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.17</td>
      <td>2007-05-30</td>
      <td>2007-05-31</td>
      <td>2007-06-01</td>
      <td>3</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.09</td>
      <td>2007-07-13</td>
      <td>2007-07-18</td>
      <td>2007-07-19</td>
      <td>5</td>
    </tr>
  </tbody>
</table>



![png](/home/appertjt/Documents/Grad%20School/Thesis/Chap2LeveragedPortfolio/performance/output_9_2.png)



```python

```

