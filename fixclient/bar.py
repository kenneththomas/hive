from flask import Flask, render_template, request, jsonify
import sys
import uuid
from datetime import datetime
import logging
import sqlite3
from pathlib import Path
import random
import threading
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import baripool_action
import dfix
from scopechat import scope_chat, DEFAULT_PROMPT, register_scope_chat_routes  # Import the ScopeChat module and register_scope_chat_routes
from profile import register_profile_routes  # Import the new profile module
from market_data import FinnhubClient
import maricon
import portfolio  # Import the portfolio module
from market_maker import MarketMaker

app = Flask(__name__)

# Register profile routes
register_profile_routes(app)

# Register ScopeChat routes
register_scope_chat_routes(app)

# Database setup
DB_PATH = Path('fixclient/instance/ourteam.db')

# Initialize market data client
finnhub_client = FinnhubClient(maricon.finnhub_key)

# Global settings for random trade generation
random_trade_settings = {
    'enabled': False,
    'interval_seconds': 15,
    'orders_per_interval': 1,
    'max_orders_before_refresh': 5000
}

# List of symbols for random trade generation
SYMBOLS = ['AAPL', 'SPY', 'TSLA']

# Initialize market maker
market_maker = MarketMaker()

# Global variable to track the market maker thread
market_maker_thread = None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_profile(scope_id):
    """Get profile information for a given scope_id (email)"""
    conn = get_db()
    try:
        profile = conn.execute('SELECT * FROM employee WHERE email = ?', (scope_id,)).fetchone()
        return dict(profile) if profile else None
    finally:
        conn.close()

def get_random_employee():
    """Get a random employee from the database with a non-empty email"""
    conn = get_db()
    try:
        employee = conn.execute('SELECT email FROM employee WHERE email IS NOT NULL AND email != "" ORDER BY RANDOM() LIMIT 1').fetchone()
        return employee['email'] if employee else 'TRADER1'
    finally:
        conn.close()

