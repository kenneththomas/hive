// Submit form function
function submitForm() {
    const formData = new FormData(document.getElementById('order-form'));
    
    fetch('/submit_order', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const outputBox = document.getElementById('output-box');
        outputBox.innerHTML += '\n' + data.output;
        // Auto-scroll to the bottom
        outputBox.scrollTop = outputBox.scrollHeight;
        
        // Update status and reset after delay
        document.getElementById('status-display').textContent = data.status;
        setTimeout(() => {
            document.getElementById('status-display').textContent = 'READY';
        }, 2000);
    });
}

// Clear form function
function clearForm() {
    document.getElementById('symbol').value = '';
    document.getElementById('quantity').value = '';
    document.getElementById('price').value = '';
    document.getElementById('sender').value = '';
}

// Show help function
function showHelp() {
    const outputBox = document.getElementById('output-box');
    outputBox.innerHTML += '\n[HELP] BariPool Trading Terminal Commands:\n';
    outputBox.innerHTML += 'F1: Display this help message\n';
    outputBox.innerHTML += 'F2: Submit order form\n';
    outputBox.innerHTML += 'F3: Clear all form fields\n';
    outputBox.innerHTML += 'F4: Exit application\n';
    // Auto-scroll to the bottom
    outputBox.scrollTop = outputBox.scrollHeight;
}

// Support for keyboard shortcuts (F1-F4)
document.addEventListener('keydown', function(event) {
    if (event.key === 'F1') {
        event.preventDefault();
        showHelp();
    } else if (event.key === 'F2') {
        event.preventDefault();
        submitForm();
    } else if (event.key === 'F3') {
        event.preventDefault();
        clearForm();
    } else if (event.key === 'F4') {
        event.preventDefault();
        window.close();
    }
}); 

function updateTime() {
    const now = new Date();
    
    // Update the time display elements
    const timeElement = document.getElementById('time-display');
    const dateElement = document.getElementById('date-display');
    
    if (timeElement) {
        timeElement.textContent = now.toLocaleTimeString();
    }
    if (dateElement) {
        dateElement.textContent = now.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
    }
    
    // Also update any other time elements if they exist
    const currentTimeElement = document.getElementById('current-time');
    const currentDateElement = document.getElementById('current-date');
    
    if (currentTimeElement) {
        currentTimeElement.textContent = now.toLocaleTimeString();
    }
    if (currentDateElement) {
        currentDateElement.textContent = now.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
    }
}

// Update time immediately and then every second
updateTime();
setInterval(updateTime, 1000);


// Add this to your existing JavaScript file

// Helper function to create an order table
function createOrderTable(orders, sideLabel, symbol, changes) {
    const table = document.createElement('table');
    
    // Create header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Remove 'Orig Qty' from headers
    const headers = [sideLabel, 'Order ID', 'Sender', 'Price', 'Qty'];
    headers.forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body rows
    const tbody = document.createElement('tbody');
    
    if (orders.length === 0) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = headers.length;
        emptyCell.textContent = 'No orders';
        emptyCell.className = 'empty-message';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    } else {
        orders.forEach(order => {
            const row = document.createElement('tr');
            
            // Add appropriate animation class based on order status
            if (changes && symbol) {
                const side = sideLabel === 'BID' ? 'buys' : 'sells';
                
                if (changes.newOrders[symbol] && changes.newOrders[symbol][side].includes(order.order_id)) {
                    row.classList.add('new-order');
                } else if (changes.partialFills[symbol] && changes.partialFills[symbol][side].includes(order.order_id)) {
                    row.classList.add('partial-fill');
                } else if (changes.fullFills[symbol] && changes.fullFills[symbol][side].includes(order.order_id)) {
                    row.classList.add('full-fill');
                }
            }
            
            // Side indicator cell (just for visual distinction)
            const sideCell = document.createElement('td');
            sideCell.className = sideLabel === 'BID' ? 'bid-indicator' : 'ask-indicator';
            sideCell.textContent = sideLabel;
            row.appendChild(sideCell);
            
            // Order details
            const orderIdCell = document.createElement('td');
            orderIdCell.textContent = order.order_id;
            row.appendChild(orderIdCell);
            
            const senderCell = document.createElement('td');
            senderCell.textContent = order.sender;
            row.appendChild(senderCell);
            
            const priceCell = document.createElement('td');
            priceCell.textContent = formatPrice(order.price);
            row.appendChild(priceCell);
            
            const qtyCell = document.createElement('td');
            qtyCell.textContent = formatQuantity(order.remaining_qty);
            row.appendChild(qtyCell);
            
            tbody.appendChild(row);
            
            // Add a temporary highlight effect for new rows
            row.classList.add('highlight');
            setTimeout(() => {
                row.classList.remove('highlight');
            }, 1000);
        });
    }
    
    table.appendChild(tbody);
    return table;
}

// Format price with 2 decimal places
function formatPrice(price) {
    return parseFloat(price).toFixed(2);
}

