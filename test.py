from Binance import Binance
import configparser
from decimal import Decimal

if __name__ == '__main__':
     
    config_file = "/Users/fatalerrortxl/Desktop/config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    binance = Binance(config)
    
    aaa = 123.1200322
    
    result = binance.getExchangeInfo('reefusdt')
    # result_ = binance.place_order(symbol="reefusdt",side="sell", type="market", quantity=100.1, test_mode=True)
    # print(result_)
    num = result["symbols"][0]["filters"][2]["stepSize"]
    print(num)
    print(Decimal(num).normalize())
    d = int(str(Decimal(num).normalize())[::-1].find("."))
    print(d)
    
    # precision = str(Decimal(binance.getExchangeInfo('enjusdt')["symbols"][0]["filters"][2]["stepSize"]).normalize())[::-1].find(".")

    print(round(aaa, 0))