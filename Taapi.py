import aiohttp

class Taapi:

    def __init__(self, config):

        # config = configparser.ConfigParser()
        # config.read('config.ini')
        self.api_host = config['taapi']['url']
        self._api_key = config['taapi']['api_key']
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

    async def get_kdj(self, exchange: str, symbol: str, interval: str, period=9, signal=3, backtracks=2):
        
        api_url= '{}/kdj?secret={}&exchange={}&symbol={}&interval={}&period={}&signal={}&backtracks={}'.format(self.api_host, self._api_key, exchange, symbol, interval, period, signal, backtracks)
        # result = await requests.get(api_url).json()
        async with self.session.get(api_url) as resp:
            result = await resp.json()

        return result

    async def get_typprice(self, exchange: str, symbol: str, interval: str, backtracks: int):
        
        api_url= '{}/typprice?secret={}&exchange={}&symbol={}&interval={}&backtracks={}'.format(self.api_host, self._api_key, exchange, symbol, interval, backtracks)
        # result = await requests.get(api_url).json()
        async with self.session.get(api_url) as resp:
            result = await resp.json()

        return result



    