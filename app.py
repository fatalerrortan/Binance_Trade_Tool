from tkinter.constants import NO
from Binance import Binance
from Taapi import Taapi
from App_Logging import getLogger
import json
from tkinter import filedialog as fd
import configparser
import sys
from decimal import Decimal
import asyncio
import traceback
import math
import json
import os

logger = getLogger('app.py')

async def cancel_current_orders(binance):

    current_orders = await safe_execute(lambda: binance.get_open_orders())
    if not len(current_orders):
        return

    for order in current_orders:
        orderId = order["orderId"]
        symbol = order["symbol"]
        if_cancel = input(f"[app] would u like to cancel this order? \r\n {order} \r\n: ")
        if if_cancel.lower() == "yes":
            result = await safe_execute(lambda: binance.cancel_order(symbol, orderId))
            logger.info(f"[app] the current opened order {orderId} - {symbol} was canceled successfuly")
        else: continue 

async def safe_execute(func):

    for i in range(0,9):
        while True:
            try:
                result = await func()
                if "error" in result:
                    raise Exception(result["error"])
            except Exception as e:
                # logger.error(e)
                logger.error(traceback.format_exc())
                await asyncio.sleep(15)
                continue
            return result
            break

async def sell(sell_rule, binance, Taapi, sell_asset_dict, interval, test_mode):

    if len(sell_rule) == 0:
        logger.warning("[sell] sell rule not found, sell function will not be executed!")
        return
    
    binance_coins = [ x for x in sell_asset_dict.keys()]

    for index, rule in sell_rule.items():

        ruled_btc_price = rule["btc"]
        altcoins_to_sell = rule["altcoin"]
        filtered_altcoins_to_sell = {**altcoins_to_sell}
        is_active = bool(rule["active"])
        
        if not is_active:
            logger.warning(f"[sell] the current sell rule {ruled_btc_price} is inactive, skipping to the next sell rule!")
            continue
        
        logger.warning(f"[sell] Current Sell Rule in USE! - when btc price is lower than {ruled_btc_price}, the followed altcoin will be sold")
      
        for coin, percentage in altcoins_to_sell.items():

            if coin not in binance_coins:
                logger.warning(f"[sell] the in rule defined {coin} is not listed in the binance asset. the sell plan of this coin will be canceled")
                del filtered_altcoins_to_sell[coin]
                continue

            logger.warning(f"[sell] -> {percentage * 100} % of {coin} will be sold")

        while True:
            await asyncio.sleep(60)
            current_btc_tp = await safe_execute(lambda: Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtracks=3)) 
            current_btc_tp_1_2 = (current_btc_tp[1]["value"] + current_btc_tp[2]["value"]) / 2
            current_btc_tp_0 = current_btc_tp[0]["value"]

            logger.info(f"[sell] average btc typical price of last two {interval} is {current_btc_tp_1_2} usdt.")
            
            if Decimal(current_btc_tp_1_2) < Decimal(ruled_btc_price):
                await asyncio.sleep(60)
                current_btc_price = Decimal(await safe_execute(lambda: binance.get_current_pirce("btc")))
                if current_btc_price < Decimal(ruled_btc_price):
                    
                    logger.warning(f"[sell] the both average btc typical price of last two {interval} {current_btc_tp_1_2} usdt and the current btc price {current_btc_price} usdt are lower than the currently rule {ruled_btc_price} usdt. Sell right NOW!!!")

                    for coin, percentage in filtered_altcoins_to_sell.items():

                        asset_pair = coin+"usdt"
                        raw_precision = await safe_execute(lambda: binance.getExchangeInfo(asset_pair))
                        raw_precision = raw_precision["symbols"][0]["filters"][2]["stepSize"]
                        precision = int(str(Decimal(raw_precision).normalize())[::-1].find("."))

                        ist_qty = await safe_execute(lambda: binance.get_account_info(coin))
                        ist_qty = Decimal(ist_qty["free"]) 
                        ist_qty = math.floor(ist_qty * 10 ** precision) / 10 ** precision if not precision == -1 else int(ist_qty)
                        
                        soll_qty = Decimal(sell_asset_dict[coin]) * Decimal(percentage)
                        soll_qty = math.floor(soll_qty * 10 ** precision) / 10 ** precision if not precision == -1 else int(soll_qty)
                        
                        qty = soll_qty if soll_qty <= ist_qty  else ist_qty

                        result = await safe_execute(lambda: binance.place_order(symbol=asset_pair, side='sell', type='MARKET', test_mode=test_mode, quantity=qty))
                        logger.warning(result)
                        logger.warning(f"[sell] {percentage * 100} % {coin} - {qty} {coin} was sold!!!")
                    # break while loop
                    break 
                
            
    logger.warning("[sell] All preset BTC typical prices have been triggered.")

