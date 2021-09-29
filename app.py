from Binance import Binance
from Taapi import Taapi
import flask
from App_Logging import getLogger
import json
from tkinter import filedialog as fd
import time
import configparser
import sys
from decimal import Decimal

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

    # config_file = "/Users/fatalerrortxl/Desktop/config.ini"
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = fd.askopenfilename(title="!Please select your config file! : ) ")
    
    logger.info("the file {} is being used as api config!!!".format(config_file))

    config = configparser.ConfigParser()
    config.read(config_file)

    # asset_list = ["doge","reef","enj","vet"]
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
    # rule_def_file = "/Users/fatalerrortxl/Desktop/Binance_Trade_Tool/rules/test.json"
    try:
        rule_def_file = sys.argv[2]
    except IndexError:
        rule_def_file = fd.askopenfilename(title="!Please select a rule definition! : ) ")
    
    logger.info("the file {} is being used as trade rule!!!".format(rule_def_file))
    
    jsonObj = None
    with open(rule_def_file) as jsonFile:
        jsonObj = json.load(jsonFile)
        jsonFile.close()
    
    interval = input("pls input candle interval to determine btc typical price: ")
    
    # 1 API request / 15 seconds
    Taapi = Taapi(config)
    for index, rule in jsonObj.items():
        btc_price = rule["btc"]
        altcoin_to_sell = Decimal(rule["altcoin"])
        logger.info("Current Rule in USE! - when btc price is lower than {}, {}% of altcoin will be sold".format(btc_price, altcoin_to_sell*100))

        while True:
            time.sleep(60)
            current_btc_tp = Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtrack=1)

            if Decimal(current_btc_tp["value"]) <= Decimal(btc_price):
                logger.warning("!!!current btc typical price {} is lower than current defined btc price {}. the orders below will be excuted!!!".format(current_btc_tp["value"], btc_price))

                for asset in asset_list:
                    precision = int(str(Decimal(binance.getExchangeInfo("{}usdt".format(asset))["symbols"][0]["filters"][2]["stepSize"]).normalize())[::-1].find("."))
                    
                    ist_qty = Decimal(binance.get_account_info(asset)["free"])
                    ist_qty = round(ist_qty, precision) if not precision == -1 else round(ist_qty, 0)
                    
                    soll_qty = Decimal(asset_dict[asset]) * altcoin_to_sell
                    soll_qty = round(soll_qty, precision) if not precision == -1 else round(soll_qty, 0)

                    logger.info("ist qty: {} and soll qty {}".format(ist_qty, soll_qty))

                    qty = soll_qty if soll_qty <= ist_qty  else ist_qty

                    result = binance.place_order(symbol='{}usdt'.format(asset), side='sell', type='MARKET', quantity=qty)
                    logger.warning (result)
                    logger.info("{}usdt and {}".format(asset, qty))
               
                break
            
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