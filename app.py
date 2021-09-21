from Binance import Binance
from Taapi import Taapi
import flask
from App_Logging import getLogger
import json
from tkinter import filedialog as fd
import time
import configparser

logger = getLogger('app.py')

def cancel_current_orders():

    current_orders = binance.get_open_orders()
    if not len(current_orders):
        return

    for order in current_orders:
        orderId = order["orderId"]
        symbol = order["symbol"]
        if_cancel = input("-> would u like to cancel this order? \r\n {} \r\n: ".format(order))
        if if_cancel.lower() == "yes":
            result = binance.cancel_order(symbol, orderId)
            logger.info("the current opened order {} - {} was canceled successfuly".format(orderId, symbol))
        else: continue 
    
if __name__ == '__main__':

    logger.info('app started')

    config_file = fd.askopenfilename(title="!Please select your config file! : ) ")

    config = configparser.ConfigParser()
    config.read(config_file)

    asset_list = list(input("please input involved assets with delimiter ',' and without whitespace: ").split(","))
    asset_dict = {}

    binance = Binance(config)

    # load all asset 
    balance = binance.get_account_info()   
    for currency in balance:
        if currency["asset"].lower() in asset_list:
            asset_dict[currency["asset"].lower()] = currency["free"]
            logger.info(currency)

    # cancel current opende orders
    cancel_current_orders()
    
    # load trade rules
    filename = fd.askopenfilename(title="!Please select a rule definition! : ) ")
    jsonObj = None
    with open(filename) as jsonFile:
        jsonObj = json.load(jsonFile)
        jsonFile.close()
    
    interval = input("pls input candle interval to determine btc typical price: ")

    logger.info("all applied rules")
    
    # 1 API request / 15 seconds
    Taapi = Taapi(config)
    for index, rule in jsonObj.items():
        btc_price = rule["btc"]
        altcoin_to_sell = float(rule["altcoin"])
        logger.info("Current Rule in USE! - when btc price is lower than {}, {}% of altcoin will be sold".format(btc_price, altcoin_to_sell*100))

        while True:
            current_btc_tp = Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtrack=1) 
            if float(current_btc_tp["value"]) <= float(btc_price):
                logger.warning("!!!current btc typical price {} is lower than current defined btc price {}. the orders below will be excuted!!!".format(current_btc_tp["value"], btc_price))
                
                for asset in asset_list:
                    # result = binance.place_order(symbol='{}usdt'.format(asset), side='sell', type='MARKET', quantity=488.6)
                    # logger.warning(result)
                    print("{}usdt and {}".format(asset, float(asset_dict[asset]) * altcoin_to_sell))

                break

        time.sleep(30)

    logger.warning("All preset prices have been triggered.")
    
    # print(binance.cancel_order(symbol='manausdt', order_id=194335224))
    # print(binance.get_order_detail(symbol='manausdt', order_id=194335224))


# app.config["DEBUG"] = True

# @app.route('/', methods=['GET'])
# def home():
#     return "<h1>Binance Trade Tool</h1>"

# @app.route('/api/v1/combiorders/create', methods=['GET'])
# def create():
#     return "<h1>Binance Trade Tool</h1>"

# @app.route('/api/v1/combiorders/orderlist', methods=['GET'])
# def orderlist():
#     return "<h1>Binance Trade Tool</h1>"

# @app.route('/api/v1/combiorders/cancel', methods=['GET'])
# def cancel():
#     return "<h1>Binance Trade Tool</h1>"

# app.run()