// Format quantity with commas for thousands
function formatQuantity(qty) {
    return parseInt(qty).toLocaleString();
}

// Global variable to store the complete order book data
let fullOrderBookData = {};
let currentSymbolFilter = '';

// Global variable to store previous state of the order book for comparison
let previousOrderBookData = {};

// Function to fetch and update the order book
function updateOrderBook() {
    fetch('/get_order_book')
        .then(response => response.json())
        .then(data => {
            // Analyze changes to determine what animations to show
            const changes = analyzeOrderChanges(previousOrderBookData, data);
            
            // Store the current data for next comparison
            previousOrderBookData = JSON.parse(JSON.stringify(data));
            
            // Store the full data
            fullOrderBookData = data;
            
            // Display filtered data with animations
            displayOrderBook(data, changes);
        })
        .catch(error => {
            console.error('Error fetching order book:', error);
            document.getElementById('order-book-container').innerHTML = 
                '<div class="error-message">Error loading order book data</div>';
        });
}

// Function to analyze changes between previous and current order book
function analyzeOrderChanges(previous, current) {
    const changes = {
        newOrders: {},
        partialFills: {},
        fullFills: {}
    };
    
    // If no previous data, all orders are considered new
    if (!previous || Object.keys(previous).length === 0) {
        for (const symbol in current) {
            changes.newOrders[symbol] = {
                buys: current[symbol].buys.map(order => order.order_id),
                sells: current[symbol].sells.map(order => order.order_id)
            };
        }
        return changes;
    }
    
    // Check each symbol
    for (const symbol in current) {
        changes.newOrders[symbol] = { buys: [], sells: [] };
        changes.partialFills[symbol] = { buys: [], sells: [] };
        changes.fullFills[symbol] = { buys: [], sells: [] };
        
        // If the symbol is new
        if (!previous[symbol]) {
            changes.newOrders[symbol] = {
                buys: current[symbol].buys.map(order => order.order_id),
                sells: current[symbol].sells.map(order => order.order_id)
            };
            continue;
        }
        
        // Check buys
        analyzeOrderSide(
            previous[symbol].buys, 
            current[symbol].buys, 
            changes.newOrders[symbol].buys,
            changes.partialFills[symbol].buys,
            changes.fullFills[symbol].buys
        );
        
        // Check sells
        analyzeOrderSide(
            previous[symbol].sells, 
            current[symbol].sells, 
            changes.newOrders[symbol].sells,
            changes.partialFills[symbol].sells,
            changes.fullFills[symbol].sells
        );
    }
    
    // Check for fully filled orders (those that were in previous but not in current)
    for (const symbol in previous) {
        if (!changes.fullFills[symbol]) {
            changes.fullFills[symbol] = { buys: [], sells: [] };
        }
        
        if (current[symbol]) {
            // Find orders that existed in previous but are gone in current
            const prevBuyIds = previous[symbol].buys.map(order => order.order_id);
            const currBuyIds = current[symbol].buys.map(order => order.order_id);
            const prevSellIds = previous[symbol].sells.map(order => order.order_id);
            const currSellIds = current[symbol].sells.map(order => order.order_id);
            
            // Orders that disappeared are considered fully filled
            prevBuyIds.forEach(id => {
                if (!currBuyIds.includes(id)) {
                    changes.fullFills[symbol].buys.push(id);
                }
            });
            
            prevSellIds.forEach(id => {
                if (!currSellIds.includes(id)) {
                    changes.fullFills[symbol].sells.push(id);
                }
            });
        }
    }
    
    return changes;
}

// Helper function to analyze changes in one side of the order book
function analyzeOrderSide(prevOrders, currOrders, newOrders, partialFills, fullFills) {
    const prevOrderMap = {};
    
    // Create a map of previous orders by ID
    prevOrders.forEach(order => {
        prevOrderMap[order.order_id] = order;
    });
    
    // Check each current order
    currOrders.forEach(order => {
        if (!prevOrderMap[order.order_id]) {
            // This is a new order
            newOrders.push(order.order_id);
        } else if (parseFloat(order.remaining_qty) < parseFloat(prevOrderMap[order.order_id].remaining_qty)) {
            // This order has been partially filled
            partialFills.push(order.order_id);
        }
    });
}

