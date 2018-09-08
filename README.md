# cryptoscraper
cryptoscraper is a tool for scraping crypto price information from [CoinMarketCap](https://coinmarketcap.com/ "CoinMarketCap")
## Requirements:
* requests, for retrieving web pages
* lxml, for efficent web scraping
* pandas, for data analysis tools (currently only uses pandas for exporting to CSV, more to come later)
* A decent CPU and internet for best performance, cryptoscraper uses multithreading to get around long wait times for requesting page data. By default, it uses 16 threads, if this is too much for your machine to handle, you can decrease it by changing the code under the function go(): ```python with Pool(16) as p:```, to a lower value, ```python with Pool(1) as p:```, a pool of 1 is like running the function without multithreading.
## Usage:
### Using cryptoscraper simply requires you to run generate_coins.py, this will add or update csv files of coins and their price data to a folder named "coins".
By default, cryptoscraper uses a function getCoins() to find the coins it will add to the coins folder. getCoins() has an attribute pages that tells it how many pages of CoinMarketCap it will scrape for coin urls. Each page contains a maximum of 100 coins. By default, this function only scrapes 1 page of 100 coins. To scrape more pages, modify the code under the function go():
```python
d = p.map(startCoin, getCoins(1))
```
to however many you want (12 in this example):
```python
d = p.map(startCoin, getCoins(12))
```
If you don't want batches of coins and would instead like to download all of the coins on the site, use the function getAllCoins() instead:
```python
d = p.map(startCoin, getAllCoins())
```
### The beauty of cryptoscraper is in its ability to automatically update an already existing coin folder.
If new coins enter the market or your page range, cryptoscraper will add those coins to your folder.
If older coins' price data ends at a few days ago, cryptoscraper will update those coins and add the prices that are missing between then and now.
