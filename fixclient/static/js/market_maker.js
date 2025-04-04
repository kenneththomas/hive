// Market Maker JavaScript

// Global variables
let marketMakerStatus = 'stopped';
let updateInterval = null;
let config = {
    symbols: ['AAPL'],
    maxPosition: 1000,
    maxNotional: 100000,
    maxDrawdown: 1000,
    targetSpreadPct: 0.001,
    minSpreadPct: 0.0005,
    maxSpreadPct: 0.005,
    defaultOrderSize: 100,
    minOrderSize: 10,
    maxOrderSize: 500,
    priceAdjustmentStep: 0.0001,
    rebalanceInterval: 5,
    priceAwayThreshold: 0.01,
    inventorySkewFactor: 0.0002,
    maxInventorySkew: 0.002
};

// DOM Elements
const startButton = document.getElementById('start-market-maker');
const stopButton = document.getElementById('stop-market-maker');
const pauseButton = document.getElementById('pause-market-maker');
const resumeButton = document.getElementById('resume-market-maker');
const emergencyStopButton = document.getElementById('emergency-stop');
const togglePriceSourceButton = document.getElementById('toggle-price-source');
const marketMakerStatusElement = document.getElementById('market-maker-status');
const priceSourceStatusElement = document.getElementById('price-source-status');
const saveConfigButton = document.getElementById('save-config');
const loadConfigButton = document.getElementById('load-config');
const refreshMarketDataButton = document.getElementById('refresh-market-data');
const cancelAllOrdersButton = document.getElementById('cancel-all-orders');
const clearLogButton = document.getElementById('clear-log');
const logContent = document.getElementById('log-content');
const statusDisplay = document.getElementById('status-display');
const dateDisplay = document.getElementById('date-display');
const timeDisplay = document.getElementById('time-display');

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    initializeDateTime();
    loadConfig();
    setupEventListeners();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

// Initialize date and time displays
function initializeDateTime() {
    updateDateTime();
}

function updateDateTime() {
    const now = new Date();
    dateDisplay.textContent = now.toLocaleDateString();
    timeDisplay.textContent = now.toLocaleTimeString();
}

// Setup event listeners
function setupEventListeners() {
    // Control buttons
    startButton.addEventListener('click', startMarketMaker);
    stopButton.addEventListener('click', stopMarketMaker);
    pauseButton.addEventListener('click', pauseMarketMaker);
    resumeButton.addEventListener('click', resumeMarketMaker);
    emergencyStopButton.addEventListener('click', emergencyStop);
    togglePriceSourceButton.addEventListener('click', togglePriceSource);
    document.getElementById('rebalance-orders').addEventListener('click', rebalanceOrders);

    // Configuration buttons
    saveConfigButton.addEventListener('click', saveConfig);
    loadConfigButton.addEventListener('click', loadConfig);

    // Market data buttons
    refreshMarketDataButton.addEventListener('click', refreshMarketData);

    // Order management buttons
    cancelAllOrdersButton.addEventListener('click', cancelAllOrders);

    // Log buttons
    clearLogButton.addEventListener('click', clearLog);

    // Symbol selection
    document.getElementById('selected-symbol').addEventListener('change', (e) => {
        refreshMarketData(e.target.value);
    });
}

// Market Maker Control Functions
function startMarketMaker() {
    if (marketMakerStatus === 'stopped') {
        // Call the backend API to start the market maker
        fetch('/api/market-maker/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                marketMakerStatus = 'running';
                updateStatus();
                log('Market maker started');
                
                // Start periodic updates
                updateInterval = setInterval(() => {
                    refreshMarketData();
                    updatePositions();
                    updateOrders();
                }, 1000);
            } else {
                log(`Error starting market maker: ${data.message}`);
            }
        })
        .catch(error => {
            log(`Error starting market maker: ${error.message}`);
        });
    }
}

function stopMarketMaker() {
    if (marketMakerStatus === 'running' || marketMakerStatus === 'paused') {
        // Call the backend API to stop the market maker
        fetch('/api/market-maker/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    marketMakerStatus = 'stopped';
                    updateStatus();
                    log('Market maker stopped');
                    
                    // Clear update interval
                    if (updateInterval) {
                        clearInterval(updateInterval);
                        updateInterval = null;
                    }
                } else {
                    log(`Error stopping market maker: ${data.message || 'Unknown error'}`);
                }
            })
            .catch(error => {
                log(`Error stopping market maker: ${error.message}`);
            });
    }
}

