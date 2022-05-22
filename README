
# Automatic Binance Trade Tool
a tool to trade crypto currency automatically in binance according to your own defined events and rules, which will be triggerd by compositive comparison using current, average and typical prices.

## Acknowledgements

 - Your own trade rules and events should be written in json and placed in the directory "rules". the example below might help you understand how to accomplish it 
    
```json
{   
    "sell": {        
        "1": { 
            "active": 1,
            "btc": 58800,
            "altcoin": {
                "doge": 0.1,
                "fil": 0.1,
                "theta":0.1,
                "icp":0.1
            }
        },
        "2": { 
            "active": 1,
            "btc": 44800,
            "altcoin": {
                "fil": 0.05,
                "doge":0.05
            }
        },
        "3": { 
            "active": 0,
            "btc": 42000,
            "altcoin": {
                "fil": 0.05,
                "doge":0.05
            }
        }
    },
    "buy": {}       
}
```
- In the sell block each child element corresponds to a set of our sell event and rule.
    - **index 1 ~ 3**: the keys of the sell child elements specifies the order in which the trade events and rules are triggered.
    - **active**: {1 | 0}: indicates if the trade event and rule of this block is active. 1 -> active, 0 -> inactive, which will be skipped
    - **btc**: wenn both the average BTC typical price of last two periods and the current BTCUSDT price are lower than the here defined BTCUSDT prices, the coins inside the block "altcoin" will be sold in USDT.
        - the value of the period will be asked at the beginning of programm run
    - **altcoin**: the coins that are written in this block will be sold according to the assigned percentage, once the trade event defined before is triggered. 
- If the entire sell block is empty, the program will not perform any sell transactions and continue to read the buy transaction logic, see below
```json
{   
    "sell": {},
    "buy": {
        "1": {
            "active": 1,
            "btc": [29700, 32890],
            "percentage": 0.5,
            "altcoin": {
                "doge": 0.7,
                "fil": 0.1,
                "theta": 0.1,
                "icp": 0.1
            }
        },    
        "2": {
            "active": 0,
            "btc": [28900, 29700],
            "percentage": 0.5,
            "altcoin": {
                "doge": 0.7,
                "fil": 0.1,
                "theta": 0.1,
                "icp": 0.1
            }
        },
        "3": {
            "active": 0,
            "btc": [54263, 54867],
            "percentage": 0.3,
            "altcoin": {
                "doge": 0.7,
                "fil": 0.1,
                "mana": 0.2
            }
        }
    }       
}
```
- In the buy block each child block corresponds to a set of our buy event and rule.
    - **active**: see the same attribute in the sell block
    - **btc**: this attribute expect an interval of the BTCUSDT. When the current BTCUSDT first breaks down the the range and then returns to this range from bottom and simultaneously the current typical btc price is also within this range, x% of USDT will be used to buy the coins that were written in the "altcoin" block.
    - **percentage**: the value of this attribute specifies **x%** of USDT
    - **altcoin**: the coins that are written in this block will be bought according to the assigned percentage, once the trade event defined before is triggered.
- Similarly, the program will not perform any buy transactions, if the entire buy block is empty.

```json
[taapi]
url = https://api.taapi.io
api_key = 

[binance]
url = https://api.binance.com
api_key = 
secret_key = 
```
- There is a config.ini in the root directory in which the taapi api url and the binance api url were pre-defined to serve the program. accordingly you need to place your own api and secret key in this file.
- TAAPI.IO https://taapi.io/ is a straightforward REST API and price data provider for fetching popular Technical Analysis Indicator Data, which is used by this program to detect trade event.
    - register an account and choose the basic service. It is free and enough for the usage of this program

## Release

Please see the release page for details


## Usage

1. Just double click the program that you downloaded from the release page. then a console will popup to ask you to specify the run mode, productive or test? in test mode the program will treat your own SELL event and rules based on your real asset on Binance but not really do any transactions. For your Buy events and rules the program will setup a virtual account you with 100,000,000 USDT. so feel free to test your crazy ideas by choosing the Test Mode.
![App Screenshot](https://github.com/fatalerrortan/Binance_Trade_Tool/blob/dev_api_websocket/pic/test_mode.png?raw=true)

2. after choosing the run mode two file selectors will popup to help you specifing your config.ini and rule file respectively.Immediately afterwards, your assets on the Binance will be read and printed out on the screen
![App Screenshot](https://github.com/fatalerrortan/Binance_Trade_Tool/blob/dev_api_websocket/pic/config.png?raw=true)

3. You will then be asked to specify a candlestick timeframe on which your events and rules should be triggered. The k-line movements in different time frames can be found on tradingview.com. The currently accepted parameters are 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M. The recommended value is 5m. then the current Rules in USE will be printed out on the screen.
![App Screenshot](https://github.com/fatalerrortan/Binance_Trade_Tool/blob/dev_api_websocket/pic/timeframe.png?raw=true)

4. (optional) the program can also be executed from terminal with three arguments 

example ``` ./app /home/test/config.ini ../rule.json debug ```
   
    - arg 1: directorty of the config.ini 
    - arg 2: directorty of your trade rules 
    - arg 3: "debug" - in the debug mode all app output will be written in the log/0000.log, otherwise only the transaction records when and what was be traded.

example ``` ./app /home/test/config.ini ../rule.json debug ```


## Screenshots

![App Screenshot](https://github.com/fatalerrortan/Binance_Trade_Tool/blob/dev_api_websocket/pic/screenshot.png?raw=true)


## License

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)


## Authors

- [@fatalerrortan](https://github.com/fatalerrortan)


## Donation

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=5W6RCYTBVJYZC)