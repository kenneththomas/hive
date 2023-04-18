from collections import defaultdict

def parse_fix_messages(fix_messages):
    trades = defaultdict(list)
    
    for fix_message in fix_messages:
        fields = fix_message.split(';')
        message_dict = {field.split('=')[0]: field.split('=')[1] for field in fields}
        
        if message_dict['35'] == '8':  # Execution Report
            symbol = message_dict['55']
            side = int(message_dict['54'])
            last_px = float(message_dict['31'])
            last_shares = int(message_dict['32'])
            
            trade = {'side': side, 'last_px': last_px, 'last_shares': last_shares}
            trades[symbol].append(trade)
            
    return trades

def calculate_pnl_and_positions(trades):
    pnl = defaultdict(float)
    positions = defaultdict(int)
    
    for symbol, trades_list in trades.items():
        for trade in trades_list:
            pnl[symbol] += (trade['last_px'] * trade['last_shares'] * (1 if trade['side'] == 1 else -1))
            positions[symbol] += (trade['last_shares'] * (1 if trade['side'] == 1 else -1))
            
    return pnl, positions

# Example FIX messages
fix_messages = [
    "8=FIX.4.2;35=8;49=BARI;11=12345;17=abcd1234;37=12345;39=2;54=1;55=AAPL;150=2;14=100;31=150.00;32=100;151=0;60=20230101-12:00:00.000;52=20230101-12:00:00.000;30=BARI;76=BARI",
    "8=FIX.4.2;35=8;49=BARI;11=67890;17=efgh5678;37=67890;39=2;54=2;55=AAPL;150=2;14=100;31=160.00;32=100;151=0;60=20230101-12:05:00.000;52=20230101-12:05:00.000;30=BARI;76=BARI",
]

trades = parse_fix_messages(fix_messages)
pnl, positions = calculate_pnl_and_positions(trades)

for symbol, pnl_value in pnl.items():
    print(f"PnL for {symbol}: {pnl_value}")

for symbol, position in positions.items():
    print(f"Open position for {symbol}: {position}")