function pauseMarketMaker() {
    if (marketMakerStatus === 'running') {
        marketMakerStatus = 'paused';
        updateStatus();
        log('Market maker paused');
        
        // Clear update interval
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
    }
}

function resumeMarketMaker() {
    if (marketMakerStatus === 'paused') {
        marketMakerStatus = 'running';
        updateStatus();
        log('Market maker resumed');
        
        // Restart periodic updates
        updateInterval = setInterval(() => {
            refreshMarketData();
            updatePositions();
            updateOrders();
        }, 1000);
    }
}

function emergencyStop() {
    // Call the backend API to stop the market maker
    fetch('/api/market-maker/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                marketMakerStatus = 'stopped';
                updateStatus();
                log('EMERGENCY STOP: Market maker stopped immediately');
                
                // Clear update interval
                if (updateInterval) {
                    clearInterval(updateInterval);
                    updateInterval = null;
                }
                
                // Cancel all orders
                cancelAllOrders();
            } else {
                log(`Error during emergency stop: ${data.message || 'Unknown error'}`);
            }
        })
        .catch(error => {
            log(`Error during emergency stop: ${error.message}`);
        });
}

function togglePriceSource() {
    fetch('/api/market-maker/toggle-price-source', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const source = data.use_real_market_data ? 'Real Market Data' : 'Baripool Order Book';
                priceSourceStatusElement.textContent = source;
                log(`Price source switched to ${source}`);
                
                // Refresh market data to reflect the new price source
                refreshMarketData();
            } else {
                log(`Error toggling price source: ${data.error}`);
            }
        })
        .catch(error => {
            log(`Error toggling price source: ${error.message}`);
        });
}

// Configuration Functions
function saveConfig() {
    // Get values from form
    config.symbols = document.getElementById('symbols').value.split(',').map(s => s.trim());
    config.maxPosition = parseInt(document.getElementById('max-position').value);
    config.maxNotional = parseInt(document.getElementById('max-notional').value);
    config.maxDrawdown = parseInt(document.getElementById('max-drawdown').value);
    config.targetSpreadPct = parseFloat(document.getElementById('target-spread-pct').value);
    config.minSpreadPct = parseFloat(document.getElementById('min-spread-pct').value);
    config.maxSpreadPct = parseFloat(document.getElementById('max-spread-pct').value);
    config.defaultOrderSize = parseInt(document.getElementById('default-order-size').value);
    config.minOrderSize = parseInt(document.getElementById('min-order-size').value);
    config.maxOrderSize = parseInt(document.getElementById('max-order-size').value);
    config.priceAdjustmentStep = parseFloat(document.getElementById('price-adjustment-step').value);
    config.rebalanceInterval = parseInt(document.getElementById('rebalance-interval').value);
    config.priceAwayThreshold = parseFloat(document.getElementById('price-away-threshold').value);
    config.inventorySkewFactor = parseFloat(document.getElementById('inventory-skew-factor').value);
    config.maxInventorySkew = parseFloat(document.getElementById('max-inventory-skew').value);

    // Save to localStorage
    localStorage.setItem('marketMakerConfig', JSON.stringify(config));
    log('Configuration saved');
}

function loadConfig() {
    // Load from localStorage
    const savedConfig = localStorage.getItem('marketMakerConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
        
        // Update form values
        document.getElementById('symbols').value = config.symbols.join(', ');
        document.getElementById('max-position').value = config.maxPosition;
        document.getElementById('max-notional').value = config.maxNotional;
        document.getElementById('max-drawdown').value = config.maxDrawdown;
        document.getElementById('target-spread-pct').value = config.targetSpreadPct;
        document.getElementById('min-spread-pct').value = config.minSpreadPct;
        document.getElementById('max-spread-pct').value = config.maxSpreadPct;
        document.getElementById('default-order-size').value = config.defaultOrderSize;
        document.getElementById('min-order-size').value = config.minOrderSize;
        document.getElementById('max-order-size').value = config.maxOrderSize;
        document.getElementById('price-adjustment-step').value = config.priceAdjustmentStep;
        document.getElementById('rebalance-interval').value = config.rebalanceInterval;
        document.getElementById('price-away-threshold').value = config.priceAwayThreshold;
        document.getElementById('inventory-skew-factor').value = config.inventorySkewFactor;
        document.getElementById('max-inventory-skew').value = config.maxInventorySkew;
        
        log('Configuration loaded');
    }
}

