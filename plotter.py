import json
import matplotlib.pyplot as plt
import time

def readJSON():
    with open('coins.json', 'r', encoding='utf-8') as fp:
        return json.load(fp)

def graphCoin(coin_name):
    start = time.time()
    dict = readJSON()
    end = time.time()
    print(end - start)
    days = dict[coin_name]
    graphlist = []
    maxval = 0
    minval = 10000
    for day in days:
        graphlist.append(days[day]['open'])
        if days[day]['open'] > maxval:
            maxval = days[day]['open']
        if days[day]['open'] < minval:
            minval = days[day]['open']
    plt.plot(range(len(days.keys())), graphlist, linewidth=2.0)
    plt.axis([len(days.keys()) - 31, len(days.keys()) - 1, minval, maxval])
    plt.show()

def main():
    graphCoin('BTC')

if __name__ == '__main__':
    main()
