from flask import Flask, render_template, request, jsonify
import sys
import uuid
from datetime import datetime
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import baripool_action
import dfix

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

@app.route('/get_recent_trades')
def get_recent_trades():
    print(baripool.fillcontainer)
    trades = []
    
    for order_id, execution_report in baripool.fillcontainer.items():
        try:
            # Check if execution_report is a valid string
            #if not execution_report or not isinstance(execution_report, str):
                #continue
                
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
                    'order_id': order_id
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

if __name__ == '__main__':
    app.run(debug=True) 