// Market Data Functions
function refreshMarketData(symbol = null) {
    if (!symbol) {
        symbol = document.getElementById('selected-symbol').value;
    }
    
    // Fetch current price
    fetch(`/api/market-data/price/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.price !== null && data.price !== undefined) {
                document.getElementById('current-price-value').textContent = `$${data.price.toFixed(2)}`;
            } else {
                document.getElementById('current-price-value').textContent = 'N/A';
                if (data.message) {
                    log(data.message);
                } else {
                    log(`No price data available for ${symbol}`);
                }
            }
            updateOrderBook(symbol);
        })
        .catch(error => {
            log(`Error fetching market data: ${error.message}`);
        });
}

function updateOrderBook(symbol) {
    // Fetch order book
    fetch(`/api/market-data/orderbook/${symbol}`)
        .then(response => response.json())
        .then(data => {
            updateOrderBookDisplay(data.bids, data.asks);
        })
        .catch(error => {
            log(`Error fetching order book: ${error.message}`);
        });
}

function updateOrderBookDisplay(bids, asks) {
    const bidsContainer = document.getElementById('bids-container');
    const asksContainer = document.getElementById('asks-container');
    
    // Clear existing entries
    bidsContainer.innerHTML = '';
    asksContainer.innerHTML = '';
    
    // Add bid entries
    bids.forEach(bid => {
        const entry = document.createElement('div');
        entry.className = 'order-book-entry bid';
        
        // Create a container for the quote and button
        const quoteContainer = document.createElement('div');
        quoteContainer.className = 'quote-container';
        
        // Create the quote text
        const quoteText = document.createElement('span');
        quoteText.textContent = `${bid.price.toFixed(2)} (${bid.quantity})`;
        quoteContainer.appendChild(quoteText);
        
        // Create the lift button
        const liftButton = document.createElement('button');
        liftButton.className = 'lift-button';
        liftButton.textContent = 'Lift';
        liftButton.onclick = () => liftQuote(bid.symbol, bid.price, bid.quantity, 'buy');
        quoteContainer.appendChild(liftButton);
        
        entry.appendChild(quoteContainer);
        bidsContainer.appendChild(entry);
    });
    
    // Add ask entries
    asks.forEach(ask => {
        const entry = document.createElement('div');
        entry.className = 'order-book-entry ask';
        
        // Create a container for the quote and button
        const quoteContainer = document.createElement('div');
        quoteContainer.className = 'quote-container';
        
        // Create the quote text
        const quoteText = document.createElement('span');
        quoteText.textContent = `${ask.price.toFixed(2)} (${ask.quantity})`;
        quoteContainer.appendChild(quoteText);
        
        // Create the lift button
        const liftButton = document.createElement('button');
        liftButton.className = 'lift-button';
        liftButton.textContent = 'Lift';
        liftButton.onclick = () => liftQuote(ask.symbol, ask.price, ask.quantity, 'sell');
        quoteContainer.appendChild(liftButton);
        
        entry.appendChild(quoteContainer);
        asksContainer.appendChild(entry);
    });
}

// Function to lift a quote from the order book
function liftQuote(symbol, price, quantity, side) {
    log(`Lifting ${side} quote for ${symbol} at ${price} for ${quantity} shares`);
    
    // Call the backend API to lift the quote
    fetch('/api/market-maker/lift-quote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            symbol: symbol,
            price: price,
            quantity: quantity,
            side: side
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log(`Successfully lifted quote: ${data.message}`);
            // Refresh market data, positions, and orders
            refreshMarketData(symbol);
            updatePositions();
            updateOrders();
        } else {
            log(`Error lifting quote: ${data.message}`);
        }
    })
    .catch(error => {
        log(`Error lifting quote: ${error.message}`);
    });
}

// Position and Order Management Functions
function updatePositions() {
    fetch('/api/positions')
        .then(response => response.json())
        .then(data => {
            updatePositionsTable(data);
            updatePositionSummary(data);
        })
        .catch(error => {
            log(`Error fetching positions: ${error.message}`);
        });
}

function updatePositionsTable(positions) {
    const tbody = document.getElementById('positions-table-body');
    tbody.innerHTML = '';
    
    if (!positions || positions.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="8" class="no-data-message">No positions available</td>';
        tbody.appendChild(emptyRow);
        return;
    }
    
    positions.forEach(position => {
        // Ensure all required properties exist with default values
        const avgPrice = position.avgPrice || 0;
        const currentPrice = position.currentPrice || 0;
        const marketValue = position.marketValue || 0;
        const pnl = position.pnl || 0;
        const pnlPct = position.pnlPct || 0;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${position.symbol || 'N/A'}</td>
            <td>${position.side || 'N/A'}</td>
            <td>${position.quantity || 0}</td>
            <td>$${avgPrice.toFixed(2)}</td>
            <td>$${currentPrice.toFixed(2)}</td>
            <td>$${marketValue.toFixed(2)}</td>
            <td>$${pnl.toFixed(2)}</td>
            <td>${pnlPct.toFixed(2)}%</td>
        `;
        tbody.appendChild(row);
    });
}

