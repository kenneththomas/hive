#rly not interested in making the ten billionth market data scraper or using someone else's

#market data is stored in US Pennies
md = {'ZVZZT' : 1000,
      'AAPL' : 17000,
}

def getprice(symbol):
    return md.get(symbol)