async def usdt_deposit(binance: object, test_mode): 
    
    while True:
            current_usdt = await safe_execute(lambda: binance.get_account_info("usdt"))    
            current_usdt = Decimal(current_usdt["free"])
            if test_mode:
                current_usdt = 100000000
            if current_usdt < 10:
                logger.info(f"[buy] current usdt remain {current_usdt} usdt is lower than 10 usdt. the buy function will not be executed until sell orders are placed, reloading usdt remain in 60 sec")
                await asyncio.sleep(60)  
            else: 
                logger.info(f"[buy] current usdt remain {current_usdt} usdt. the buy function is working.")
                return current_usdt

# async def buy_backup(buy_rule, binance, Taapi, interval, test_mode):
    
    # check if buy rule of the json file is empty? if true terminate the buy coroutine
    if len(buy_rule) == 0:
        logger.warning("[buy] buy rule not found, buy function will not be executed!")
        return
    
    current_usdt = await usdt_deposit(binance, test_mode)

    altcoin_before = None
    high_triggered = None

    for index, rule in buy_rule.items():

        high, low = Decimal(rule["btc"][0]), Decimal(rule["btc"][1])
        altcoin = rule["altcoin"]

        if altcoin_before:

            for coin, percentage in altcoin_before.items():
                if coin in altcoin:
                    altcoin[coin] = Decimal(altcoin[coin]) + Decimal(percentage)
                else:
                    altcoin[coin] = Decimal(percentage)     
                    
        logger.warning("[buy] Current Buy Rule in USE! - when the high price {} usdt will be double triggered in the interval high {} ~ low {} usdt, the following buy orders will be executed!".format(high, high, low))
      
        for coin, percentage in altcoin.items():
            logger.warning("[buy] -> {} % of usdt will be used to buy {}".format(percentage * 100, coin))

        while True:

            await asyncio.sleep(60)
      
            current_btc_price = Decimal(await safe_execute(lambda: binance.get_current_pirce("btc")))

            if current_btc_price > high:

                if high_triggered:
                    
                    current_btc_tp = await safe_execute(lambda: Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtracks=3)) 
                    current_btc_tp_1_2 = Decimal((current_btc_tp[1]["value"] + current_btc_tp[2]["value"]) / 2)

                    if current_btc_tp_1_2 > high:
                        logger.warning("[buy] the both average btc typical price of last two {} {} usdt and current btc price {} usdt are higher than the current high {} usdt aigain! Buy right NOW!!!".format(interval, current_btc_tp_1_2, current_btc_price, high))

                        for coin, percentage in altcoin.items():

                            asset_pair = coin+"usdt"
                            ist_usdt = int(await usdt_deposit(binance, test_mode))
                            soll_usdt = int(current_usdt * Decimal(percentage)) 

                            usdt = soll_usdt if soll_usdt <= ist_usdt else ist_usdt

                            if usdt <= 10:
                                logger.warning("[buy] pre defined {} % usdt - {} usdt is lower that 10 usdt, so not enough to buy {}, the order will be executed with 10 usdt!!!".format(percentage * 100 ,ist_usdt, coin))
                                usdt = 10
                                
                            result = await safe_execute(lambda: binance.place_order(symbol=asset_pair, side='buy', type='MARKET', test_mode=test_mode, quoteOrderQty=usdt))
                            logger.warning(result)
                            logger.warning("[buy] {} % usdt - {} usdt - was used to buy {}!!!".format(percentage * 100 ,ist_usdt, coin))

                        altcoin_before = None
                        high_triggered = None
                        break
                    else: continue
                else: 
                    logger.info("[buy] the current high {} is not triggered yet!".format(high))
                    continue
        
            if current_btc_price <= high and current_btc_price >= low:
                
                logger.info("[buy] the current btc price {} usdt is between the current high {} and low {}. waiting for Buy signal!".format(current_btc_price, high, low))
                high_triggered = True
                continue

            if current_btc_price < low:

                logger.warning("[buy] the current btc price {} usdt is lower than the current low {} usdt. skipping to the next interval rule!!!".format(current_btc_price, low))
                high_triggered = True
                altcoin_before = altcoin
                break             
    
    logger.warning("[buy] All preset prices have been triggered, the next buy round will being launched!")

    await buy(buy_rule, binance, Taapi, interval, test_mode)

