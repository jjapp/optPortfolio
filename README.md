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

We will plan on purchasing options that are 200 days until expiration to mimic the long S&P portion of the portfolio.  We will sell any option that reaches 30 days to expiration and is still in inventory.

## Managing the Portfolio

### Step 1

Calculate total portfolio value.  This will be the combined value of the T-Bill portion and the current value of the options.  The combined value times the desired leverage equals "targetDelta".

Returns:  targetDelta

### Step 2a:  Non rebalance days

Save total value of portfolio.  Calculate daily returns.  Calculate options statistics.

### Step 2b:  Rebalance days

Compare current option inventory delta to targetDelta.  If option delta is too high we sell the oldest option/s until the actual delta is less than 50 delta from targetDelta.

If option inventory delta is more than 50 delta below targetDelta purchase at the money calls at least 200 days out until actual delta is less than 50 delta from targetDelta.

Save total value of portfolio.  Calculate daily returns.  Calculate options statistics.

## System Design

### Inventory Class

Description:  Holds the options in the portfolio.

Methods:

* Add option
* Remove option
* Calculate Inventory Delta
* Calculate Inventory Theta
* Remove/Replace aged inventory.

### Option Class

* Create Option
* Get Price
* Get Theta
* Get Delta
* Get age

### Cash Class

### Portfolio Class

