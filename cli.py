import os
import argparse
import logging
from dotenv import load_dotenv
from bot import BasicBot

load_dotenv()

LOG_FILE = os.getenv('BOT_LOG_FILE', 'bot.log')
logging.basicConfig(level=logging.INFO, filename=LOG_FILE, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('basicbot')
logger.setLevel(logging.DEBUG)


def positive_float(value):
    try:
        f = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid float value: {value}")
    if f <= 0:
        raise argparse.ArgumentTypeError("Value must be positive")
    return f


def parse_args():
    p = argparse.ArgumentParser(description='Place orders on Binance Futures Testnet (USDT-M).')
    p.add_argument('--api-key', help='Binance API key (or set BINANCE_API_KEY env var)')
    p.add_argument('--api-secret', help='Binance API secret (or set BINANCE_API_SECRET env var)')
    p.add_argument('--base-url', default='https://testnet.binancefuture.com', help='Testnet base URL')
    p.add_argument('order_type', choices=['market', 'limit', 'stop-limit'], help='Order type')
    p.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    p.add_argument('symbol', help='Trading pair symbol, e.g., BTCUSDT')
    p.add_argument('quantity', type=positive_float, help='Quantity to buy/sell')
    p.add_argument('--price', type=positive_float, help='Limit price (required for limit and stop-limit)')
    p.add_argument('--stop-price', type=positive_float, help='Stop trigger price (required for stop-limit)')
    return p.parse_args()


def main():
    args = parse_args()
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    if not api_key or not api_secret:
        logger.error('API key or secret not provided. Set env vars or pass --api-key/--api-secret.')
        print('Missing API credentials. Use --api-key/--api-secret or set env variables.')
        return

    bot = BasicBot(api_key, api_secret, base_url=args.base_url, logger=logger)

    try:
        if args.order_type == 'market':
            resp = bot.place_market_order(args.symbol, args.side, args.quantity)
        elif args.order_type == 'limit':
            if not args.price:
                raise ValueError('Limit orders require --price')
            resp = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
        elif args.order_type == 'stop-limit':
            if not args.price or not args.stop_price:
                raise ValueError('Stop-limit requires --price and --stop-price')
            resp = bot.place_stop_limit_order(args.symbol, args.side, args.quantity, args.price, args.stop_price)
        else:
            raise ValueError('Unsupported order type')

        logger.info('Order placed: %s', resp)
        print('Order response:')
        print(resp)
    except Exception as e:
        logger.exception('Error placing order: %s', e)
        print('Error:', e)


if __name__ == '__main__':
    main()