async def buy(buy_rule, binance, Taapi, interval, test_mode):
    # check if buy rule of the json file is empty? if true terminate the buy coroutine
    if len(buy_rule) == 0:
        return logger.warning("[buy] buy rule not found, buy function will not be executed!")
    
    
    last_index = None
    bottom_index = int(len(buy_rule))

    while True:

        await asyncio.sleep(60)
        current_usdt = await usdt_deposit(binance, test_mode)
        current_btc_price = Decimal(await safe_execute(lambda: binance.get_current_pirce("btc")))
        for index, rule in buy_rule.items():

            low, high = Decimal(rule["btc"][0]), Decimal(rule["btc"][1])
            is_active = bool(rule["active"])
            
            if not is_active:
                logger.warning(f"[buy] the current buy rule with low {low} and high {high} is inactive, skipping to the next buy rule!")
                continue

            current_index = int(index)
            
            if low < current_btc_price < high:
                
                if last_index:
                    if last_index <= current_index:
                        
                        logger.info(f"[buy] the current btc price {current_btc_price} is located in low {low} and high {high}, the last rule index {last_index} <= current rule index {current_index}, so waiting for buy signal!")
                        last_index = current_index
                        break
           
                    elif last_index > current_index:
                        
                        logger.warning(f"[buy] the current btc price {current_btc_price} is located in low {low} and high {high}, the last rule index {last_index} > current rule index {current_index}, continue to compare current btc typical price!")                       

                        current_btc_tp = await safe_execute(lambda: Taapi.get_typprice(exchange='binance', symbol='BTC/USDT', interval=interval, backtracks=1)) 
                        current_btc_tp = Decimal(current_btc_tp[0]["value"])
                        
                        if not current_btc_tp > low:
                            logger.warning(f"[buy] the current btc typical price {current_btc_tp} < current low {low}, it wasn't a real bull break. continue...")
                            break                        
                        
                        logger.warning(f"[buy] the current btc typical price {current_btc_tp} > current low {low}, the following buy will be executed immediately!!!")                       

                        percentage = Decimal(rule["percentage"])
                        usdt_current_interval = current_usdt * percentage
                        altcoins = rule["altcoin"]
                        for coin, pct in altcoins.items():
                            asset_pair = coin+"usdt"
                            soll_usdt = int(usdt_current_interval * Decimal(pct)) 
                            usdt = soll_usdt if soll_usdt >= 10 else None
                            if usdt:
                                result = await safe_execute(lambda: binance.place_order(symbol=asset_pair, side='buy', type='MARKET', test_mode=test_mode, quoteOrderQty=usdt))
                                logger.warning(result)
                                logger.warning(f"[buy] {pct * 100} % usdt - {usdt} usdt - was used to buy {coin}!!!")
                            else:
                                logger.warning(f"[buy] quoteOrderQty of {coin} order is {soll_usdt} usdt, lower than 10 usdt, skipping to the next coin!")                       
                        last_index = current_index
                        break
                else:
                    logger.info(f"[buy] the current btc price {current_btc_price} and the last index was not initilized, waiting for buy signal!")
                    last_index = current_index
                    break
            
            elif current_index == 1 and current_btc_price > high:

                logger.info(f"[buy] the current btc price {current_btc_price} is !above! the all rule intervals, waiting for buy signal!!")
                break

            elif current_index == bottom_index and current_btc_price < low:

                logger.info(f"[buy] the current btc price {current_btc_price} is !below! the all rule intervals, waiting for buy signal!!")
                break
        
            # else: 
            #     logger.error(f"[buy] Exception Case found -> current btc price {current_btc_price}")

