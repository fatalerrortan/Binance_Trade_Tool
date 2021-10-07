from Binance import Binance
import configparser
from decimal import Decimal

if __name__ == '__main__':
     
    config_file = "/Users/fatalerrortxl/Desktop/config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    binance = Binance(config)
    
    # result=binance.place_order(symbol='dogeusdt', side='buy', type='MARKET', quantity=100)
    print(result)