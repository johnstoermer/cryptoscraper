import json
from datetime import datetime
import pandas as pd

def readJSON():
    with open('coins.json', 'r', encoding='utf-8') as fp:
        return json.load(fp)

def sortcoins():
    dict = readJSON();
    for coin in dict:
        print(coin)
        new_coin = []
        dates = list(dict[coin].keys())
        dates.sort(key=lambda x: datetime.strptime(x, '%m%d%y'))
        for date in dates:
            new_coin.append({'date':date, **dict[coin][date]})
        coin_df = pd.DataFrame(new_coin)
        coin_df = coin_df.set_index('date')
        try:
            coin_df.to_csv('coins\\{}'.format(coin))
        except:
            print(coin + ' yikes')

sortcoins()
