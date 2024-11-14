from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import time
import json
import ccxt

app = Flask(__name__)
CORS(app)

# Coinbase price fetch
def get_coinbase_price():
    url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    try:
        response = requests.get(url)
        data = response.json()
        coinbase_price = float(data['data']['amount'])
        return coinbase_price
    except Exception as e:
        print(f"Error fetching price data from Coinbase: {e}")
        return None

# CoinGecko price fetch
def get_coingecko_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        coingecko_price = data['bitcoin']['usd']
        return coingecko_price
    except Exception as e:
        print(f"Error fetching price data from CoinGecko: {e}")
        return None

# Gemini price fetch
def get_gemini_price():
    # Initialize exchange instance
    try:
        exchange = ccxt.gemini()
        # Define the trading symbol
        symbol = 'BTC/USD'  # Gemini uses uppercase
        # Fetch order book data
        order_book = exchange.fetch_order_book(symbol)
        # Extract ask and bid prices
        gemini_bid = order_book['bids'][0][0]  # The price of the best bid order
        gemini_ask = order_book['asks'][0][0]  # The price of the best ask order
        
        return gemini_bid, gemini_ask
    except Exception as e:
        print(f"Error fetching price data from Gemini: {e}")
        return None, None

	       
 
# Kraken price fetch
def get_kraken_price():
    url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
    try:
        response = requests.get(url)
        data = response.json()
        kraken_bid = float(data['result']['XXBTZUSD']['b'][0])
        kraken_ask = float(data['result']['XXBTZUSD']['a'][0])
        return kraken_bid, kraken_ask
    except Exception as e:
        print(f"Error fetching price data from Kraken: {e}")
        return None, None

# Bitfinex price fetch
def get_bitfinex_price():
    url = "https://api.bitfinex.com/v1/pubticker/btcusd"
    try:
        response = requests.get(url)
        data = response.json()
        bitfinex_bid = float(data['bid'])
        bitfinex_ask = float(data['ask'])
        return bitfinex_bid, bitfinex_ask
    except Exception as e:
        print(f"Error fetching price data from Bitfinex: {e}")
        return None, None

# Function to fetch the ask and bid prices from OKX
def get_okx_price():
    url = "https://www.okx.com/api/v5/market/books?instId=BTC-USDT"  # Example symbol BTC-USDT
    try:
        response = requests.get(url)
        order_book = response.json()
       # okx_bid = float(data['data'][0]['bids'][0][0])  # Bid price
        #okx_ask = float(data['data'][0]['asks'][0][0])  # Ask price
        okx_ask = order_book['data'][0]['asks']
        okx_bid = order_book['data'][0]['bids']

        return bids, asks
    except Exception as e:
        print(f"Error fetching price data from OKX: {e}")
        return None, None

# KuCoin price fetch
def get_kucoin_price():
    url = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
    try:
        response = requests.get(url)
        data = response.json()
        kucoin_bid = float(data['data']['bestBid'])
        kucoin_ask = float(data['data']['bestAsk'])
        return kucoin_bid, kucoin_ask
    except Exception as e:
        print(f"Error fetching price data from KuCoin: {e}")
        return None, None

# Function to calculate the profit and percentage
def calculate_profit(buy_price, sell_price):
    profit = sell_price - buy_price
    profit_percentage = (profit / buy_price) * 100
    return profit, profit_percentage

# Flask route for Coinbase price
@app.route('/coinbase_price', methods=['GET'])
def coinbase_price():
    price = get_coinbase_price()
    return jsonify({'coinbase_price': price})

# Flask route for Kraken prices
@app.route('/kraken_price', methods=['GET'])
def kraken_price():
    bid, ask = get_kraken_price()
    return jsonify({'kraken_bid': bid, 'kraken_ask': ask})

# Flask route for Gemini prices
@app.route('/gemini_price', methods=['GET'])
def gemini_price():
    gemini_bid, gemini_ask = get_gemini_price()
    return jsonify({'gemini_bid': bid, 'gemini_ask': ask})

# Flask route for Bitfinex prices
@app.route('/bitfinex_price', methods=['GET'])
def bitfinex_price():
    bid, ask = get_bitfinex_price()
    return jsonify({'bitfinex_bid': bid, 'bitfinex_ask': ask})

# Flask route for OKX prices
#@app.route('/okx_price', methods=['GET'])
#def okx_price():
   # bid, ask = get_okx_price()
   # return jsonify({'okx_bid': bid, 'okx_ask': ask})

