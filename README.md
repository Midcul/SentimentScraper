# SentimentScraper
A pipeline that joins the BeautifulSoup webscraper and Flair sentiment classifier. The goal is to get an idea of the Internet's positive or negative sentiment on any topic or question. Currently, the code checks Google for stock news to use that sentiment as a indicator for future stock performance.

scraper.py is a module in which you can enter the desired queries, and receive a list of site/sentiment scores for that query.

results.py is a test of scraper.py that labels each stock sentiment/performance pair as a success or fail.
