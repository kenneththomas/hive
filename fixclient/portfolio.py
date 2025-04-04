import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import sys
import os

# Add the pyengine directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pyengine')))

# Try to import baripool, with fallback
try:
    import baripool
    BARIPOOL_AVAILABLE = True
    logging.info("Successfully imported baripool module")
except ImportError as e:
    logging.error(f"Failed to import baripool module: {str(e)}")
    BARIPOOL_AVAILABLE = False

# Database setup
DB_PATH = Path('fixclient/instance/ourteam.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_portfolio(trader_id):
    """
    Get portfolio information for a trader including:
    - Open positions
    - Filled trades
    - PnL
    """
    if not BARIPOOL_AVAILABLE:
        logging.error("baripool module not available")
        return {
            'open_positions': [],
            'filled_trades': [],
            'total_realized_pnl': 0,
            'total_unrealized_pnl': 0,
            'total_pnl': 0
        }
    
    try:
        # Get all trades for the trader from fillcontainer
        trades = []
        logging.info(f"Processing fillcontainer for trader: {trader_id}")
        
        # Check if fillcontainer exists and is accessible
        if not hasattr(baripool, 'fillcontainer'):
            logging.error("baripool.fillcontainer not found")
            return {
                'open_positions': [],
                'filled_trades': [],
                'total_realized_pnl': 0,
                'total_unrealized_pnl': 0,
                'total_pnl': 0
            }
        
        for key, execution_report in baripool.fillcontainer.items():
            try:
                # Only include actual executions (ExecType=F for Fill or Partial Fill)
                if '150' in execution_report and execution_report['150'] in ['1', '2']:  # 1=Partial Fill, 2=Fill
                    # Check if this trade belongs to our trader
                    if execution_report.get('49') == trader_id or execution_report.get('56') == trader_id:
                        # Extract the order ID from the composite key (format: orderid_timestamp)
                        order_id = key.split('_')[0]
                        
                        trade = {
                            'order_id': order_id,
                            'symbol': execution_report.get('55', 'Unknown'),
                            'side': execution_report.get('54', '1'),  # 1=Buy, 2=Sell
                            'quantity': execution_report.get('32', '0'),  # LastQty
                            'price': execution_report.get('31', '0'),  # LastPx
                            'time': execution_report.get('60', datetime.now().strftime("%H:%M:%S")),
                            'status': 'Filled'
                        }
                        trades.append(trade)
            except Exception as e:
                logging.error(f"Error processing trade {key}: {str(e)}")
                continue
        
        logging.info(f"Found {len(trades)} trades for trader: {trader_id}")
        
        # Process trades to calculate positions and PnL
        positions = {}
        filled_trades = []
        open_positions = []
        
        for trade in trades:
            symbol = trade['symbol']
            side = trade['side']
            quantity = int(trade['quantity'])
            price = float(trade['price'])
            
            # Add to filled trades
            filled_trades.append(trade)
            
            # Update positions
            if symbol not in positions:
                positions[symbol] = {
                    'symbol': symbol,
                    'quantity': 0,
                    'avg_price': 0,
                    'realized_pnl': 0,
                    'unrealized_pnl': 0,
                    'current_price': 0  # Will be updated with market price
                }
            
            # Update position based on trade side
            if side == '1':  # Buy
                # If we have a short position, close it first
                if positions[symbol]['quantity'] < 0:
                    # Calculate realized PnL from closing short position
                    short_quantity = min(abs(positions[symbol]['quantity']), quantity)
                    short_pnl = (positions[symbol]['avg_price'] - price) * short_quantity
                    positions[symbol]['realized_pnl'] += short_pnl
                    
                    # Update remaining quantity
                    remaining_quantity = quantity - short_quantity
                    if remaining_quantity > 0:
                        # Calculate new average price for long position
                        total_value = (positions[symbol]['quantity'] * positions[symbol]['avg_price']) + (remaining_quantity * price)
                        positions[symbol]['quantity'] = positions[symbol]['quantity'] + remaining_quantity
                        positions[symbol]['avg_price'] = total_value / positions[symbol]['quantity']
                    else:
                        positions[symbol]['quantity'] = positions[symbol]['quantity'] + quantity
                else:
                    # Calculate new average price for long position
                    total_value = (positions[symbol]['quantity'] * positions[symbol]['avg_price']) + (quantity * price)
                    positions[symbol]['quantity'] = positions[symbol]['quantity'] + quantity
                    positions[symbol]['avg_price'] = total_value / positions[symbol]['quantity']
            
            elif side == '2':  # Sell
                # If we have a long position, close it first
                if positions[symbol]['quantity'] > 0:
                    # Calculate realized PnL from closing long position
                    long_quantity = min(positions[symbol]['quantity'], quantity)
                    long_pnl = (price - positions[symbol]['avg_price']) * long_quantity
                    positions[symbol]['realized_pnl'] += long_pnl
                    
                    # Update remaining quantity
                    remaining_quantity = quantity - long_quantity
                    if remaining_quantity > 0:
                        # Calculate new average price for short position
                        total_value = (abs(positions[symbol]['quantity']) * positions[symbol]['avg_price']) + (remaining_quantity * price)
                        positions[symbol]['quantity'] = positions[symbol]['quantity'] - remaining_quantity
                        positions[symbol]['avg_price'] = total_value / abs(positions[symbol]['quantity'])
                    else:
                        positions[symbol]['quantity'] = positions[symbol]['quantity'] - quantity
                else:
                    # Calculate new average price for short position
                    total_value = (abs(positions[symbol]['quantity']) * positions[symbol]['avg_price']) + (quantity * price)
                    positions[symbol]['quantity'] = positions[symbol]['quantity'] - quantity
                    positions[symbol]['avg_price'] = total_value / abs(positions[symbol]['quantity'])
        
        # Add positions with non-zero quantity to open positions
        for symbol, position in positions.items():
            if position['quantity'] != 0:
                open_positions.append(position)
        
        logging.info(f"Found {len(open_positions)} open positions for trader: {trader_id}")
        
        # Calculate total PnL
        total_realized_pnl = sum(position['realized_pnl'] for position in positions.values())
        total_unrealized_pnl = sum(position['unrealized_pnl'] for position in positions.values())
        total_pnl = total_realized_pnl + total_unrealized_pnl
        
        return {
            'open_positions': open_positions,
            'filled_trades': filled_trades,
            'total_realized_pnl': total_realized_pnl,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_pnl': total_pnl
        }
    except Exception as e:
        import traceback
        logging.error(f"Error getting portfolio: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def update_position_prices(positions, market_prices):
    """
    Update unrealized PnL based on current market prices
    """
    for position in positions:
        symbol = position['symbol']
        if symbol in market_prices:
            current_price = market_prices[symbol]
            position['current_price'] = current_price
            
            # Calculate unrealized PnL
            if position['quantity'] > 0:  # Long position
                position['unrealized_pnl'] = (current_price - position['avg_price']) * position['quantity']
            elif position['quantity'] < 0:  # Short position
                position['unrealized_pnl'] = (position['avg_price'] - current_price) * abs(position['quantity'])
            else:
                position['unrealized_pnl'] = 0
    
    return positions 