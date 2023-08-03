import requests
import re
from bs4 import BeautifulSoup
from flair.data import Sentence
from flair.models import TextClassifier

# score_flair function returns POSITIVE/NEGATIVE and a score from -1 to 1 rating how POS/NEG the text is
classifier = TextClassifier.load('en-sentiment')


def score_flair(text):
    sentence = Sentence(text)
    classifier.predict(sentence)
    score = sentence.labels[0].score
    value = sentence.labels[0].value
    return score, value


def news_sentiment(company):
    # Get html text of the news page given a google query "(company) news"
    page = requests.get('https://www.google.com/search?q=' + company + '+stock+news&tbm=nws')
    soup = BeautifulSoup(page.content, 'html.parser')
    # 'a' is the html header that links are found under
    results = soup.find_all('a')

    # Get links from html text of google news page
    links = []
    for line in results:
        line = str(line)
        try:
            links.append(line[line.index('https'):])
        except ValueError:
            pass

    # Clean up links and remove links to other google pages
    links = [i[:i.index('"')] for i in links]
    links = [i for i in links if 'google.com' not in i]
    links = [i[:i.index('&amp')] for i in links]

    # These sites halt the program, so I'm manually removing them
    links = [i for i in links if 'nasdaq.com' not in i]
    links = [i for i in links if 'money.usnews.com' not in i]
    links = [i for i in links if 'caterpillar.com' not in i]
    links = [i for i in links if 'cmegroup.com' not in i]

    # Go article by article, record publish date and sentiment. This data will be compared against market movement the
    # day of publishing or the closest future day of open market. These articles seem to be 3 days old at most
    dates = []
    sentiments = []

    # For article datetime-finding
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for i in links:
        print(i)
        page = requests.get(i)
        soup = BeautifulSoup(page.content, 'html.parser')

        # HTML labels vary from article to article, so try and except is a quick skip for articles I can't process
        try:
            # Pick out HTML line with datetime, isolate yyyy-mm-dd
            datetime = soup.find_all('time')
            datetime = str(datetime[0])
            month_match = [j for j in months if j in datetime][0]
            dateindex = datetime.index(month_match)

            final_date = ''
            day_found = False
            day_finished = False

            # Add characters to the date until the specific day has been added. No year needed
            # The number of articles is small; if that increases, please optimize this
            while not day_finished:
                final_date += datetime[dateindex]
                dateindex += 1
                if datetime[dateindex] in '0123456789':
                    day_found = True
                if day_found and datetime[dateindex] not in '0123456789':
                    day_finished = True

            # Standardize month/day format to string month-day to use the yfinance module down the line
            final_date = final_date.split(' ')
            dates.append('0' + str(months.index(final_date[0][:3]) + 1) + '-' + (final_date[1]))

            # Pick out article text, de-noising as much as possible
            results = soup.find_all('p')
            found_text = re.search('<p(.*)</p>', str(results))
            found_text = found_text.group(1)
            found_text = re.sub('<.*?>', '', found_text)
            sentiments.append(score_flair(found_text))

        # If the HTML headers I've selected aren't found
        except IndexError:
            pass

        # If the HTML headers are found, but regex returns no text
        except AttributeError:
            pass

        # A website stalls for too long upon trying to get its HTML text
        except ConnectionError:
            pass

        # Related to ConnectionError, I think
        except TimeoutError:
            pass

    return list(zip(dates, sentiments))


# Does it work?
if __name__ == '__main__':
    print(news_sentiment('AMZN'))
