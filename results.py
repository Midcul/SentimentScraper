from yahoo_fin import stock_info as si
import yfinance as yf
import ssl
from scraper import *

# Avoids certificate verify failed error
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# Running all 503 tickers takes too long and is prone to stalling at some point in the middle. Divide into groups of 25
tickers = si.tickers_sp500()
subsets = []
for i in range(0, 476, 25):
    subsets.append(tickers[i:i+26])

# Accuracy test
cases = 0
correct = 0

for i in subsets:
    for j in i:
        sentiment_data = news_sentiment(j)
        for k in sentiment_data:
            date = '2023-' + k[0]
            sentiment = k[1][1]
            data = yf.download(j, date, period='1d')

            try:
                Open = data.iloc[0, 0]
                Close = data.iloc[0, 3]

            # Download can fail!?
            except IndexError:
                continue

            if Close < Open and sentiment == 'NEGATIVE':
                correct += 1
            elif Close > Open and sentiment == 'POSITIVE':
                correct += 1
            cases += 1

            print(correct, '/', cases, correct/cases, '%')