function updatePositionSummary(positions) {
    if (!positions || positions.length === 0) {
        document.getElementById('total-trades').textContent = '0';
        document.getElementById('realized-pnl').textContent = '$0.00';
        document.getElementById('unrealized-pnl').textContent = '$0.00';
        return;
    }
    
    const totalTrades = positions.reduce((sum, pos) => sum + (pos.trades || 0), 0);
    const realizedPnl = positions.reduce((sum, pos) => sum + (pos.realizedPnl || 0), 0);
    const unrealizedPnl = positions.reduce((sum, pos) => sum + (pos.unrealizedPnl || 0), 0);
    
    document.getElementById('total-trades').textContent = totalTrades;
    document.getElementById('realized-pnl').textContent = `$${realizedPnl.toFixed(2)}`;
    document.getElementById('unrealized-pnl').textContent = `$${unrealizedPnl.toFixed(2)}`;
}

function updateOrders() {
    fetch('/api/orders/active')
        .then(response => response.json())
        .then(data => {
            updateOrdersTable(data);
            document.getElementById('active-orders-count').textContent = data.length;
        })
        .catch(error => {
            log(`Error fetching orders: ${error.message}`);
        });
}

function updateOrdersTable(orders) {
    const tbody = document.getElementById('active-orders-table-body');
    tbody.innerHTML = '';
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(order.time).toLocaleTimeString()}</td>
            <td>${order.id}</td>
            <td>${order.symbol}</td>
            <td>${order.side}</td>
            <td>$${order.price.toFixed(2)}</td>
            <td>${order.quantity}</td>
            <td>${order.status}</td>
            <td>
                <button onclick="cancelOrder('${order.id}')" class="action-button">Cancel</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function cancelOrder(orderId) {
    fetch(`/api/orders/${orderId}/cancel`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            log(`Order ${orderId} cancelled`);
            updateOrders();
        })
        .catch(error => {
            log(`Error cancelling order: ${error.message}`);
        });
}

function cancelAllOrders() {
    fetch('/api/orders/cancel-all', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            log('All orders cancelled');
            updateOrders();
        })
        .catch(error => {
            log(`Error cancelling all orders: ${error.message}`);
        });
}

// Function to manually trigger rebalancing
function rebalanceOrders() {
    fetch('/api/market-maker/rebalance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log('Orders rebalanced successfully');
            // Refresh market data, positions, and orders
            refreshMarketData();
            updatePositions();
            updateOrders();
        } else {
            log(`Error rebalancing orders: ${data.message}`);
        }
    })
    .catch(error => {
        log(`Error rebalancing orders: ${error.message}`);
    });
}

// Utility Functions
function updateStatus() {
    marketMakerStatusElement.textContent = marketMakerStatus.charAt(0).toUpperCase() + marketMakerStatus.slice(1);
    
    // Update button states
    startButton.disabled = marketMakerStatus !== 'stopped';
    stopButton.disabled = marketMakerStatus === 'stopped';
    pauseButton.disabled = marketMakerStatus !== 'running';
    resumeButton.disabled = marketMakerStatus !== 'paused';
    
    // Update status display
    statusDisplay.textContent = marketMakerStatus.toUpperCase();
}

function log(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContent.appendChild(logEntry);
    logContent.scrollTop = logContent.scrollHeight;
}

function clearLog() {
    logContent.innerHTML = '';
    log('Log cleared');
} 