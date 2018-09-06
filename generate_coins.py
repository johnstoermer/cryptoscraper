import requests
import time
from datetime import datetime
from lxml import html
import pandas as pd
from multiprocessing import Pool
import numpy as np
import os.path

def getAllCoins(): #use for scraping all coins
    url = 'https://coinmarketcap.com/all/views/all/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    coin_hrefs = tree.xpath('//*[@class="currency-name-container link-secondary"]//@href')
    return coin_hrefs

def getCoins(): #use for scraping batches of coins by page
    coin_hrefs = []
    for i in range(1): #by page, 100 per page
        url = 'https://coinmarketcap.com/{}'.format(i)
        page = requests.get(url)
        tree = html.fromstring(page.content)
        coin_hrefs += tree.xpath('//*[@class="currency-name-container link-secondary"]//@href')
    return coin_hrefs

def startCoin(coin_href):
    url = 'https://coinmarketcap.com' + coin_href + 'historical-data/?start=20130428&end=' + datetime.today().strftime('%Y%m%d')
    page = requests.get(url)
    tree = html.fromstring(page.content)
    try:
        coin_name = tree.xpath('/html/body/div[2]/div/div[1]/div[3]/div[1]/h1/span/text()')[0].replace('(', '').replace(')', '')
    except:
        #coin_name = tree.xpath('/html/body/div[2]/div/div[1]/div[4]/div[1]/h1/span/text()')[0].replace('(', '').replace(')', '')
        return 0
    if os.path.isfile('coins\\{}'.format(coin_name)):
        updateCoin(tree, coin_name)
        return 1
    else:
        newCoin(tree, coin_name)
        return 1

def newCoin(tree, coin_name):
    print('Starting ' + coin_name + '...')
    coin_new = []
    count = 1
    while True:
        try:
            coin_dict = {}
            coin_dict['date'] = int(datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(count))[0], '%b %d, %Y').strftime('%y%m%d'))
            coin_dict['open'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[2]/text()'.format(count))[0])
            coin_dict['high'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[3]/text()'.format(count))[0])
            coin_dict['low'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[4]/text()'.format(count))[0])
            coin_dict['close'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[5]/text()'.format(count))[0])
            coin_dict['volume'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[6]/text()'.format(count))[0].replace(',', ''))
            coin_new.append(coin_dict)
            count += 1
            #coin_dict[date]['market_cap'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[7]/text()'.format(count))[0].replace(',', '')) not all coins have market_cap
        except:
            print(coin_name + ' breaking at ' + str(count) + '...')
            break
    coin_new.reverse()
    coin_df = pd.DataFrame(coin_new)
    coin_df = coin_df.set_index('date')
    coin_df.to_csv('coins\\{}'.format(coin_name))
    print(coin_name + ' was added.')

def updateCoin(tree, coin_name):
    print('Updating ' + coin_name + '...')
    coin_df = pd.read_csv('coins\\{}'.format(coin_name))
    coin_df = coin_df.set_index('date')
    date = coin_df.index[-1]
    print(date)
    coin_update = []
    count = 1
    while True:
        if date == int(datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(count))[0], '%b %d, %Y').strftime('%y%m%d')):
            break
        else:
            coin_dict = {}
            coin_dict['date'] = int(datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(count))[0], '%b %d, %Y').strftime('%y%m%d'))
            coin_dict['open'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[2]/text()'.format(count))[0])
            coin_dict['high'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[3]/text()'.format(count))[0])
            coin_dict['low'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[4]/text()'.format(count))[0])
            coin_dict['close'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[5]/text()'.format(count))[0])
            coin_dict['volume'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[6]/text()'.format(count))[0].replace(',', ''))
            coin_update.append(coin_dict)
            count += 1
            print(coin_name)
    if coin_update != []:
        coin_update.reverse()
        update_df = pd.DataFrame(coin_update)
        update_df = update_df.set_index('date')
        coin_df = coin_df.append(update_df)
        coin_df.to_csv('coins\\{}'.format(coin_name))
        print(coin_name + ' was updated.')

def go():
    count = 0
    start = time.time()
    with Pool(16) as p:
        d = p.map(startCoin, getCoins())
        p.close()
        p.join()
        for a in d:
            count += a
    end = time.time()
    print('Finished with ' + str((end-start)/count) + ' seconds per coin')

def main():
    go()

if __name__ == '__main__':
    main()
