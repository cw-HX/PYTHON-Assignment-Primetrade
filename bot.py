import time
import hashlib
import hmac
import logging
import requests
from urllib.parse import urlencode

class BasicBot:
    """Simplified Binance Futures (USDT-M) Testnet trading bot using REST.

    Uses the Testnet base URL https://testnet.binancefuture.com and signed
    requests for private endpoints.
    """

    def __init__(self, api_key, api_secret, base_url="https://testnet.binancefuture.com", recv_window=5000, logger=None):
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')
        self.base_url = base_url.rstrip('/')
        self.recv_window = recv_window
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        self.logger = logger or logging.getLogger(__name__)

    def _sign(self, params: dict) -> dict:
        params = params.copy()
        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = self.recv_window
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(self.api_secret, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params

    def _request(self, method: str, path: str, params=None, signed=False):
        url = f"{self.base_url}{path}"
        params = params or {}
        if signed:
            params = self._sign(params)
        try:
            if method.upper() == 'GET':
                self.logger.debug("REQUEST GET %s params=%s", url, params)
                r = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'DELETE':
                self.logger.debug("REQUEST DELETE %s params=%s", url, params)
                r = self.session.delete(url, params=params, timeout=10)
            else:
                self.logger.debug("REQUEST %s %s params=%s", method.upper(), url, params)
                r = self.session.post(url, params=params, timeout=10)
            self.logger.debug("RESPONSE %s status=%s text=%s", url, r.status_code, r.text)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            self.logger.error("HTTP error for %s %s: %s", method, url, e)
            raise

    def place_market_order(self, symbol: str, side: str, quantity: float, reduce_only=False):
        """Place a MARKET futures order.

        side: 'BUY' or 'SELL'
        """
        path = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': float(quantity),
            'reduceOnly': str(reduce_only).lower()
        }
        return self._request('POST', path, params=params, signed=True)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, time_in_force: str='GTC', reduce_only=False):
        path = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'LIMIT',
            'timeInForce': time_in_force,
            'price': str(price),
            'quantity': float(quantity),
            'reduceOnly': str(reduce_only).lower()
        }
        return self._request('POST', path, params=params, signed=True)

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float, time_in_force: str='GTC', reduce_only=False):
        """Stop-Limit via STOP order (STOP + LIMIT fields).
        """
        path = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'STOP',
            'timeInForce': time_in_force,
            'price': str(price),
            'stopPrice': str(stop_price),
            'quantity': float(quantity),
            'reduceOnly': str(reduce_only).lower()
        }
        return self._request('POST', path, params=params, signed=True)

    def get_order(self, symbol: str, orderId: int=None, origClientOrderId: str=None):
        path = '/fapi/v1/order'
        params = {'symbol': symbol.upper()}
        if orderId is not None:
            params['orderId'] = int(orderId)
        if origClientOrderId is not None:
            params['origClientOrderId'] = origClientOrderId
        return self._request('GET', path, params=params, signed=True)

    def cancel_order(self, symbol: str, orderId: int=None, origClientOrderId: str=None):
        path = '/fapi/v1/order'
        params = {'symbol': symbol.upper()}
        if orderId is not None:
            params['orderId'] = int(orderId)
        if origClientOrderId is not None:
            params['origClientOrderId'] = origClientOrderId
        return self._request('DELETE', path, params=params, signed=True)
