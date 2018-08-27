import math
import time
import requests
from lxml import html
import re
import json
from multiprocessing import Pool
from datetime import datetime

def getCoins():
    url = 'https://coinmarketcap.com/all/views/all/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    #coin_names = tree.xpath('//*[@class="currency-name-container link-secondary"]/text()')
    coin_hrefs = tree.xpath('//*[@class="currency-name-container link-secondary"]//@href')
    return coin_hrefs

def addCoin(coin_href):
    coin_dict = {}
    url = 'https://coinmarketcap.com' + coin_href + 'historical-data/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    try:
        coin_name = tree.xpath('/html/body/div[2]/div/div[1]/div[3]/div[1]/h1/span/text()')[0].replace('(', '').replace(')', '')
        print(coin_name + ' started')
        for i in range(1, 31):
            try:
                date = datetime.strptime(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[1]/text()'.format(i))[0], '%b %d, %Y').strftime('%m%d%y')
                coin_dict[date] = {}
                coin_dict[date]['open'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[2]/text()'.format(i))[0])
                coin_dict[date]['high'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[3]/text()'.format(i))[0])
                coin_dict[date]['low'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[4]/text()'.format(i))[0])
                coin_dict[date]['close'] = float(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[5]/text()'.format(i))[0])
                coin_dict[date]['volume'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[6]/text()'.format(i))[0].replace(',', ''))
                #coin_dict[date]['market_cap'] = int(tree.xpath('//*[@id="historical-data"]/div/div[2]/table/tbody/tr[{}]/td[7]/text()'.format(i))[0].replace(',', '')) not all coins have market_cap
            except:
                print(coin_name + ' day ' + str(i) + ' DNE, breaking...')
                break
    except:
        print('No historical data!')
        return None
    return [coin_dict, coin_name]

def generateJSON(dict):
    with open('coins.json', 'w', encoding='utf-8') as fp:
        json.dump(dict, fp, ensure_ascii=False, indent=4, sort_keys=True)
        print('Generated JSON')

def main():
    dict = {}
    count = 0
    start = time.time()
    with Pool(16) as p:
        d = p.map(addCoin, getCoins())
        p.close()
        p.join()
        for a in d:
            if a != None:
                dict[str(a[1])] = a[0]
                count += 1
    end = time.time()
    print('Average Time per Coin (for ' + str(count) + ' coins): ' + str((end - start)/count))
    generateJSON(dict)

if __name__ == '__main__':
    main()