async def trading(data=None):

    if data:
        taapi_api_url = data["taapi_api_url"] 
        taapi_api_key = data["taapi_api_key"]
        binance_api_key = data["binance_api_key"]
        binance_secret_key = data["binance_secret_key"]
        binance_api_url = data["binance_api_url"]
        run_mode = data["run_mode"]  # yes -> prod, no->test
        trade_rule = json.loads(data["trade_rule"].file.read())
        candle_interval = data["candle_interval"]
        current_orders = data["current_orders"] # yes -> check, no->skip

    if not data:
        run_mode = input("[app] would u like to start a productive RUN? input 'yes' for productive run or any else for test mode!\r\n: ") 

    if run_mode.lower() == "yes":
        test_mode = None
    else:
        test_mode = True
    
    logger.info("[app] the run will be in !!! {} !!! mode executed".format("Productive" if test_mode == None else "TEST"))
    
    if not data:
        try:
            config_file = sys.argv[1]
        except IndexError:
            config_file = fd.askopenfilename(title="!Please select your config file! : ) ")
        
        logger.info(f"[app] the file {config_file} is being used as api config!!!")

        config = configparser.ConfigParser()
        config.read(config_file)
    else:
        config = {
            "binance":{
                "url": binance_api_url,
                "api_key": binance_api_key,
                "secret_key": binance_secret_key
            },
            "taapi":{
                "url": taapi_api_url,
                "api_key": taapi_api_key,
            }
        }
    
    sell_asset_dict = {}

    binance = Binance(config)

    # load all asset 
    balance = await safe_execute(lambda: binance.get_account_info())

    for currency in balance:
        
        sell_asset_dict[currency["asset"].lower()] = currency["free"]
        logger.info(currency)
        
    if not data:
        # cancel current opende orders
        await cancel_current_orders(binance)
        # load trade rules
        try:
            rule_def_file = sys.argv[2]
        except IndexError:
            rule_def_file = fd.askopenfilename(title="!Please select a rule definition! : ) ")
        
        logger.info(f"[app] the file {rule_def_file} is being used as trade rule!!!")
        
        jsonObj = None
        with open(rule_def_file) as jsonFile:
            jsonObj = json.load(jsonFile)
            jsonFile.close()
    else:
        jsonObj = trade_rule
    
    if not data:
        interval = input("[app] pls input candle interval to determine btc typical price: ")
    else:
        interval = candle_interval

    Taapi_api = Taapi(config)

    await asyncio.gather(
                            sell(jsonObj["sell"], binance, Taapi_api, sell_asset_dict, interval, test_mode), 
                            buy(jsonObj["buy"], binance, Taapi_api, interval, test_mode)
                        )

def app_close():
    logger.info("[app] app is stopping!!!")
    for t in asyncio.all_tasks():
        task_name = str(t.get_coro())
        if "buy" in task_name or "sell" in task_name:
            try:
                t.cancel()
            except asyncio.CancelledError:
                logger.info("[app] Sell and Buy functions are being cancelled now")

if __name__ == '__main__':
    logger.info('[app] app is launching!!!')
    logger.info('[app] server is launching!!!')
    try:
        # os.system('python server.py')
        asyncio.run(trading())
    except Exception as e:
        logger.error(traceback.format_exc())