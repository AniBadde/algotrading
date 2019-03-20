"""
Created on Thu May 18 22:58:12 2017
@author: c0redumb
"""

# To make print working for Python2/3
from __future__ import print_function

# Use six to import urllib so it is working for Python2/3
from six.moves import urllib
# If you don't want to use six, please comment out the line above
# and use the line below instead (for Python3 only).
#import urllib.request, urllib.parse, urllib.error

import time
import pandas as pd
from datetime import date, timedelta
import math

'''
Starting on May 2017, Yahoo financial has terminated its service on
the well used EOD data download without warning. This is confirmed
by Yahoo employee in forum posts.
Yahoo financial EOD data, however, still works on Yahoo financial pages.
These download links uses a "crumb" for authentication with a cookie "B".
This code is provided to obtain such matching cookie and crumb.
'''

# Build the cookie handler
cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)

# Cookie and corresponding crumb
_cookie = None
_crumb = None

# Headers to fake a user agent
_headers={
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}

def _get_cookie_crumb():
	'''
	This function perform a query and extract the matching cookie and crumb.
	'''

	# Perform a Yahoo financial lookup on SP500
	req = urllib.request.Request('https://finance.yahoo.com/quote/^GSPC', headers=_headers)
	f = urllib.request.urlopen(req)
	alines = f.read().decode('utf-8')

	# Extract the crumb from the response
	global _crumb
	cs = alines.find('CrumbStore')
	cr = alines.find('crumb', cs + 10)
	cl = alines.find(':', cr + 5)
	q1 = alines.find('"', cl + 1)
	q2 = alines.find('"', q1 + 1)
	crumb = alines[q1 + 1:q2]
	_crumb = crumb

	# Extract the cookie from cookiejar
	global cookier, _cookie
	for c in cookier.cookiejar:
		if c.domain != '.yahoo.com':
			continue
		if c.name != 'B':
			continue
		_cookie = c.value

	# Print the cookie and crumb
	#print('Cookie:', _cookie)
	#print('Crumb:', _crumb)

def load_yahoo_quote(ticker, begindate, enddate, info = 'quote', format_output = 'list'):
	'''
	This function load the corresponding history/divident/split from Yahoo.
	'''
	# Check to make sure that the cookie and crumb has been loaded
	global _cookie, _crumb
	if _cookie == None or _crumb == None:
		_get_cookie_crumb()

	# Prepare the parameters and the URL
	tb = time.mktime((int(begindate[0:4]), int(begindate[4:6]), int(begindate[6:8]), 4, 0, 0, 0, 0, 0))
	te = time.mktime((int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), 18, 0, 0, 0, 0, 0))

	param = dict()
	param['period1'] = int(tb)
	param['period2'] = int(te)
	param['interval'] = '1d'
	if info == 'quote':
		param['events'] = 'history'
	elif info == 'dividend':
		param['events'] = 'div'
	elif info == 'split':
		param['events'] = 'split'
	param['crumb'] = _crumb
	params = urllib.parse.urlencode(param)
	url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?{}'.format(ticker, params)
	#print(url)
	req = urllib.request.Request(url, headers=_headers)

	# Perform the query
	# There is no need to enter the cookie here, as it is automatically handled by opener
	f = urllib.request.urlopen(req)
	alines = f.read().decode('utf-8')
	#print(alines)
	if format_output == 'list':
		return alines.split()

	if format_output == 'dataframe':
		nested_alines = [line.split(',') for line in alines[1:]]
		cols = alines[0].split(',')
		adf = pd.DataFrame.from_records(nested_alines, columns=cols)
		return adf

## Actual Code: above is setting up the CSV reader


def load_quote(ticker):
	print('===', ticker, '===')
	print(load_yahoo_quote(ticker, '20180519', '20180520'))
	# print(load_yahoo_quote(ticker, '20180519', '20180520', 'dividend'))
	#print(load_yahoo_quote(ticker, '20180515', '20180517', 'split'))
	
def openingP(ticker,date1,date2):
	try:
	    input = load_yahoo_quote(ticker, date1, date2)
	except:
		return 0
	dataList = input[2].split(",")
	for j in range(1,len(dataList)):
		elem = dataList[j]
		elem.strip(' u')
		elem.strip("'")
		dataList[j] = float(elem)
	dataList.pop(0)
	return dataList[0]
	
def closingP(ticker,date1,date2):
	try:
		input = load_yahoo_quote(ticker, date1, date2)
	except:
		return 0
	dataList = input[2].split(",")
	for j in range(1,len(dataList)):
		elem = dataList[j]
		elem.strip(' u')
		elem.strip("'")
		dataList[j] = float(elem)
	dataList.pop(0)
	return dataList[3]
	
def dateList(start, end):
	d1 = date(int(start[0:4]), int(start[4:6]), int(start[6:8]))
	d2 = date(int(end[0:4]), int(end[4:6]), int(end[6:8]))
	delta = d2-d1
	out = []
	for i in range(delta.days+1):
		s = d1 + timedelta(i)
		sn = s.strftime('%Y%m%d')
		out = out + [sn]
	return out