// Update the display function to use the changes information
function displayOrderBook(data, changes) {
    const container = document.getElementById('order-book-container');
    
    // Clear previous content
    container.innerHTML = '';
    
    // Filter data if a filter is applied
    let filteredData = {};
    if (currentSymbolFilter) {
        // Case-insensitive filter
        const filterLower = currentSymbolFilter.toLowerCase();
        
        for (const symbol in data) {
            if (symbol.toLowerCase().includes(filterLower)) {
                filteredData[symbol] = data[symbol];
            }
        }
    } else {
        filteredData = data;
    }
    
    // Check if there are any books after filtering
    if (Object.keys(filteredData).length === 0) {
        if (currentSymbolFilter) {
            container.innerHTML = `<div class="no-data-message">No matching symbols for "${currentSymbolFilter}"</div>`;
        } else {
            container.innerHTML = '<div class="no-data-message">No active orders in the book</div>';
        }
        return;
    }
    
    // Create a section for each symbol
    for (const symbol in filteredData) {
        const bookData = filteredData[symbol];
        const symbolSection = document.createElement('div');
        symbolSection.className = 'symbol-section';
        
        // Create symbol header
        const symbolHeader = document.createElement('h3');
        symbolHeader.textContent = symbol;
        symbolSection.appendChild(symbolHeader);
        
        // Create book display with buy and sell sides
        const bookDisplay = document.createElement('div');
        bookDisplay.className = 'book-display';
        
        // Buy side (bids) - now with changes parameter
        const buyTable = createOrderTable(bookData.buys, 'BID', symbol, changes);
        buyTable.className = 'order-table buy-table';
        
        // Sell side (asks) - now with changes parameter
        const sellTable = createOrderTable(bookData.sells, 'ASK', symbol, changes);
        sellTable.className = 'order-table sell-table';
        
        // Add tables to book display
        bookDisplay.appendChild(buyTable);
        bookDisplay.appendChild(sellTable);
        symbolSection.appendChild(bookDisplay);
        
        // Add the symbol section to the container
        container.appendChild(symbolSection);
    }
}

// Global variable to store recent trades
let recentTrades = [];
let lastTradeCount = 0;

// Function to fetch and update the trade ticker
function updateTradeTicker() {
    fetch('/get_recent_trades')
        .then(response => response.json())
        .then(data => {
            // Check if we have new trades
            const hasNewTrades = data.length > lastTradeCount;
            lastTradeCount = data.length;
            
            // Store the trades
            recentTrades = data;
            
            // Display the trades
            displayTradeTicker(recentTrades, hasNewTrades);
        })
        .catch(error => {
            console.error('Error fetching recent trades:', error);
            document.getElementById('trade-ticker').innerHTML = 
                '<div class="error-message">Error loading trade data</div>';
        });
}

// Function to display the trade ticker
function displayTradeTicker(trades, hasNewTrades) {
    const tickerContainer = document.getElementById('trade-ticker');
    
    // Clear previous content
    tickerContainer.innerHTML = '';
    
    // Check if there are any trades
    if (trades.length === 0) {
        tickerContainer.innerHTML = '<div class="no-trades-message">No recent trades</div>';
        return;
    }
    
    // Create a table for the trades
    const table = document.createElement('table');
    table.className = 'ticker-table';
    
    // Create header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const headers = ['Time', 'Symbol', 'Quantity', 'Price', 'Buyer', 'Seller'];
    headers.forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body rows
    const tbody = document.createElement('tbody');
    
    trades.forEach((trade, index) => {
        const row = document.createElement('tr');
        
        // Add new trade animation
        if (hasNewTrades && index === 0) {
            row.classList.add('new-trade');
        }
        
        // Time cell
        const timeCell = document.createElement('td');
        timeCell.textContent = trade.time;
        row.appendChild(timeCell);
        
        // Symbol cell
        const symbolCell = document.createElement('td');
        symbolCell.textContent = trade.symbol;
        symbolCell.className = 'ticker-symbol';
        row.appendChild(symbolCell);
        
        // Quantity cell
        const qtyCell = document.createElement('td');
        qtyCell.textContent = formatQuantity(trade.quantity);
        row.appendChild(qtyCell);
        
        // Price cell
        const priceCell = document.createElement('td');
        priceCell.textContent = formatPrice(trade.price);
        priceCell.className = 'ticker-price';
        row.appendChild(priceCell);
        
        // Buyer cell
        const buyerCell = document.createElement('td');
        buyerCell.textContent = trade.buyer;
        buyerCell.className = 'ticker-buyer';
        row.appendChild(buyerCell);
        
        // Seller cell
        const sellerCell = document.createElement('td');
        sellerCell.textContent = trade.seller;
        sellerCell.className = 'ticker-seller';
        row.appendChild(sellerCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    tickerContainer.appendChild(table);
}

// Add this to your existing window.onload function
window.onload = function() {
    // Your existing code...
    
    // Initial update of the order book and trade ticker
    updateOrderBook();
    updateTradeTicker();
    
    // Set intervals to update the data
    setInterval(updateOrderBook, 1000);
    setInterval(updateTradeTicker, 1000);
    
    // Set up symbol filter functionality
    document.getElementById('apply-filter').addEventListener('click', function() {
        currentSymbolFilter = document.getElementById('symbol-filter').value.trim();
        displayOrderBook(fullOrderBookData);
    });
    
    document.getElementById('reset-filter').addEventListener('click', function() {
        document.getElementById('symbol-filter').value = '';
        currentSymbolFilter = '';
        displayOrderBook(fullOrderBookData);
    });
    
    // Allow pressing Enter in the filter input to apply the filter
    document.getElementById('symbol-filter').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            currentSymbolFilter = this.value.trim();
            displayOrderBook(fullOrderBookData);
        }
    });
};