def process_order(side_value, symbol, quantity, price, sender):
    """Process an order and return the result"""
    fix_message = f"11={unique_id()};54={side_value};55={symbol};38={quantity};44={price};49={sender}"
    
    # Simulate some trades to match with
    baripool_action.bp_directentry_sim()
    output = baripool.on_new_order(fix_message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return {
        'output': f"[{timestamp}] {output}",
        'status': "ORDER SENT"
    }

def generate_random_trade():
    """Generate a random trade with realistic market data."""
    try:
        # Get a random employee as sender
        sender = get_random_employee()
        
        # Get all available symbols (from our list and from the order book)
        available_symbols = list(SYMBOLS)  # Start with our predefined list
        
        # Add symbols from the order book that aren't already in our list
        for symbol, book in baripool.bookshelf.items():
            if book and symbol not in available_symbols:
                available_symbols.append(symbol)
        
        # Get a random symbol from our expanded list
        symbol = random.choice(available_symbols)
        
        # Get current market price
        quote_data = finnhub_client.get_quote(symbol)
        
        if 'c' not in quote_data or not quote_data['c']:
            return {'error': 'Unable to fetch market price'}, 404
            
        current_price = float(quote_data['c'])
        
        # Increment the order count for this symbol
        finnhub_client.increment_order_count(symbol)
        
        # Generate a random price within 1% of the current price
        price_variation = random.uniform(-0.01, 0.01)
        price = round(current_price * (1 + price_variation), 2)
        
        # Generate a random quantity between 10 and 1000
        quantity = random.randint(10, 1000)
        
        # Randomly choose buy or sell
        side = random.choice(['Buy', 'Sell'])
        side_value = "1" if side == "Buy" else "2"
        
        # Process the order
        result = process_order(side_value, symbol, quantity, price, sender)
        
        return {
            'status': 'success',
            'output': f"Generated random {side} order for {quantity} {symbol} at ${price}"
        }
        
    except Exception as e:
        print(f"Error generating random trade: {str(e)}")
        return {'error': 'Internal server error'}, 500

def generate_fallback_trade(symbol, sender):
    """Generate a fallback trade when market price is unavailable"""
    side = '1' if random.random() > 0.5 else '2'
    price = round(random.uniform(100, 200), 2)
    quantity = random.randint(10, 100)
    
    fix_message = f"11={unique_id()};54={side};55={symbol};38={quantity};44={price};49={sender}"
    
    # Simulate some trades to match with
    baripool_action.bp_directentry_sim()
    output = baripool.on_new_order(fix_message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return {
        'output': f"[{timestamp}] {output}",
        'status': "ORDER SENT (FALLBACK)",
        'order': {
            'side': side,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'sender': sender
        }
    }

# Configure Flask's logging to filter out specific endpoints
class EndpointFilter(logging.Filter):
    def __init__(self, excluded_endpoints):
        self.excluded_endpoints = excluded_endpoints
        super().__init__()
        
    def filter(self, record):
        message = record.getMessage()
        for endpoint in self.excluded_endpoints:
            if f"GET {endpoint}" in message:
                return False
        return True

# Apply the filter to the Werkzeug logger
logging.getLogger('werkzeug').addFilter(
    EndpointFilter(['/get_order_book', '/get_recent_trades', '/get_portfolio', '/test_baripool', '/market-maker'])
)

def unique_id():
    return str(uuid.uuid4())[:8]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Check if the request is JSON or form data
    if request.is_json:
        # Handle JSON request (from generate_random_trade)
        data = request.get_json()
        side_value = data.get('side')
        if side_value == "Buy":
            side_value = "1"
        elif side_value == "Sell":
            side_value = "2"
        
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        price = data.get('price')
        sender = data.get('sender')
    else:
        # Handle form data (from the UI)
        side_value = request.form.get('side')
        if side_value == "Buy":
            side_value = "1"
        elif side_value == "Sell":
            side_value = "2"
        
        symbol = request.form.get('symbol')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        sender = request.form.get('sender')
    
    result = process_order(side_value, symbol, quantity, price, sender)
    return jsonify(result)

@app.route('/get_time')
def get_time():
    return jsonify({
        'time': datetime.now().strftime("%H:%M:%S"),
        'date': datetime.now().strftime("%d-%b-%Y")
    })

@app.route('/get_order_book')
def get_order_book():
    books_data = {}
    
    for symbol, book in baripool.bookshelf.items():
        if not book:  # Skip empty books
            continue
            
        buys = [order for order in book if order.side == '1' and not order.is_canceled]
        sells = [order for order in book if order.side == '2' and not order.is_canceled]
        
        # Sort buys by price (descending) and sells by price (ascending)
        buys.sort(key=lambda x: x.limitprice, reverse=True)
        sells.sort(key=lambda x: x.limitprice)
        
        books_data[symbol] = {
            'buys': [
                {
                    'order_id': order.orderid,
                    'sender': order.sendercompid,
                    'original_qty': order.original_qty,
                    'remaining_qty': order.qty,
                    'price': order.limitprice,
                    'symbol': symbol,
                    'time': baripool.fillcontainer.get(order.orderid, {}).get('60', '') or 
                           baripool.fillcontainer.get(order.orderid, {}).get('52', '')
                } for order in buys
            ],
            'sells': [
                {
                    'order_id': order.orderid,
                    'sender': order.sendercompid,
                    'original_qty': order.original_qty,
                    'remaining_qty': order.qty,
                    'price': order.limitprice,
                    'symbol': symbol,
                    'time': baripool.fillcontainer.get(order.orderid, {}).get('60', '') or 
                           baripool.fillcontainer.get(order.orderid, {}).get('52', '')
                } for order in sells
            ]
        }
    
    return jsonify(books_data)

@app.route('/get_recent_trades')
def get_recent_trades():
    trades = []
    
    for order_id, execution_report in baripool.fillcontainer.items():
        try:
            # Parse the FIX execution report to extract trade details
            parsed_report = execution_report
            
            # Only include actual executions (ExecType=F for Fill or Partial Fill)
            if '150' in parsed_report and parsed_report['150'] in ['1', '2']:  # 1=Partial Fill, 2=Fill
                trade = {
                    'symbol': parsed_report.get('55', 'Unknown'),
                    'price': parsed_report.get('31', 'Unknown'),  # LastPx
                    'quantity': parsed_report.get('32', '0'),     # LastQty
                    'time': parsed_report.get('60', datetime.now().strftime("%H:%M:%S")),
                    'buyer': parsed_report.get('49', 'Unknown'),  # SenderCompID
                    'seller': parsed_report.get('56', 'Unknown'), # TargetCompID
                    'order_id': order_id,
                    'side': 'Buy' if parsed_report.get('54') == '1' else 'Sell'
                }
                trades.append(trade)
        except Exception as e:
            # Log the error but continue processing other trades
            print(f"Error processing trade {order_id}: {str(e)}")
            continue
    
    # Sort by time, most recent first
    trades.sort(key=lambda x: x['time'], reverse=True)
    
    # Limit to most recent 20 trades
    return jsonify(trades[:20])

@app.route('/generate_random_trade', methods=['POST'])
def generate_random_trade_route():
    result, status_code = generate_random_trade()
    return jsonify(result), status_code

@app.route('/get_market_price', methods=['POST'])
def get_market_price_api():
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        # Get real-time quote (using cache if available)
        quote_data = finnhub_client.get_quote(symbol)
        
        if 'c' in quote_data:
            price = quote_data['c']
            if price:
                return jsonify({'price': price})
                
        return jsonify({'error': 'Unable to fetch market price'}), 404
        
    except Exception as e:
        print(f"Error fetching market price: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/update_random_trade_settings', methods=['POST'])
def update_random_trade_settings():
    try:
        data = request.get_json()
        
        if 'enabled' in data:
            random_trade_settings['enabled'] = data['enabled']
        
        if 'interval_seconds' in data:
            random_trade_settings['interval_seconds'] = int(data['interval_seconds'])
        
        if 'orders_per_interval' in data:
            random_trade_settings['orders_per_interval'] = int(data['orders_per_interval'])
        
        if 'max_orders_before_refresh' in data:
            random_trade_settings['max_orders_before_refresh'] = int(data['max_orders_before_refresh'])
            # Update the Alpha Vantage client setting
            finnhub_client.max_orders_before_refresh = random_trade_settings['max_orders_before_refresh']
        
        return jsonify({
            'status': 'success',
            'settings': random_trade_settings
        })
        
    except Exception as e:
        print(f"Error updating random trade settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_random_trade_settings', methods=['GET'])
def get_random_trade_settings():
    return jsonify(random_trade_settings)

@app.route('/get_portfolio', methods=['GET'])
def get_portfolio_route():
    """Get portfolio information for the logged-in trader"""
    trader_id = request.args.get('trader_id')
    
    if not trader_id:
        return jsonify({'error': 'Trader ID is required'}), 400
    
    try:
        # Get portfolio data
        logging.info(f"Getting portfolio for trader: {trader_id}")
        portfolio_data = portfolio.get_portfolio(trader_id)
        
        # Get current market prices for all symbols in open positions
        market_prices = {}
        for position in portfolio_data['open_positions']:
            symbol = position['symbol']
            logging.info(f"Getting market price for symbol: {symbol}")
            try:
                quote_data = finnhub_client.get_quote(symbol)
                if 'c' in quote_data and quote_data['c']:
                    market_prices[symbol] = float(quote_data['c'])
                else:
                    logging.warning(f"No current price data for symbol: {symbol}")
            except Exception as e:
                logging.error(f"Error getting market price for {symbol}: {str(e)}")
                # Continue with other symbols
        
        # Update position prices and unrealized PnL
        if market_prices:
            portfolio_data['open_positions'] = portfolio.update_position_prices(
                portfolio_data['open_positions'], 
                market_prices
            )
            
            # Recalculate total unrealized PnL
            portfolio_data['total_unrealized_pnl'] = sum(
                position['unrealized_pnl'] for position in portfolio_data['open_positions']
            )
            
            # Recalculate total PnL
            portfolio_data['total_pnl'] = (
                portfolio_data['total_realized_pnl'] + 
                portfolio_data['total_unrealized_pnl']
            )
        
        return jsonify(portfolio_data)
        
    except Exception as e:
        import traceback
        logging.error(f"Error getting portfolio: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/test_portfolio', methods=['GET'])
def test_portfolio_route():
    """Test if portfolio module is working correctly"""
    try:
        trader_id = request.args.get('trader_id', 'TRADER1')
        portfolio_data = portfolio.get_portfolio(trader_id)
        return jsonify({
            'status': 'success',
            'message': 'Portfolio module is working correctly',
            'portfolio_data': portfolio_data
        })
    except Exception as e:
        import traceback
        logging.error(f"Error testing portfolio: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error in portfolio module: {str(e)}'
        }), 500

@app.route('/test_baripool', methods=['GET'])
def test_baripool_route():
    """Test if baripool module is accessible"""
    try:
        import baripool
        fillcontainer_size = len(baripool.fillcontainer) if hasattr(baripool, 'fillcontainer') else 0
        return jsonify({
            'status': 'success',
            'message': 'baripool module is accessible',
            'fillcontainer_size': fillcontainer_size
        })
    except Exception as e:
        import traceback
        logging.error(f"Error testing baripool: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error accessing baripool: {str(e)}'
        }), 500

@app.route('/cancel_order', methods=['POST'])
def cancel_order_route():
    """Cancel an order by order ID"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
            
        # Call the baripool cancel order function
        baripool.on_cancel_order(order_id)
        
        # Get the current time for the response
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        return jsonify({
            'status': 'success',
            'message': f'Order {order_id} has been canceled',
            'output': f"[{timestamp}] Order {order_id} has been canceled"
        })
        
    except Exception as e:
        import traceback
        logging.error(f"Error canceling order: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error canceling order: {str(e)}'
        }), 500

@app.route('/market-maker')
def market_maker_page():
    return render_template('market_maker.html')

@app.route('/api/market-data/price/<symbol>')
def get_market_maker_price(symbol):
    try:
        price = market_maker.get_current_price(symbol)
        if price is None:
            return jsonify({
                'price': None,
                'message': f'No price data available for {symbol}'
            })
        return jsonify({'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-data/orderbook/<symbol>')
def get_symbol_order_book(symbol):
    try:
        order_book = market_maker.get_order_book(symbol)
        return jsonify(order_book)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/positions')
def get_positions():
    try:
        positions = market_maker.get_positions()
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/active')
def get_active_orders():
    try:
        orders = market_maker.get_active_orders()
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    try:
        market_maker.cancel_order(order_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/cancel-all', methods=['POST'])
def cancel_all_orders():
    try:
        market_maker.cancel_all_orders()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def start_market_maker_thread():
    """Start the market maker in a separate thread"""
    global market_maker_thread
    
    # Check if thread is already running
    if market_maker_thread and market_maker_thread.is_alive():
        return {'status': 'error', 'message': 'Market maker thread is already running'}
    
    # Create and start a new thread
    market_maker_thread = threading.Thread(target=market_maker.run, daemon=True)
    market_maker_thread.start()
    
    return {'status': 'success', 'message': 'Market maker thread started'}

@app.route('/api/market-maker/start', methods=['POST'])
def start_market_maker():
    try:
        config = request.json
        # Start the market maker
        result = market_maker.start(config)
        
        # If market maker started successfully, start the thread
        if result['status'] == 'success':
            thread_result = start_market_maker_thread()
            if thread_result['status'] == 'error':
                # If thread failed to start, stop the market maker
                market_maker.stop()
                return jsonify(thread_result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/stop', methods=['POST'])
def stop_market_maker():
    try:
        # Stop the market maker
        result = market_maker.stop()
        
        # The thread will exit naturally when market_maker.is_running becomes False
        # We don't need to explicitly stop the thread
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/pause', methods=['POST'])
def pause_market_maker():
    try:
        market_maker.pause()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/resume', methods=['POST'])
def resume_market_maker():
    try:
        market_maker.resume()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/toggle-price-source', methods=['POST'])
def toggle_price_source():
    try:
        result = market_maker.toggle_price_source()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/rebalance', methods=['POST'])
def rebalance_market_maker():
    try:
        result = market_maker.rebalance_orders()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market-maker/lift-quote', methods=['POST'])
def lift_quote():
    try:
        data = request.json
        symbol = data.get('symbol')
        price = float(data.get('price'))
        quantity = int(data.get('quantity'))
        side = data.get('side')
        
        if not all([symbol, price, quantity, side]):
            return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400
        
        result = market_maker.lift_quote(symbol, price, quantity, side)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5017)