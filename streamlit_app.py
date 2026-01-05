import os
import logging
from dotenv import load_dotenv
import streamlit as st
from bot import BasicBot

load_dotenv()

# Simple in-memory log handler that writes to Streamlit session state
class StreamlitHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        if 'logs' not in st.session_state:
            st.session_state['logs'] = []
        st.session_state['logs'].append(msg)


def get_logger():
    logger = logging.getLogger('basicbot_streamlit')
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        h = StreamlitHandler()
        h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(h)
    return logger

logger = get_logger()

st.title('Simplified Binance Futures Testnet Bot')

with st.sidebar:
    st.header('API Credentials')
    api_key = st.text_input('API Key', value=os.getenv('BINANCE_API_KEY') or '')
    api_secret = st.text_input('API Secret', value=os.getenv('BINANCE_API_SECRET') or '', type='password')
    base_url = st.text_input('Base URL', value='https://testnet.binancefuture.com')
    dry_run = st.checkbox('Dry run (no network calls)', value=True)
    st.markdown('---')
    st.markdown('Logs')
    if 'logs' in st.session_state:
        st.text('\n'.join(st.session_state['logs'][-50:]))
    else:
        st.text('No logs yet')

st.header('Order')
col1, col2 = st.columns(2)
with col1:
    order_type = st.selectbox('Order Type', ['market', 'limit', 'stop-limit'])
    side = st.selectbox('Side', ['BUY', 'SELL'])
    symbol = st.text_input('Symbol', value='BTCUSDT')
with col2:
    quantity = st.number_input('Quantity', min_value=0.00000001, value=0.001, format='%f')
    price = st.number_input('Price (for limit/stop-limit)', min_value=0.0, value=0.0, format='%f')
    stop_price = st.number_input('Stop Price (for stop-limit)', min_value=0.0, value=0.0, format='%f')

if st.button('Place Order'):
    if not api_key or not api_secret:
        st.error('API credentials are required (set in sidebar or .env).')
    else:
        bot = BasicBot(api_key, api_secret, base_url=base_url, logger=logger)
        # stub network calls if dry_run
        if dry_run:
            def fake_request(method, path, params=None, signed=False):
                logger.info('DRY-RUN %s %s %s signed=%s', method, path, params, signed)
                return {
                    'orderId': 999999999,
                    'symbol': params.get('symbol'),
                    'status': 'NEW',
                    'side': params.get('side'),
                    'type': params.get('type'),
                    'origQty': params.get('quantity'),
                    'price': params.get('price', ''),
                    'clientOrderId': 'streamlit-dryrun'
                }
            bot._request = fake_request

        try:
            if order_type == 'market':
                resp = bot.place_market_order(symbol, side, quantity)
            elif order_type == 'limit':
                if price <= 0:
                    st.error('Limit orders require a positive `Price`.')
                    raise ValueError('Price required')
                resp = bot.place_limit_order(symbol, side, quantity, price)
            elif order_type == 'stop-limit':
                if price <= 0 or stop_price <= 0:
                    st.error('Stop-limit orders require positive `Price` and `Stop Price`.')
                    raise ValueError('Price/StopPrice required')
                resp = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
            else:
                st.error('Unsupported order type')
                raise ValueError('Unsupported')

            st.success('Order placed')
            st.json(resp)
            logger.info('Order response: %s', resp)
        except Exception as e:
            logger.exception('Error placing order: %s', e)
            st.error(f'Error placing order: {e}')

st.markdown('---')
st.header('Recent Logs')
if 'logs' in st.session_state:
    for line in st.session_state['logs'][-100:]:
        st.text(line)
else:
    st.text('No logs yet')
