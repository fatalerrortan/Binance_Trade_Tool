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
import asyncio
import traceback

logger = getLogger('app.py')

async def cancel_current_orders(binance):

    current_orders = await safe_execute(lambda: binance.get_open_orders())
    if not len(current_orders):
        return

    for order in current_orders:
        orderId = order["orderId"]
        symbol = order["symbol"]
        if_cancel = input("-> would u like to cancel this order? \r\n {} \r\n: ".format(order))
        if if_cancel.lower() == "yes":
            result = await safe_execute(lambda: binance.cancel_order(symbol, orderId))
            logger.info("the current opened order {} - {} was canceled successfuly".format(orderId, symbol))
        else: continue 

async def safe_execute(func):

    for i in range(0,9):
        while True:
            try:
                result = await func()
            except Exception as e:
                # logger.error(e)
                logger.error(traceback.format_exc())
                await asyncio.sleep(15)
                continue
            return result
            break

async def sell(sell_rule, binance, Taapi, sell_asset_dict, interval):
    
    for index, rule in sell_rule.items():
        btc_price = rule["btc"]
        altcoins_to_sell = rule["altcoin"]
        
        logger.info("[sell] Current Rule in USE! - when btc price is lower than {}, the followed altcoin will be sold".format(btc_price))
      
        for coin, percentage in altcoins_to_sell.items():
        
            logger.info("[sell] > {} % of {} will be sold".format(percentage * 100, coin))

        while True:
            await asyncio.sleep(15)
            current_btc_tp = await safe_execute(lambda: Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtrack=1)) 
            logger.debug("typical price of last {} is {}".format(interval, current_btc_tp))
            if Decimal(current_btc_tp["value"]) <= Decimal(btc_price):
                logger.warning("[sell] current btc typical price {} is lower than current defined btc price {}. the orders below will be excuted!!!".format(current_btc_tp["value"], btc_price))

                for coin, percentage in altcoins_to_sell.items():

                    asset_pair = coin+"usdt"
                    raw_precision = await safe_execute(lambda: binance.getExchangeInfo(asset_pair))
                    raw_precision = raw_precision["symbols"][0]["filters"][2]["stepSize"]
                    precision = int(str(Decimal(raw_precision).normalize())[::-1].find("."))

                    ist_qty = await safe_execute(lambda: binance.get_account_info(coin))
                    ist_qty = Decimal(ist_qty["free"])
                    ist_qty = round(ist_qty, precision) if not precision == -1 else round(ist_qty, 0)

                    soll_qty = Decimal(sell_asset_dict[coin]) * Decimal(percentage)
                    soll_qty = round(soll_qty, precision) if not precision == -1 else round(soll_qty, 0)

                    qty = soll_qty if soll_qty <= ist_qty  else ist_qty

                    result = await safe_execute(lambda: binance.place_order(symbol=asset_pair, side='sell', type='MARKET', quantity=qty, test_mode=True))
                    logger.warning(result)
                    logger.warning("[sell] > {} % {} - {} was sold!!!".format(percentage * 100 ,coin, qty))
               
                break
            
    logger.warning("[sell] All preset prices have been triggered.")

async def buy():
    logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Buy Func would be called!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    pass

async def trading():
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = fd.askopenfilename(title="!Please select your config file! : ) ")
    
    logger.info("the file {} is being used as api config!!!".format(config_file))

    config = configparser.ConfigParser()
    config.read(config_file)
    
    sell_asset_dict = {}

    binance = Binance(config)

    # load all asset 
    balance = await safe_execute(lambda: binance.get_account_info())

    for currency in balance:
        
        sell_asset_dict[currency["asset"].lower()] = currency["free"]
        logger.info(currency)

    # cancel current opende orders
    await cancel_current_orders(binance)
    
    # load trade rules
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

    Taapi_api = Taapi(config)

    await asyncio.gather(
                            sell(jsonObj["sell"], binance, Taapi_api, sell_asset_dict, interval), 
                            buy()
                        )
    
    
if __name__ == '__main__':
    logger.info('app started')
    asyncio.run(trading())


 