# Flask route for KuCoin prices
@app.route('/kucoin_price', methods=['GET'])
def kucoin_price():
    bid, ask = get_kucoin_price()
    return jsonify({'kucoin_bid': bid, 'kucoin_ask': ask})

# Flask route to monitor arbitrage opportunities
@app.route('/monitor_arbitrage', methods=['GET'])
def monitor_arbitrage():
    coinbase_price = get_coinbase_price()
    coingecko_price = get_coingecko_price()
    kraken_bid, kraken_ask = get_kraken_price()
    bitfinex_bid, bitfinex_ask = get_bitfinex_price()
    kucoin_bid, kucoin_ask = get_kucoin_price()
    okx_bid, okx_ask = get_okx_price()
    gemini_bid, gemini_ask = get_gemini_price()

    # Store the prices in a dictionary for display
    prices = {
        "Coinbase": {"price": coinbase_price},
        "CoinGecko": {"price": coingecko_price},
        "Kraken": {"bid": kraken_bid, "ask": kraken_ask},
        "Bitfinex": {"bid": bitfinex_bid, "ask": bitfinex_ask},
        "KuCoin": {"bid": kucoin_bid, "ask": kucoin_ask},
	"OKX": {"bid": okx_bid, "ask": okx_ask},
        "Gemini": {"bid": gemini_bid, "ask": gemini_ask}
    }

    opportunities = []

    # Arbitrage checks and opportunity calculation
    if coinbase_price and kraken_ask and coinbase_price < kraken_ask:
        profit, profit_percentage = calculate_profit(coinbase_price, kraken_ask)
        opportunities.append({
            'pair': 'Coinbase to Kraken',
            'buy_price': coinbase_price,
            'sell_price': kraken_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })

 # Arbitrage checks and opportunity calculation
    if coingecko_price and kraken_ask and coingecko_price < kraken_ask:
        profit, profit_percentage = calculate_profit(coingecko_price, kraken_ask)
        opportunities.append({
            'pair': 'CoinGecko to Kraken',
            'buy_price': coingecko_price,
            'sell_price': kraken_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })


  # Arbitrage checks and opportunity calculation
    if gemini_bid and kraken_ask and gemini_bid < kraken_ask:
        profit, profit_percentage = calculate_profit(gemini_bid, kraken_ask)
        opportunities.append({
            'pair': 'Gemini to Kraken',
            'buy_price': gemini_bid,
            'sell_price': kraken_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })

    if coinbase_price and okx_ask and coinbase_price < okx_ask:
        profit, profit_percentage = calculate_profit(coinbase_price, okx_ask)
        opportunities.append({
            'pair': 'Coinbase to OKX',
            'buy_price': coinbase_price,
            'sell_price': okx_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })
    if coingecko_price and bitfinex_ask and coingecko_price < bitfinex_ask:
        profit, profit_percentage = calculate_profit(coingecko_price, bitfinex_ask)
        opportunities.append({
            'pair': 'CoinGecko to bitfinex',
            'buy_price': coingecko_price,
            'sell_price': bitfinex_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })


    if coinbase_price and bitfinex_ask and coinbase_price < bitfinex_ask:
        profit, profit_percentage = calculate_profit(coinbase_price, bitfinex_ask)
        opportunities.append({
            'pair': 'Coinbase to Bitfinex',
            'buy_price': coinbase_price,
            'sell_price': bitfinex_ask,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })

    if kraken_bid and bitfinex_ask and kraken_bid > bitfinex_ask:
        profit, profit_percentage = calculate_profit(bitfinex_ask, kraken_bid)
        opportunities.append({
            'pair': 'Bitfinex to Kraken',
            'buy_price': bitfinex_ask,
            'sell_price': kraken_bid,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })

    if kraken_bid and kucoin_ask and kraken_bid > kucoin_ask:
        profit, profit_percentage = calculate_profit(kucoin_ask, kraken_bid)
        opportunities.append({
            'pair': 'KuCoin to Kraken',
            'buy_price': kucoin_ask,
            'sell_price': kraken_bid,
            'profit': f"${profit:.2f}",
            'profit_percentage': f"{profit_percentage:.2f}%" if profit_percentage is not None else "N/A"
        })

    return jsonify({'arbitrage_opportunities': opportunities})


@app.route('/')
def home():
    return render_template('index.html')  # Renders the index.html file from templates
    #return "Welcome to the Arbitrage Monitoring App!"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
