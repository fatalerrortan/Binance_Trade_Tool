import requests
import configparser

class Taapi:

    def __init__(self, config):

        # config = configparser.ConfigParser()
        # config.read('config.ini')
        self.api_host = config['taapi']['url']
        self._api_key = config['taapi']['api_key']

    def get_kdj(self, exchange: str, symbol: str, interval: str, period=9, signal=3, backtracks=2):
        
        api_url= '{}/kdj?secret={}&exchange={}&symbol={}&interval={}&period={}&signal={}&backtracks={}'.format(self.api_host, self._api_key, exchange, symbol, interval, period, signal, backtracks)
        result = requests.get(api_url).json()

        return result

    def get_typprice(self, exchange: str, symbol: str, interval: str, backtrack=1):
        
        api_url= '{}/typprice?secret={}&exchange={}&symbol={}&interval={}&backtrack={}'.format(self.api_host, self._api_key, exchange, symbol, interval, backtrack)
        result = requests.get(api_url).json()
        return result

    