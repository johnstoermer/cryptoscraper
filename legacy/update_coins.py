import requests
import time
from datetime import datetime
from lxml import html
import pandas as pd
from multiprocessing import Pool
import numpy as np

def getCoins():
    coin_hrefs = []
    for i in range(1,5):
        url = 'https://coinmarketcap.com/{}'.format(i)
        page = requests.get(url)
        tree = html.fromstring(page.content)
        coin_hrefs += tree.xpath('//*[@class="currency-name-container link-secondary"]//@href')
    return coin_hrefs

def updateCoin(coin_href):
    url = 'https://coinmarketcap.com' + coin_href + 'historical-data/?start=20130428&end=' + datetime.today().strftime('%Y%m%d')
    page = requests.get(url)
    tree = html.fromstring(page.content)
    try:
        coin_name = tree.xpath('/html/body/div[2]/div/div[1]/div[3]/div[1]/h1/span/text()')[0].replace('(', '').replace(')', '')
    except:
        #coin_name = tree.xpath('/html/body/div[2]/div/div[1]/div[4]/div[1]/h1/span/text()')[0].replace('(', '').replace(')', '')
        return 0
    coin_df = pd.read_csv('coins\\{}'.format(coin_name))
    coin_df = coin_df.set_index('date')
    date = coin_df.index[-1]
    coin_update = []
    count = 1
    while True:
        if date == int(datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(count))[0], '%b %d, %Y').strftime('%m%d%y')): #test
            break
        else:
            coin_dict = {}
            coin_dict['date'] = int(datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(count))[0], '%b %d, %Y').strftime('%m%d%y'))
            coin_dict['open'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[2]/text()'.format(count))[0])
            coin_dict['high'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[3]/text()'.format(count))[0])
            coin_dict['low'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[4]/text()'.format(count))[0])
            coin_dict['close'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[5]/text()'.format(count))[0])
            coin_dict['volume'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[6]/text()'.format(count))[0].replace(',', ''))
            coin_update.append(coin_dict)
            count += 1
    if coin_update != []:
        coin_update.reverse()
        update_df = pd.DataFrame(coin_update)
        update_df = update_df.set_index('date')
        coin_df = coin_df.append(update_df)
        coin_df.to_csv('coins\\{}'.format(coin_name))
        print(coin_name + ' was updated.')
        return 1
    else:
        return 0

def update():
    count = 0
    start = time.time()
    with Pool(16) as p:
        d = p.map(updateCoin, getCoins())
        p.close()
        p.join()
        for a in d:
            count += a
    end = time.time()
    if count == 0:
        print('All coins are updated!')
    else:
        print(str(count) + ' coins were updated.')

def RSI(series, period): #http://www.andrewshamlet.net/2017/06/10/python-tutorial-rsi/ idk dude, maybe this? https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
    d = d.drop(d.index[:(period-1)])
    rs = u.ewm(com=period-1, adjust = False).mean() / d.ewm(com=period-1, adjust=False).mean()
    return 100 - 100 / (1 + rs)

def MACD(df):
    return df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()

def analyze(coin_name):
    coin_df = pd.read_csv('coins\\{}'.format(coin_name))
    coin_df = coin_df.set_index('date')
    coin_df['rsi'] = RSI(coin_df['close'], 14)
    coin_df['macd'] = MACD(coin_df)
    print(coin_df)

def main():
    update()
    #analyze('BTC')

if __name__ == '__main__':
    main()