## Assumptions

#open, high, low, close, adj, volume
# we buy at market opening and sell at market close
# moving averages are calculated using the opening price for convenience

#portfolio list - shares owned, spent, earned 

## Trading Algorithms


#Simple Moving Average Momentum Strategy

dates = dateList('20140402','20140517')

print(dates[17])

portlist = [0,0,0]

def calc5MVA(ticker,dat):
	sum = 0
	for i in range(len(dates)-1):
		if dates[i] == dat:
			for j in range(i-3,i):
				#print(j)
				#print(openingP(ticker, dates[j], dates[j+1]))
				sum += openingP(ticker, dates[j], dates[j+1])
				#print(sum)
	return sum/3
	
def calc20MVA(ticker, dat):
	sum = 0
	for i in range(len(dates)-1):
		if dates[i] == dat:
			for j in range(i-7,i):
				#print(j)
				sum += openingP(ticker, dates[j], dates[j+1])
				#print(sum)
	return sum/7
		
def calcNMVA(n, ticker, dat):
	sum = 0
	for i in range(len(dates)-1):
		if dates[i] == dat:
			for j in range(i-n,i):
				price = openingP(ticker, dates[j], dates[j+1])
				if price != 0:
					sum += price
				else:
					sum += openingP(ticker, dates[j-1], dates[j])
	return sum/n

	
def tradeMVA(ticker):
	for i in range(23,len(dates)-1):
		print(calc5MVA(ticker, dates[i]))
		print(calc20MVA(ticker, dates[i]))
		if (calc5MVA(ticker, dates[i]) > calc20MVA(ticker, dates[i])) and (calc5MVA(ticker, dates[i-1]) < calc20MVA(ticker, dates[i-1])):
			portlist[0] += 10
			portlist[1] += 10*openingP(ticker, dates[i], dates[i+1])
		if (calc5MVA(ticker, dates[i]) < calc20MVA(ticker, dates[i])) and (calc5MVA(ticker, dates[i-1]) > calc20MVA(ticker, dates[i-1])):
			portlist[0] -= 10
			portlist[2] += 10*openingP(ticker, dates[i], dates[i+1])
		print(dates[i])
		print(portlist)
	return
	
#Cooler Moving Average Momentum Strategy - add weights to means?

def calcWMVA(n, ticker, dat):
	return


#Mean Reversion

#use mean formula from above to calculate average (for now)

def standdev(ticker, date, mean):
	sumval = 0
	for i in range(len(dates)-1):
		sumval += (openingP(ticker, dates[i], dates[i+1])-mean)**2
	std = math.sqrt(sumval/len(dates))
	return std
		
		
def zVal(price,mean,standdev):
	return (price-mean)/standdev


def tradeMean(ticker):
	for i in range(12,len(dates)-1):
		mean = calcNMVA(10,ticker,dates[i])
		std = standdev(ticker,dates[i],mean)
		price = openingP(ticker, dates[i], dates[i+1])
		if price == 0:
			price = openingP(ticker, dates[i-1], dates[i])
		z = zVal(price, mean, std)
		print(z)
		if z>0.4:
			portlist[0] -= 10
			portlist[2] += 10*price
		if z<-0.4:
			portlist[0] += 10
			portlist[1] += 10*price
		if z<0.2 and z>=0:
			if portlist[0] > 0:
				portlist[1] += portlist[0]*price
				portlist[0] = 0
		elif z>-0.2 and z<=0:
			if portlist[0] > 0:
				portlist[2] += portlist[0]*price
				portlist[0] = 0
		print(portlist)
		
	return portlist


## Findings

# 1) Moving Average Crossover Strategy:

#Traditional crossover moving strategies don't really work anywhere outisde some
#kind of local minimum point (decreasing and then increasing). Does not capitalize
#on a stock price continuously increasing or decreasing over time which is pretty
#problematic. May work on very high frequency trades (with low margins). 

#TWTR: with 3, 7 MVA *average* 4.5% gain from 02/04/14 to 04/07/14

# 2) Mean Reversion Strategy:

#We sell when the price has a z-score greater than 1 (> 1 SD over mean), and
#buy when the z score is less than 1. When the price is within some margin, we 
#clear our position and go back to neutral (so at any point in time we only have
#a buy or sell position. 

''' 0.7-0.3 1011,1047
	0.5-0.3 2079.6, 2093.6
	0.4-0.2 3262.099, 3161.399
	
	'''



## Testing
def test():
	# Download quote for stocks
	#print(load_yahoo_quote('QCOM','20050519','20180520')[2])
	
	tradeMean('TWTR')
	print(portlist)
	
	return

	# Download quote for index
	#load_quote('^DJI')
	
	
#print(calc5MVA('AAPL','20170605'))

test()
