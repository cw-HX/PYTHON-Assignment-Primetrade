# Simplified Binance Futures Testnet Bot

This project provides a small Python bot that places market, limit, and stop-limit orders on Binance Futures Testnet (USDT-M) using signed REST calls.

Setup

1. Register and activate Binance Futures Testnet at https://testnet.binancefuture.com and generate API credentials.
2. Copy `.env.example` to `.env` and add your `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

Usage

Place a market order:

```bash
python cli.py market BUY BTCUSDT 0.001
```

Place a limit order:

```bash
python cli.py limit SELL BTCUSDT 0.001 --price 30000
```

Place a stop-limit order:

```bash
python cli.py stop-limit BUY BTCUSDT 0.001 --price 31000 --stop-price 30950
```

Notes

- All requests use the Testnet base URL `https://testnet.binancefuture.com`.
- Logs are written to `bot.log` by default.
- This is a simplified example—use responsibly on testnet before moving to live trading.

Optional

- To add TWAP, Grid, or a Streamlit UI, add request and I will add those next.
