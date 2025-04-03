from flask import Flask, render_template, request, jsonify
import sys
import uuid
from datetime import datetime
import logging
import sqlite3
from pathlib import Path
import random
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import baripool_action
import dfix
from scopechat import scope_chat, DEFAULT_PROMPT  # Import the ScopeChat module and DEFAULT_PROMPT
from profile import register_profile_routes  # Import the new profile module

app = Flask(__name__)

# Register profile routes
register_profile_routes(app)

# Database setup
DB_PATH = Path('fixclient/instance/ourteam.db')

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

def generate_random_trade():
    """Generate a random trade based on the order book"""
    # Get a random employee as sender
    sender = get_random_employee()
    
    # Get the order book
    books_data = {}
    for symbol, book in baripool.bookshelf.items():
        if not book:
            continue
        buys = [order for order in book if order.side == '1' and not order.is_canceled]
        sells = [order for order in book if order.side == '2' and not order.is_canceled]
        
        if buys or sells:
            books_data[symbol] = {
                'buys': buys,
                'sells': sells
            }
    
    # If no orders in book, use AAPL
    if not books_data:
        symbol = 'AAPL'
        side = '1' if random.random() > 0.5 else '2'
        price = round(random.uniform(100, 200), 2)
        unmarketable_price = price + (0.01 if side == '1' else -0.01)  # Slightly off from market price
    else:
        # Pick a random symbol with orders
        symbol = random.choice(list(books_data.keys()))
        book = books_data[symbol]
        
        # Decide whether to buy or sell
        if book['buys'] and book['sells']:
            side = '1' if random.random() > 0.5 else '2'
        elif book['buys']:
            side = '2'  # Sell against buys
        else:
            side = '1'  # Buy against sells
            
        # Get price from the book
        if side == '1' and book['sells']:
            price = book['sells'][0].limitprice
            unmarketable_price = price + 0.01  # Slightly higher than best offer
        elif side == '2' and book['buys']:
            price = book['buys'][0].limitprice
            unmarketable_price = price - 0.01  # Slightly lower than best bid
        else:
            price = round(random.uniform(100, 200), 2)
            unmarketable_price = price + (0.01 if side == '1' else -0.01)
    
    # Generate the marketable trade
    marketable_fix_message = f"11={unique_id()};54={side};55={symbol};38=10;44={price};49={sender}"
    
    # Generate the unmarketable trade
    unmarketable_fix_message = f"11={unique_id()};54={side};55={symbol};38=100;44={unmarketable_price};49={sender}"
    
    # Simulate some trades to match with
    baripool_action.bp_directentry_sim()
    
    # Submit both trades
    marketable_output = baripool.on_new_order(marketable_fix_message)
    unmarketable_output = baripool.on_new_order(unmarketable_fix_message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return {
        'output': f"[{timestamp}] Marketable: {marketable_output}\n[{timestamp}] Unmarketable: {unmarketable_output}",
        'status': "ORDERS SENT",
        'marketable': {
            'side': side,
            'symbol': symbol,
            'quantity': 10,
            'price': price,
            'sender': sender
        },
        'unmarketable': {
            'side': side,
            'symbol': symbol,
            'quantity': 100,
            'price': unmarketable_price,
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
    EndpointFilter(['/get_order_book', '/get_recent_trades'])
)

def unique_id():
    return str(uuid.uuid4())[:8]

# Define the order handler function that will be used by ScopeChat
def handle_ai_order(side, symbol, quantity, price, sender):
    """Handle order submission from AI trader"""
    fix_message = f"11={unique_id()};54={side};55={symbol};38={quantity};44={price};49={sender}"
    
    # Simulate some trades to match with
    baripool_action.bp_directentry_sim()
    output = baripool.on_new_order(fix_message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return {
        'output': f"[{timestamp}] {output}",
        'status': "ORDER SENT",
        'side': side,
        'symbol': symbol,
        'quantity': quantity,
        'price': price
    }

# Set the order handler for ScopeChat
scope_chat.set_order_handler(handle_ai_order)

# Helper function to check if a symbol was mentioned in chat history
def symbol_mentioned_in_chat(scope_id, symbol):
    """Check if a symbol was mentioned in the chat history"""
    history = scope_chat.get_chat_history(scope_id)
    symbol_upper = symbol.upper()
    
    for message in history:
        if symbol_upper in message["content"].upper():
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    side_value = request.form.get('side')
    if side_value == "Buy":
        side_value = "1"
    elif side_value == "Sell":
        side_value = "2"
    
    symbol = request.form.get('symbol')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    sender = request.form.get('sender')
    
    fix_message = f"11={unique_id()};54={side_value};55={symbol};38={quantity};44={price};49={sender}"
    
    # Simulate some trades to match with
    baripool_action.bp_directentry_sim()
    output = baripool.on_new_order(fix_message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return jsonify({
        'output': f"[{timestamp}] {output}",
        'status': "ORDER SENT"
    })

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

@app.route('/scope_chat/send', methods=['POST'])
def scope_chat_send():
    scope_id = request.form.get('scope_id')
    message = request.form.get('message')
    custom_prompt = request.form.get('custom_prompt')
    
    if not scope_id or not message:
        return jsonify({"error": "Scope ID and message are required"}), 400
    
    result = scope_chat.send_message(scope_id, message, custom_prompt)
    
    # Check if an order was placed and if the symbol was mentioned in chat
    if 'order_result' in result and 'symbol' in result['order_result']:
        symbol = result['order_result']['symbol']
        if symbol_mentioned_in_chat(scope_id, symbol):
            result['shared_trade'] = True
            result['trade_details'] = result['order_result']
    
    return jsonify(result)

@app.route('/scope_chat/history', methods=['GET'])
def scope_chat_history():
    scope_id = request.args.get('scope_id')
    
    if not scope_id:
        return jsonify({"error": "Scope ID is required"}), 400
    
    history = scope_chat.get_chat_history(scope_id)
    return jsonify({"history": history, "scope_id": scope_id})

@app.route('/scope_chat/clear', methods=['POST'])
def scope_chat_clear():
    scope_id = request.form.get('scope_id')
    
    if not scope_id:
        return jsonify({"error": "Scope ID is required"}), 400
    
    result = scope_chat.clear_chat(scope_id)
    return jsonify(result)

@app.route('/scope_chat/default_prompt', methods=['GET'])
def get_default_prompt():
    return jsonify({"prompt": DEFAULT_PROMPT})

@app.route('/generate_random_trade', methods=['POST'])
def generate_random_trade_route():
    result = generate_random_trade()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5017)