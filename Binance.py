import requests
import hashlib
import hmac
import configparser
import time


class Binance:
    
    def __init__(self, config):
        
        # config = configparser.ConfigParser()
        # config.read('config.ini')
        # self.logger = logging.getLogger("root.{}".format(__name__))
        # self.ws_url = ws_url
        self.api_host = config['binance']['url']
        self._api_key = config['binance']['api_key']
        self._secret_key = bytes(config['binance']['secret_key'], "utf-8")
        self._headers = {
            "Accept": "*/*",
            'X-MBX-APIKEY': self._api_key
        }

    def get_account_info(self):

        request_url = self._prepare_request_data("/api/v3/account", "USER_DATA",{})
        balances = requests.get(request_url, headers=self._headers).json()['balances']
        
        result = []
        for balance in balances:
            if float(balance["free"]) != 0 or float(balance["locked"]) != 0:         
                result.append(balance)
    
        return result

    def place_order(self, symbol:str, side:str, type:str, quantity:float, price:float, stop_price:float, time_in_force:str, test_mode=None):
        
        params = {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": type.upper(),
                "timeInForce": time_in_force.upper(),
                "quantity": quantity,
                "price": price,
                "stopPrice": stop_price,
                "newOrderRespType": "RESULT"
            }
        endpoint = "/api/v3/order/test" if test_mode == True else "/api/v3/order"
        request_url = self._prepare_request_data(endpoint, "TRADE", params)
        result = requests.post(request_url, headers=self._headers).json()
        return result

    def cancel_order(self, symbol: str, order_id: int):

        data = {
                "symbol": symbol.upper(),
                "orderId": order_id
                }
        request_url = self._prepare_request_data("/api/v3/order", "TRADE", data)
        result = requests.delete(request_url, headers=self._headers).json()
        return result

    def get_order_detail(self, symbol: str, order_id: int):
    # "status":"EXPIRED",     {FILLED | NEW | EXPIRED(for FOK) | CANCELED}
    
        data = {
                "symbol": symbol.upper(),
                "orderId": order_id
                }
        request_url = self._prepare_request_data("/api/v3/order", "USER_DATA", data)
        result = requests.get(request_url, headers=self._headers).json()
        return result

    def get_open_orders(self):
        request_url = self._prepare_request_data("/api/v3/openOrders", "USER_DATA", {})
        result = requests.get(request_url, headers=self._headers).json()
        return result

    def _prepare_request_data(self, uri: str, auth_type: str, params: dict):
        
        if not auth_type:
            request_params = ""
            if params:
                request_params_dict = params
            
                for key in sorted(request_params_dict.keys()):
                    request_params += "{}={}&".format(key,request_params_dict[key])
            
            request_url = "{}{}?{}".format(self.api_host, uri, request_params)
        else:
            request_params_dict = {
                "timestamp": int(time.time()*1000)
            } 

            if params:
                request_params_dict = {**request_params_dict, **params}      
            
            request_params = ""
            for key in sorted(request_params_dict.keys()):
                request_params += "{}={}&".format(key,request_params_dict[key])

            signature = self._get_hmacSHA256_sigature(request_params[:-1])       
            request_url = "{}{}?{}signature={}".format(self.api_host, uri, request_params, signature)

        return request_url

    def _get_hmacSHA256_sigature(self, request_params: str):
        hash = hmac.new(self._secret_key, bytes(request_params, "utf-8"), hashlib.sha256).hexdigest()

        return hash


