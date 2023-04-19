import csv

def process_trades(file_name):
    open_positions = {}
    total_pnl = 0

    with open(file_name, newline='') as csvfile:
        trades = csv.DictReader(csvfile)
        for trade in trades:
            symbol = trade['symbol']
            side = trade['side']
            price = float(trade['price'])
            qty = int(trade['qty'])

            if symbol not in open_positions:
                open_positions[symbol] = {'quantity': 0, 'avg_price': 0, 'realized_pnl': 0}

            current_quantity = open_positions[symbol]['quantity']
            current_avg_price = open_positions[symbol]['avg_price']

            if side == 'Buy':
                new_quantity = current_quantity + qty
                new_avg_price = ((current_avg_price * current_quantity) + (price * qty)) / new_quantity
            else:  # 'Sell'
                new_quantity = current_quantity - qty
                pnl = (current_avg_price - price) * qty
                total_pnl += pnl
                open_positions[symbol]['realized_pnl'] += pnl

                if new_quantity == 0:
                    new_avg_price = 0
                else:
                    new_avg_price = current_avg_price

            open_positions[symbol]['quantity'] = new_quantity
            open_positions[symbol]['avg_price'] = new_avg_price

    for symbol, position in open_positions.items():
        if position['quantity'] == 0:
            print(f"Symbol: {symbol} - Realized PnL: {position['realized_pnl']}")
        else:
            print(f"Symbol: {symbol} - Open Quantity: {position['quantity']} - Open Avg Px: {position['avg_price']}")

    print(f"Total Realized PnL: {total_pnl}")

# Assuming the CSV file is named 'trades.csv'
process_trades('trades.csv')

