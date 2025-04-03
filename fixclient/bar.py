from flask import Flask, render_template, request, jsonify
import sys
import uuid
from datetime import datetime
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import baripool_action

app = Flask(__name__)

def unique_id():
    return str(uuid.uuid4())[:8]

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
                    'price': order.limitprice
                } for order in buys
            ],
            'sells': [
                {
                    'order_id': order.orderid,
                    'sender': order.sendercompid,
                    'original_qty': order.original_qty,
                    'remaining_qty': order.qty,
                    'price': order.limitprice
                } for order in sells
            ]
        }
    
    return jsonify(books_data)

if __name__ == '__main__':
    app.run(debug=True) 