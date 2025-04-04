"""
Market Making Algorithm Module

This module implements a basic market making algorithm that:
1. Analyzes the order book
2. Makes trading decisions based on configurable parameters
3. Places and manages orders
4. Monitors risk limits
"""

import time
import logging
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Tuple, Any
import json
import sys
import os

# Add the pyengine directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pyengine')))

# Import required modules
import baripool
from market_data import FinnhubClient
import maricon
import portfolio  # Import portfolio module to use its functions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('market_maker')

class MarketMaker:
    """
    Market Making Algorithm
    
    This class implements a basic market making strategy that:
    - Places bid and ask orders around the mid-price
    - Adjusts quotes based on inventory
    - Manages risk limits
    - Tracks performance
    """
    
    def __init__(self, trader_id: str = "MARKET_MAKER"):
        """
        Initialize the market maker
        
        Args:
            trader_id (str): The trader ID to use for orders
        """
        self.trader_id = trader_id
        self.is_running = False
        self.is_paused = False
        self.active_orders = {}  # {order_id: order_details}
        self.position = {}  # {symbol: quantity}
        self.use_real_market_data = True  # Flag to toggle between real market data and baripool prices
        self.performance_metrics = {
            'total_trades': 0,
            'spread_capture': 0.0,
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'start_time': None,
            'last_update': None
        }
        
        # Default configuration
        self.config = {
            'symbols': ['AAPL'],  # List of symbols to market make
            'max_position': 1000,  # Maximum position size in shares
            'max_notional': 100000,  # Maximum notional exposure in dollars
            'max_drawdown': 1000,  # Maximum drawdown in dollars
            'target_spread_pct': 0.001,  # Target spread as percentage of mid price
            'min_spread_pct': 0.0005,  # Minimum spread as percentage of mid price
            'max_spread_pct': 0.005,  # Maximum spread as percentage of mid price
            'default_order_size': 100,  # Default order size in shares
            'min_order_size': 10,  # Minimum order size in shares
            'max_order_size': 500,  # Maximum order size in shares
            'price_adjustment_step': 0.0001,  # Price adjustment step as percentage
            'rebalance_interval': 5,  # Rebalance interval in seconds
            'price_away_threshold': 0.01,  # Maximum distance from market price as percentage
            'inventory_skew_factor': 0.0002,  # How much to adjust spread based on inventory
            'max_inventory_skew': 0.002  # Maximum inventory skew adjustment
        }
        
        # Initialize market data client
        self.market_data_client = FinnhubClient(maricon.finnhub_key)
        
        # Log initialization
        logger.info(f"Market maker initialized for trader: {trader_id}")
    
    def start(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start the market making algorithm
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration to use, or None to use default
            
        Returns:
            Dict[str, Any]: Status information
        """
        if self.is_running:
            return {'status': 'error', 'message': 'Market maker is already running'}
        
        # Update configuration if provided
        if config:
            self.update_config(config)
        
        # Reset active orders dictionary
        self.active_orders = {}
        logger.info("Active orders dictionary reset")
        
        self.is_running = True
        self.is_paused = False
        self.performance_metrics['start_time'] = datetime.now()
        self.performance_metrics['last_update'] = datetime.now()
        
        logger.info(f"Market maker started for trader: {self.trader_id}")
        return {'status': 'success', 'message': 'Market maker started successfully'}
    
    def stop(self) -> Dict[str, Any]:
        """
        Stop the market making algorithm and cancel all orders
        
        Returns:
            Dict[str, Any]: Status information
        """
        if not self.is_running:
            return {'status': 'error', 'message': 'Market maker is not running'}
        
        # Cancel all active orders
        self.cancel_all_orders()
        
        self.is_running = False
        self.is_paused = False
        
        logger.info(f"Market maker stopped for trader: {self.trader_id}")
        return {'status': 'success', 'message': 'Market maker stopped successfully'}
    
    def pause(self) -> Dict[str, Any]:
        """
        Pause the market making algorithm
        
        Returns:
            Dict[str, Any]: Status information
        """
        if not self.is_running:
            return {'status': 'error', 'message': 'Market maker is not running'}
        
        if self.is_paused:
            return {'status': 'error', 'message': 'Market maker is already paused'}
        
        self.is_paused = True
        
        logger.info(f"Market maker paused for trader: {self.trader_id}")
        return {'status': 'success', 'message': 'Market maker paused successfully'}
    
    def resume(self) -> Dict[str, Any]:
        """
        Resume the market making algorithm
        
        Returns:
            Dict[str, Any]: Status information
        """
        if not self.is_running:
            return {'status': 'error', 'message': 'Market maker is not running'}
        
        if not self.is_paused:
            return {'status': 'error', 'message': 'Market maker is not paused'}
        
        self.is_paused = False
        
        logger.info(f"Market maker resumed for trader: {self.trader_id}")
        return {'status': 'success', 'message': 'Market maker resumed successfully'}
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the market maker configuration
        
        Args:
            new_config (Dict[str, Any]): New configuration parameters
            
        Returns:
            Dict[str, Any]: Status information
        """
        # Validate new configuration
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
        
        logger.info(f"Market maker configuration updated: {new_config}")
        return {'status': 'success', 'message': 'Configuration updated successfully'}
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current market maker configuration
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        return self.config
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current market maker status
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'active_orders': len(self.active_orders),
            'position': self.position,
            'performance_metrics': self.performance_metrics
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions for all symbols
        
        Returns:
            List[Dict[str, Any]]: List of position information
        """
        try:
            # First update our position tracking
            self.update_position()
            
            # Get portfolio data for more detailed information
            portfolio_data = portfolio.get_portfolio(self.trader_id)
            
            # Use portfolio data if available, otherwise use our position tracking
            if portfolio_data and portfolio_data['open_positions']:
                # Ensure all required properties are defined with default values
                for position in portfolio_data['open_positions']:
                    # Ensure all required properties exist with default values
                    position.setdefault('avgPrice', 0.0)
                    position.setdefault('currentPrice', 0.0)
                    position.setdefault('marketValue', 0.0)
                    position.setdefault('pnl', 0.0)
                    position.setdefault('pnlPct', 0.0)
                    position.setdefault('trades', 0)
                    position.setdefault('realizedPnl', 0.0)
                    position.setdefault('unrealizedPnl', 0.0)
                return portfolio_data['open_positions']
            
            # Fallback to our position tracking if portfolio data is not available
            positions = []
            for symbol, quantity in self.position.items():
                # Get current market price
                current_price = self.get_current_price(symbol) or 0.0
                
                # Calculate position metrics
                market_value = quantity * current_price
                
                position_info = {
                    'symbol': symbol,
                    'side': 'Long' if quantity > 0 else 'Short',
                    'quantity': abs(quantity),
                    'avgPrice': 0.0,  # Would need to track trade history for this
                    'currentPrice': current_price,
                    'marketValue': market_value,
                    'pnl': 0.0,  # Would need trade history for realized P&L
                    'pnlPct': 0.0,  # Would need trade history for P&L percentage
                    'trades': self.performance_metrics['total_trades'],
                    'realizedPnl': self.performance_metrics['realized_pnl'],
                    'unrealizedPnl': self.performance_metrics['unrealized_pnl']
                }
                positions.append(position_info)
            
            return positions
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            # Return empty list with a default position to prevent UI errors
            return [{
                'symbol': 'N/A',
                'side': 'N/A',
                'quantity': 0,
                'avgPrice': 0.0,
                'currentPrice': 0.0,
                'marketValue': 0.0,
                'pnl': 0.0,
                'pnlPct': 0.0,
                'trades': 0,
                'realizedPnl': 0.0,
                'unrealizedPnl': 0.0
            }]
    
    def get_active_orders(self) -> List[Dict[str, Any]]:
        """
        Get all active orders
        
        Returns:
            List[Dict[str, Any]]: List of active order information
        """
        logger.info(f"Getting active orders. Count: {len(self.active_orders)}")
        logger.info(f"Active orders: {self.active_orders}")
        
        active_orders = []
        for order_id, order in self.active_orders.items():
            order_info = {
                'id': order_id,
                'time': order['time'],
                'symbol': order['symbol'],
                'side': 'Buy' if order['side'] == '1' else 'Sell',
                'price': order['price'],
                'quantity': order['quantity'],
                'status': 'Active'
            }
            active_orders.append(order_info)
        
        logger.info(f"Returning {len(active_orders)} active orders")
        return active_orders
    
    def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """
        Get the current order book for a symbol
        
        Args:
            symbol (str): The symbol to get the order book for
            
        Returns:
            Dict[str, Any]: Order book information
        """
        if symbol not in baripool.bookshelf:
            return {'bids': [], 'asks': []}
        
        book = baripool.bookshelf[symbol]
        bids = [order for order in book if order.side == '1' and not order.is_canceled]
        asks = [order for order in book if order.side == '2' and not order.is_canceled]
        
        # Sort bids by price (descending) and asks by price (ascending)
        bids.sort(key=lambda x: x.limitprice, reverse=True)
        asks.sort(key=lambda x: x.limitprice)
        
        return {
            'bids': [
                {
                    'order_id': order.orderid,
                    'sender': order.sendercompid,
                    'quantity': order.qty,
                    'price': order.limitprice,
                    'symbol': symbol
                } for order in bids
            ],
            'asks': [
                {
                    'order_id': order.orderid,
                    'sender': order.sendercompid,
                    'quantity': order.qty,
                    'price': order.limitprice,
                    'symbol': symbol
                } for order in asks
            ]
        }
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get the current market price for a symbol
        
        Args:
            symbol (str): The symbol to get the price for
            
        Returns:
            Optional[float]: The current market price, or None if not available
        """
        if self.use_real_market_data:
            try:
                quote_data = self.market_data_client.get_quote(symbol)
                if 'c' in quote_data and quote_data['c']:
                    return float(quote_data['c'])
            except Exception as e:
                logger.error(f"Error getting market price for {symbol}: {str(e)}")
        else:
            # Use baripool order book to get mid price
            order_book = self.get_order_book(symbol)
            if order_book['bids'] and order_book['asks']:
                best_bid = order_book['bids'][0]['price']
                best_ask = order_book['asks'][0]['price']
                return (best_bid + best_ask) / 2
            else:
                logger.warning(f"No order book data for {symbol}")
        
        return None
    
    def toggle_price_source(self) -> Dict[str, Any]:
        """
        Toggle between real market data and baripool prices
        
        Returns:
            Dict[str, Any]: Status information
        """
        self.use_real_market_data = not self.use_real_market_data
        source = "real market data" if self.use_real_market_data else "baripool order book"
        logger.info(f"Price source switched to {source}")
        return {
            'status': 'success',
            'message': f"Price source switched to {source}",
            'use_real_market_data': self.use_real_market_data
        }
    
    def calculate_optimal_quotes(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate optimal bid and ask quotes for a symbol
        
        Args:
            symbol (str): The symbol to calculate quotes for
            
        Returns:
            Tuple[Optional[float], Optional[float]]: (bid_price, ask_price)
        """
        logger.info(f"Calculating optimal quotes for {symbol}")
        
        # Get current market price
        market_price = self.get_current_price(symbol)
        if market_price is None:
            logger.warning(f"Could not get market price for {symbol}, using order book")
            # Try to get mid price from order book
            order_book = self.get_order_book(symbol)
            if not order_book['bids'] or not order_book['asks']:
                logger.error(f"No order book data for {symbol}")
                return None, None
            
            best_bid = order_book['bids'][0]['price']
            best_ask = order_book['asks'][0]['price']
            mid_price = (best_bid + best_ask) / 2
            logger.info(f"Using order book mid price for {symbol}: {mid_price} (best bid: {best_bid}, best ask: {best_ask})")
        else:
            mid_price = market_price
            logger.info(f"Using market price for {symbol}: {mid_price}")
        
        # Get current position
        position = self.position.get(symbol, 0)
        logger.info(f"Current position for {symbol}: {position}")
        
        # Calculate base spread
        base_spread = mid_price * self.config['target_spread_pct']
        logger.info(f"Base spread for {symbol}: {base_spread} ({self.config['target_spread_pct']} of {mid_price})")
        
        # Adjust spread based on inventory
        inventory_skew = min(
            abs(position) * self.config['inventory_skew_factor'],
            self.config['max_inventory_skew']
        )
        logger.info(f"Inventory skew for {symbol}: {inventory_skew}")
        
        if position > 0:  # Long position, widen ask spread
            bid_spread = base_spread * (1 - inventory_skew)
            ask_spread = base_spread * (1 + inventory_skew)
            logger.info(f"Long position for {symbol}, widening ask spread")
        elif position < 0:  # Short position, widen bid spread
            bid_spread = base_spread * (1 + inventory_skew)
            ask_spread = base_spread * (1 - inventory_skew)
            logger.info(f"Short position for {symbol}, widening bid spread")
        else:  # Flat position, equal spreads
            bid_spread = base_spread
            ask_spread = base_spread
            logger.info(f"Flat position for {symbol}, equal spreads")
        
        # Ensure spreads are within limits
        min_spread = mid_price * self.config['min_spread_pct']
        max_spread = mid_price * self.config['max_spread_pct']
        
        bid_spread = max(min_spread, min(bid_spread, max_spread))
        ask_spread = max(min_spread, min(ask_spread, max_spread))
        
        logger.info(f"Adjusted spreads for {symbol}: bid={bid_spread}, ask={ask_spread} (min: {min_spread}, max: {max_spread})")
        
        # Calculate bid and ask prices
        bid_price = mid_price - bid_spread
        ask_price = mid_price + ask_spread
        
        # Round to appropriate decimal places
        bid_price = round(bid_price, 2)
        ask_price = round(ask_price, 2)
        
        logger.info(f"Final quotes for {symbol}: bid={bid_price}, ask={ask_price}, spread={ask_price - bid_price}")
        
        return bid_price, ask_price
    
    def place_order(self, symbol: str, side: str, price: float, quantity: int) -> Dict[str, Any]:
        """
        Place a new order
        
        Args:
            symbol (str): The symbol to trade
            side (str): '1' for buy, '2' for sell
            price (float): The limit price
            quantity (int): The quantity to trade
            
        Returns:
            Dict[str, Any]: Order information
        """
        # Generate a unique order ID
        order_id = str(uuid.uuid4())[:8]
        
        # Create FIX message
        fix_message = f"11={order_id};54={side};55={symbol};38={quantity};44={price};49={self.trader_id}"
        
        logger.info(f"Attempting to place order: {symbol} {side} {quantity} @ {price} (ID: {order_id})")
        logger.info(f"Current active orders before placement: {len(self.active_orders)}")
        
        # Submit order
        try:
            logger.info(f"Sending FIX message: {fix_message}")
            result = baripool.on_new_order(fix_message)
            logger.info(f"Received response: {result}")
            
            # Parse the result
            if "ORDER SENT" in result:
                # Order was accepted
                self.active_orders[order_id] = {
                    'symbol': symbol,
                    'side': side,
                    'price': price,
                    'quantity': quantity,
                    'time': datetime.now().strftime("%H:%M:%S")
                }
                
                logger.info(f"Order placed successfully: {symbol} {side} {quantity} @ {price} (ID: {order_id})")
                logger.info(f"Active orders after placement: {len(self.active_orders)}")
                return {
                    'status': 'success',
                    'order_id': order_id,
                    'message': result
                }
            else:
                # Order was rejected
                logger.warning(f"Order rejected: {result}")
                return {
                    'status': 'error',
                    'message': result
                }
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error placing order: {str(e)}"
            }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            order_id (str): The order ID to cancel
            
        Returns:
            Dict[str, Any]: Status information
        """
        logger.info(f"Attempting to cancel order: {order_id}")
        logger.info(f"Current active orders before cancellation: {len(self.active_orders)}")
        
        if order_id not in self.active_orders:
            logger.warning(f"Order {order_id} not found in active orders")
            return {
                'status': 'error',
                'message': f"Order {order_id} not found in active orders"
            }
        
        try:
            # Call the baripool cancel order function
            baripool.on_cancel_order(order_id)
            
            # Remove from active orders
            del self.active_orders[order_id]
            
            logger.info(f"Order canceled: {order_id}")
            logger.info(f"Active orders after cancellation: {len(self.active_orders)}")
            return {
                'status': 'success',
                'message': f"Order {order_id} canceled successfully"
            }
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error canceling order: {str(e)}"
            }
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """
        Cancel all active orders
        
        Returns:
            Dict[str, Any]: Status information
        """
        if not self.active_orders:
            return {
                'status': 'success',
                'message': "No active orders to cancel"
            }
        
        canceled_count = 0
        error_count = 0
        
        for order_id in list(self.active_orders.keys()):
            result = self.cancel_order(order_id)
            if result['status'] == 'success':
                canceled_count += 1
            else:
                error_count += 1
        
        logger.info(f"Canceled {canceled_count} orders, {error_count} errors")
        return {
            'status': 'success',
            'message': f"Canceled {canceled_count} orders, {error_count} errors"
        }
    
    def lift_quote(self, symbol: str, price: float, quantity: int, side: str) -> Dict[str, Any]:
        """
        Lift a quote from the order book
        
        Args:
            symbol (str): The symbol to trade
            price (float): The price to lift
            quantity (int): The quantity to trade
            side (str): 'buy' or 'sell'
            
        Returns:
            Dict[str, Any]: Status information
        """
        logger.info(f"Lifting {side} quote for {symbol} at {price} for {quantity} shares")
        
        # Convert side to FIX format
        fix_side = '1' if side == 'buy' else '2'
        
        # Place the order
        result = self.place_order(symbol, fix_side, price, quantity)
        
        if result['status'] == 'success':
            logger.info(f"Successfully lifted quote: {result['message']}")
            return {
                'status': 'success',
                'message': f"Successfully lifted {side} quote for {symbol} at {price} for {quantity} shares"
            }
        else:
            logger.warning(f"Failed to lift quote: {result['message']}")
            return {
                'status': 'error',
                'message': f"Failed to lift quote: {result['message']}"
            }
    
    def update_position(self) -> None:
        """
        Update the current position based on filled orders
        """
        logger.info(f"Updating position. Current active orders: {len(self.active_orders)}")
        
        # Use the portfolio module to get the latest positions
        try:
            # Get portfolio data for this trader
            portfolio_data = portfolio.get_portfolio(self.trader_id)
            
            # Update our position dictionary from portfolio data
            self.position = {}
            for position in portfolio_data['open_positions']:
                symbol = position['symbol']
                quantity = position['quantity']
                self.position[symbol] = quantity
            
            # Update performance metrics
            self.performance_metrics['realized_pnl'] = portfolio_data['total_realized_pnl']
            self.performance_metrics['unrealized_pnl'] = portfolio_data['total_unrealized_pnl']
            self.performance_metrics['total_trades'] = len(portfolio_data['filled_trades'])
            
            logger.info(f"Updated positions from portfolio: {self.position}")
        except Exception as e:
            logger.error(f"Error updating position from portfolio: {str(e)}")
            
            # Fallback to the original method if portfolio module fails
            try:
                logger.info("Falling back to fillcontainer method for position updates")
                for key, execution_report in baripool.fillcontainer.items():
                    # Only include actual executions (ExecType=F for Fill or Partial Fill)
                    if '150' in execution_report and execution_report['150'] in ['1', '2']:  # 1=Partial Fill, 2=Fill
                        # Check if this trade belongs to our trader
                        if execution_report.get('49') == self.trader_id:
                            symbol = execution_report.get('55', 'Unknown')
                            side = execution_report.get('54', '1')  # 1=Buy, 2=Sell
                            quantity = int(execution_report.get('32', '0'))  # LastQty
                            
                            logger.info(f"Processing execution: {symbol} {side} {quantity} (Order ID: {key})")
                            
                            # Update position
                            if symbol not in self.position:
                                self.position[symbol] = 0
                            
                            if side == '1':  # Buy
                                self.position[symbol] += quantity
                            else:  # Sell
                                self.position[symbol] -= quantity
                            
                            # Update performance metrics
                            self.performance_metrics['total_trades'] += 1
                            
                            # Remove from active orders if fully filled
                            order_id = key.split('_')[0]
                            if order_id in self.active_orders:
                                if execution_report['150'] == '2':  # Fully filled
                                    logger.info(f"Order {order_id} fully filled, removing from active orders")
                                    del self.active_orders[order_id]
                                else:  # Partially filled
                                    logger.info(f"Order {order_id} partially filled, updating quantity")
                                    self.active_orders[order_id]['quantity'] -= quantity
            except Exception as e:
                logger.error(f"Error updating position from fillcontainer: {str(e)}")
        
        logger.info(f"Position update complete. Active orders: {len(self.active_orders)}")
    
    def check_risk_limits(self) -> Tuple[bool, str]:
        """
        Check if any risk limits are breached
        
        Returns:
            Tuple[bool, str]: (is_breached, message)
        """
        # Check position limits
        for symbol, quantity in self.position.items():
            if abs(quantity) > self.config['max_position']:
                return True, f"Position limit breached for {symbol}: {quantity} > {self.config['max_position']}"
        
        # Check notional exposure
        total_notional = 0
        for symbol, quantity in self.position.items():
            market_price = self.get_current_price(symbol)
            if market_price is not None:
                total_notional += abs(quantity * market_price)
        
        if total_notional > self.config['max_notional']:
            return True, f"Notional exposure limit breached: {total_notional} > {self.config['max_notional']}"
        
        # Check drawdown
        # This would require tracking P&L history, which we don't do in this simple version
        # For now, we'll just check if unrealized P&L is negative and exceeds max_drawdown
        if self.performance_metrics['unrealized_pnl'] < -self.config['max_drawdown']:
            return True, f"Drawdown limit breached: {self.performance_metrics['unrealized_pnl']} < -{self.config['max_drawdown']}"
        
        return False, "All risk limits within bounds"
    
    def rebalance_orders(self) -> Dict[str, Any]:
        """
        Rebalance orders for all symbols
        
        Returns:
            Dict[str, Any]: Status information
        """
        if not self.is_running or self.is_paused:
            logger.info(f"Market maker status: running={self.is_running}, paused={self.is_paused}")
            return {
                'status': 'error',
                'message': "Market maker is not running or is paused"
            }
        
        logger.info("Starting order rebalancing process")
        
        # Update position first to ensure we have the latest position data
        self.update_position()
        logger.info(f"Current positions: {self.position}")
        
        # Check risk limits
        is_breached, message = self.check_risk_limits()
        if is_breached:
            logger.warning(f"Risk limits breached: {message}")
            # We could stop the market maker here, but for now we'll just log a warning
        
        # Process each symbol
        results = {}
        for symbol in self.config['symbols']:
            logger.info(f"Processing symbol: {symbol}")
            
            # Calculate optimal quotes
            bid_price, ask_price = self.calculate_optimal_quotes(symbol)
            if bid_price is None or ask_price is None:
                logger.warning(f"Could not calculate optimal quotes for {symbol}")
                continue
            
            logger.info(f"Calculated quotes for {symbol}: bid={bid_price}, ask={ask_price}")
            
            # Cancel existing orders for this symbol
            symbol_orders = [order_id for order_id, order in self.active_orders.items() if order['symbol'] == symbol]
            if symbol_orders:
                logger.info(f"Canceling {len(symbol_orders)} existing orders for {symbol}")
                for order_id in symbol_orders:
                    self.cancel_order(order_id)
            else:
                logger.info(f"No existing orders to cancel for {symbol}")
            
            # Place new orders
            logger.info(f"Placing new orders for {symbol}: bid={bid_price}, ask={ask_price}, size={self.config['default_order_size']}")
            bid_result = self.place_order(symbol, '1', bid_price, self.config['default_order_size'])
            ask_result = self.place_order(symbol, '2', ask_price, self.config['default_order_size'])
            
            results[symbol] = {
                'bid': bid_result,
                'ask': ask_result
            }
            
            logger.info(f"Order results for {symbol}: bid={bid_result['status']}, ask={ask_result['status']}")
        
        # Update performance metrics
        self.performance_metrics['last_update'] = datetime.now()
        
        return {
            'status': 'success',
            'message': "Orders rebalanced successfully",
            'results': results
        }
    
    def run(self) -> None:
        """
        Main loop for the market making algorithm
        This should be run in a separate thread
        """
        logger.info(f"Market maker run loop started for trader: {self.trader_id}")
        logger.info(f"Initial configuration: {self.config}")
        logger.info(f"Initial status: running={self.is_running}, paused={self.is_paused}")
        
        iteration_count = 0
        while self.is_running:
            iteration_count += 1
            logger.info(f"Starting iteration {iteration_count}")
            
            if not self.is_paused:
                logger.info("Market maker is active, rebalancing orders")
                result = self.rebalance_orders()
                logger.info(f"Rebalance result: {result['status']}")
                if result['status'] == 'error':
                    logger.warning(f"Rebalance error: {result['message']}")
            else:
                logger.info("Market maker is paused, skipping rebalance")
            
            # Sleep for the rebalance interval
            logger.info(f"Sleeping for {self.config['rebalance_interval']} seconds")
            time.sleep(self.config['rebalance_interval'])
        
        logger.info(f"Market maker run loop stopped for trader: {self.trader_id}")

# Create a singleton instance
market_maker = MarketMaker()

# Example usage
if __name__ == "__main__":
    print("Market maker module loaded. Use the API endpoints to control the market maker.")