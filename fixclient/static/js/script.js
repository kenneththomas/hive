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
    table.className = 'order-table';
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Define headers based on side (mirrored for ask)
    let headers;
    if (sideLabel === 'BID') {
        headers = [
            'Order ID',
            'Sender',
            'Quantity',
            'Price'
        ];
    } else {
        headers = [
            'Price',
            'Quantity',
            'Sender',
            'Order ID'
        ];
    }
    
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    if (!orders || orders.length === 0) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = headers.length;
        emptyCell.className = 'empty-message';
        emptyCell.textContent = `No ${sideLabel.toLowerCase()} orders`;
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    } else {
        // Find the maximum quantity for scaling the size indicators
        const maxQty = Math.max(...orders.map(order => parseInt(order.remaining_qty)));
        
        orders.forEach(order => {
            const row = document.createElement('tr');
            row.className = 'order-row';
            
            // Add data attributes for context menu
            row.dataset.side = sideLabel;
            row.dataset.symbol = symbol;
            row.dataset.price = order.price;
            row.dataset.qty = order.remaining_qty;
            row.dataset.orderId = order.order_id;
            row.dataset.sender = order.sender;
            
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
            
            // Create size indicator
            const sizeIndicator = document.createElement('div');
            sizeIndicator.className = 'size-indicator';
            const qtyPercent = (parseInt(order.remaining_qty) / maxQty) * 100;
            sizeIndicator.style.width = `${qtyPercent}%`;
            
            // Position the size indicator based on side
            if (sideLabel === 'BID') {
                sizeIndicator.style.right = '0';
            } else {
                sizeIndicator.style.left = '0';
            }
            
            row.appendChild(sizeIndicator);
            
            // Create cells in the correct order based on side
            if (sideLabel === 'BID') {
                // BID order: Order ID, Sender, Quantity, Price
                const orderIdCell = document.createElement('td');
                orderIdCell.textContent = order.order_id;
                row.appendChild(orderIdCell);
                
                const senderCell = document.createElement('td');
                senderCell.textContent = order.sender;
                row.appendChild(senderCell);
                
                const qtyCell = document.createElement('td');
                qtyCell.textContent = formatQuantity(order.remaining_qty);
                row.appendChild(qtyCell);
                
                const priceCell = document.createElement('td');
                priceCell.textContent = formatPrice(order.price);
                row.appendChild(priceCell);
            } else {
                // ASK order: Price, Quantity, Sender, Order ID
                const priceCell = document.createElement('td');
                priceCell.textContent = formatPrice(order.price);
                row.appendChild(priceCell);
                
                const qtyCell = document.createElement('td');
                qtyCell.textContent = formatQuantity(order.remaining_qty);
                row.appendChild(qtyCell);
                
                const senderCell = document.createElement('td');
                senderCell.textContent = order.sender;
                row.appendChild(senderCell);
                
                const orderIdCell = document.createElement('td');
                orderIdCell.textContent = order.order_id;
                row.appendChild(orderIdCell);
            }
            
            // Add right-click event listener for context menu
            row.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                
                // Show context menu
                const contextMenu = document.getElementById('context-menu');
                contextMenu.style.display = 'block';
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.style.top = `${e.pageY}px`;
                
                // Store order details in context menu for later use
                contextMenu.dataset.orderId = order.order_id;
                contextMenu.dataset.symbol = symbol;
                contextMenu.dataset.side = sideLabel;
                contextMenu.dataset.price = order.price;
                contextMenu.dataset.qty = order.remaining_qty;
                contextMenu.dataset.sender = order.sender;
                
                // Show cancel order option and hide other options
                document.getElementById('cancel-order').style.display = 'block';
                document.getElementById('trade-against').style.display = 'none';
                document.getElementById('close-position').style.display = 'none';
            });
            
            tbody.appendChild(row);
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
let selectedSymbol = null;

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
            
            // Update the symbol list
            updateSymbolList(data);
            
            // If a symbol is selected, update its order book
            if (selectedSymbol && data[selectedSymbol]) {
                displaySelectedOrderBook(selectedSymbol, data[selectedSymbol], changes);
            }
        })
        .catch(error => {
            console.error('Error fetching order book:', error);
            document.getElementById('selected-book-container').innerHTML = 
                '<div class="error-message">Error loading order book data</div>';
        });
}

// Function to update the symbol list
function updateSymbolList(data) {
    const symbolList = document.getElementById('symbol-list');
    
    // Clear the current list
    symbolList.innerHTML = '';
    
    // Get the search term
    const searchTerm = document.getElementById('symbol-search').value.toLowerCase();
    
    // Filter symbols based on search term
    const filteredSymbols = Object.keys(data).filter(symbol => 
        symbol.toLowerCase().includes(searchTerm)
    );
    
    // Sort symbols alphabetically
    filteredSymbols.sort();
    
    // Check if there are any symbols
    if (filteredSymbols.length === 0) {
        symbolList.innerHTML = '<div class="no-data-message">No matching symbols</div>';
        return;
    }
    
    // Create symbol items
    filteredSymbols.forEach(symbol => {
        const symbolItem = document.createElement('div');
        symbolItem.className = 'symbol-item';
        if (symbol === selectedSymbol) {
            symbolItem.classList.add('active');
        }
        
        symbolItem.textContent = symbol;
        symbolItem.dataset.symbol = symbol;
        
        // Add click event to select the symbol
        symbolItem.addEventListener('click', () => {
            selectSymbol(symbol);
        });
        
        symbolList.appendChild(symbolItem);
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

// Function to select a symbol and display its order book
function selectSymbol(symbol) {
    // Update the selected symbol
    selectedSymbol = symbol;
    
    // Update the active class on symbol items
    document.querySelectorAll('.symbol-item').forEach(item => {
        if (item.dataset.symbol === symbol) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Display the order book for the selected symbol
    if (fullOrderBookData[symbol]) {
        displaySelectedOrderBook(symbol, fullOrderBookData[symbol]);
    }
}

// Function to display the order book for a selected symbol
function displaySelectedOrderBook(symbol, bookData, changes) {
    const container = document.getElementById('selected-book-container');
    container.innerHTML = '';
    
    // Create symbol section
    const symbolSection = document.createElement('div');
    symbolSection.className = 'symbol-section';
    
    // Create symbol header
    const symbolHeader = document.createElement('h3');
    symbolHeader.textContent = symbol;
    symbolSection.appendChild(symbolHeader);
    
    // Create book display
    const bookDisplay = document.createElement('div');
    bookDisplay.className = 'book-display';
    
    // Calculate mid price and spread
    let priceDisplay = document.createElement('div');
    priceDisplay.className = 'price-display';
    
    if (bookData.buys.length > 0 && bookData.sells.length > 0) {
        const highestBid = parseFloat(bookData.buys[0].price);
        const lowestAsk = parseFloat(bookData.sells[0].price);
        const midPrice = ((highestBid + lowestAsk) / 2).toFixed(2);
        const spread = (lowestAsk - highestBid).toFixed(2);
        const spreadPct = ((spread / midPrice) * 100).toFixed(2);
        
        priceDisplay.innerHTML = `
            <div>Mid Price: $${midPrice}</div>
            <div>Spread: $${spread} (${spreadPct}%)</div>
        `;
    } else {
        priceDisplay.textContent = 'Insufficient orders to calculate prices';
    }
    
    bookDisplay.appendChild(priceDisplay);
    
    // Create order book layout
    const orderBookLayout = document.createElement('div');
    orderBookLayout.className = 'order-book-layout';
    
    // Create tables container
    const orderBookTables = document.createElement('div');
    orderBookTables.className = 'order-book-tables';
    
    // Buy side (bids) - on the left
    const buyTable = createOrderTable(bookData.buys, 'BID', symbol, changes);
    buyTable.className = 'order-table buy-table';
    
    // Sell side (asks) - on the right
    const sellTable = createOrderTable(bookData.sells, 'ASK', symbol, changes);
    sellTable.className = 'order-table sell-table ask-table';
    
    // Add tables to container in the correct order (bids on left, asks on right)
    orderBookTables.appendChild(buyTable);
    orderBookTables.appendChild(sellTable);
    
    // Add the tables container to the layout
    orderBookLayout.appendChild(orderBookTables);
    
    // Add the layout to the book display
    bookDisplay.appendChild(orderBookLayout);
    
    // Add the book display to the symbol section
    symbolSection.appendChild(bookDisplay);
    
    // Add the symbol section to the container
    container.appendChild(symbolSection);
}

// Function to display the order book (legacy function, kept for compatibility)
function displayOrderBook(data, changes) {
    // This function is kept for compatibility but is no longer used
    // The new order book display is handled by updateSymbolList and displaySelectedOrderBook
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

// Tab Switching Functionality
function switchTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Deactivate all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show the selected tab pane
    document.getElementById(tabId + '-tab').classList.add('active');
    
    // Activate the clicked tab button
    document.querySelector(`.tab-button[data-tab="${tabId}"]`).classList.add('active');
}

// ScopeChat Functionality
let currentScopeId = '';
let isConnected = false;

// Connect to a scope ID
function connectToScope() {
    const scopeId = document.getElementById('scope-id').value.trim();
    
    if (!scopeId) {
        alert('Please enter a SCOPE ID');
        return;
    }
    
    currentScopeId = scopeId;
    isConnected = true;
    
    // Clear the chat display
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    
    // Add connection message
    const systemMessage = document.createElement('div');
    systemMessage.className = 'system-message';
    systemMessage.textContent = `Connected to SCOPE ID: ${scopeId}`;
    chatMessages.appendChild(systemMessage);
    
    // Load chat history
    fetchChatHistory(scopeId);
    
    // Update profile display
    updateProfileDisplay(scopeId);
    
    // Update UI to show connected state
    document.getElementById('connect-scope').textContent = 'Reconnect';
    document.getElementById('chat-input').focus();
}

// Fetch chat history for a scope ID
function fetchChatHistory(scopeId) {
    fetch(`/scope_chat/history?scope_id=${scopeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.history && data.history.length > 0) {
                displayChatHistory(data.history);
            }
        })
        .catch(error => {
            console.error('Error fetching chat history:', error);
            const chatMessages = document.getElementById('chat-messages');
            const errorMessage = document.createElement('div');
            errorMessage.className = 'system-message';
            errorMessage.textContent = 'Error loading chat history.';
            chatMessages.appendChild(errorMessage);
        });
}

// Display chat history
function displayChatHistory(history) {
    const chatMessages = document.getElementById('chat-messages');
    
    history.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.role === 'user' ? 'user-message' : 'trader-message'}`;
        messageDiv.textContent = message.content;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = `message-time ${message.role === 'user' ? 'user-time' : 'trader-time'}`;
        timeDiv.textContent = message.timestamp;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.appendChild(timeDiv);
    });
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send a message to the trader
function sendMessage() {
    if (!isConnected) {
        alert('Please connect to a SCOPE ID first');
        return;
    }
    
    const messageInput = document.getElementById('chat-input');
    const message = messageInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Clear input field
    messageInput.value = '';
    
    // Get custom prompt if exists
    const customPrompt = document.getElementById('custom-prompt').value.trim();
    
    // Display user message immediately
    const chatMessages = document.getElementById('chat-messages');
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user-message';
    userMessageDiv.textContent = message;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time user-time';
    const now = new Date();
    const timestamp = now.toLocaleTimeString();
    timeDiv.textContent = timestamp;
    
    chatMessages.appendChild(userMessageDiv);
    chatMessages.appendChild(timeDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Show thinking indicator
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'chat-message trader-message';
    thinkingDiv.textContent = 'Thinking...';
    thinkingDiv.id = 'thinking-indicator';
    chatMessages.appendChild(thinkingDiv);
    
    // Send message to server
    const formData = new FormData();
    formData.append('scope_id', currentScopeId);
    formData.append('message', message);
    if (customPrompt) {
        formData.append('custom_prompt', customPrompt);
    }
    
    fetch('/scope_chat/send', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Remove thinking indicator
        document.getElementById('thinking-indicator').remove();
        
        // Display trader response
        const traderMessageDiv = document.createElement('div');
        traderMessageDiv.className = 'chat-message trader-message';
        traderMessageDiv.textContent = data.response;
        
        const responseTimeDiv = document.createElement('div');
        responseTimeDiv.className = 'message-time trader-time';
        responseTimeDiv.textContent = data.timestamp;
        
        chatMessages.appendChild(traderMessageDiv);
        chatMessages.appendChild(responseTimeDiv);
        
        // Update total stats
        if (data.tokens) {
            document.getElementById('total-input-tokens').textContent = data.tokens.total.input;
            document.getElementById('total-output-tokens').textContent = data.tokens.total.output;
            document.getElementById('total-cost').textContent = `$${(data.tokens.total.cost_cents / 100).toFixed(2)}`;
        }
        
        // If this is a shared trade (symbol was mentioned in chat), show trade details
        if (data.shared_trade && data.trade_details) {
            const tradeDetailsDiv = document.createElement('div');
            tradeDetailsDiv.className = 'shared-trade-details';
            
            // Format the trade details
            const side = data.trade_details.side === '1' ? 'BUY' : 'SELL';
            const symbol = data.trade_details.symbol;
            const quantity = data.trade_details.quantity;
            const price = data.trade_details.price;
            
            tradeDetailsDiv.innerHTML = `
                <div class="trade-details-header">SHARED TRADE DETAILS</div>
                <div class="trade-details-content">
                    <div class="trade-detail"><span>Side:</span> ${side}</div>
                    <div class="trade-detail"><span>Symbol:</span> ${symbol}</div>
                    <div class="trade-detail"><span>Quantity:</span> ${quantity}</div>
                    <div class="trade-detail"><span>Price:</span> ${price}</div>
                </div>
            `;
            
            chatMessages.appendChild(tradeDetailsDiv);
        }
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        console.error('Error sending message:', error);
        // Remove thinking indicator
        document.getElementById('thinking-indicator').remove();
        
        // Display error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'system-message';
        errorDiv.textContent = 'Error sending message. Please try again.';
        chatMessages.appendChild(errorDiv);
    });
}

// Clear chat history
function clearChat() {
    if (!currentScopeId) {
        alert('Please connect to a SCOPE ID first');
        return;
    }
    
    if (confirm('Are you sure you want to clear the chat history?')) {
        const formData = new FormData();
        formData.append('scope_id', currentScopeId);
        
        fetch('/scope_chat/clear', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = '';
            
            const systemMessage = document.createElement('div');
            systemMessage.className = 'system-message';
            systemMessage.textContent = 'Chat history cleared';
            chatMessages.appendChild(systemMessage);
            
            // Reset token stats
            document.getElementById('total-input-tokens').textContent = '0';
            document.getElementById('total-output-tokens').textContent = '0';
            document.getElementById('total-cost').textContent = '$0.00';
        })
        .catch(error => {
            console.error('Error clearing chat:', error);
            alert('Error clearing chat history. Please try again.');
        });
    }
}

// Reset prompt to default
function resetPrompt() {
    // Instead of using DEFAULT_PROMPT, fetch it from the server
    fetchDefaultPrompt();
}

// Initialize ScopeChat when page loads
function initScopeChat() {
    // We'll fetch the default prompt from the server instead of setting it directly
    fetchDefaultPrompt();
    
    // Add event listeners
    document.getElementById('connect-scope').addEventListener('click', connectToScope);
    document.getElementById('clear-chat').addEventListener('click', clearChat);
    document.getElementById('reset-prompt').addEventListener('click', resetPrompt);
    document.getElementById('send-message').addEventListener('click', sendMessage);
    
    // Send message on Enter key
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Allow scope ID connection on Enter key
    document.getElementById('scope-id').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            connectToScope();
        }
    });
    
    // Add event listeners for tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
}

// Update window.onload function to include ScopeChat initialization
window.onload = function() {
    // Your existing code...
    
    // Initial update of the order book and trade ticker
    updateOrderBook();
    updateTradeTicker();
    
    // Set intervals to update the data
    setInterval(updateOrderBook, 1000);
    setInterval(updateTradeTicker, 1000);
    
    // Set up symbol search functionality
    document.getElementById('search-symbol').addEventListener('click', function() {
        updateSymbolList(fullOrderBookData);
    });
    
    // Allow pressing Enter in the search input to search
    document.getElementById('symbol-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            updateSymbolList(fullOrderBookData);
        }
    });
    
    // Initialize ScopeChat
    initScopeChat();
    
    // Initialize minimizable blotters
    initMinimizableBlotters();
    
    // Update scopechat blotters periodically
    updateScopeChatBlotters();
    setInterval(updateScopeChatBlotters, 1000);
    
    // Add event listener for portfolio refresh button
    const refreshPortfolioBtn = document.getElementById('refresh-portfolio');
    if (refreshPortfolioBtn) {
        refreshPortfolioBtn.addEventListener('click', loadPortfolio);
    }
    
    // Add portfolio tab click handler
    const portfolioTab = document.querySelector('[data-tab="portfolio"]');
    if (portfolioTab) {
        portfolioTab.addEventListener('click', function() {
            // Load portfolio data when tab is clicked
            setTimeout(loadPortfolio, 100); // Small delay to ensure tab is active
        });
    }
    
    // Add order entry tab click handler
    const orderEntryTab = document.querySelector('[data-tab="order-entry"]');
    if (orderEntryTab) {
        orderEntryTab.addEventListener('click', function() {
            // Load open positions when order entry tab is clicked
            setTimeout(loadOrderEntryOpenPositions, 100); // Small delay to ensure tab is active
        });
    }
    
    // Load open positions when page loads if order entry tab is active
    if (document.querySelector('[data-tab="order-entry"].active')) {
        setTimeout(loadOrderEntryOpenPositions, 100);
    }
};

// Add a new function to fetch the default prompt from the server
function fetchDefaultPrompt() {
    fetch('/scope_chat/default_prompt')
        .then(response => response.json())
        .then(data => {
            if (data.prompt) {
                document.getElementById('custom-prompt').value = data.prompt;
            }
        })
        .catch(error => {
            console.error('Error fetching default prompt:', error);
            // If we can't fetch the prompt, we'll leave the textarea empty
        });
}

// Context Menu Functionality
let contextMenu = document.getElementById('context-menu');
let tradeAgainstOption = document.getElementById('trade-against');
let closePositionOption = document.getElementById('close-position');

// Hide context menu when clicking anywhere else
document.addEventListener('click', () => {
    contextMenu.style.display = 'none';
});

// Prevent context menu from closing when clicking on it
contextMenu.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Show context menu on right click
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    
    // Check if right-clicked on an order book row
    if (e.target.closest('.order-table tr') && !e.target.closest('th')) {
        const row = e.target.closest('tr');
        if (row.dataset.side && row.dataset.symbol && row.dataset.price && row.dataset.qty) {
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            
            // Store the order details in the context menu for later use
            contextMenu.dataset.side = row.dataset.side;
            contextMenu.dataset.symbol = row.dataset.symbol;
            contextMenu.dataset.price = row.dataset.price;
            contextMenu.dataset.qty = row.dataset.qty;
            
            // Show trade against option
            tradeAgainstOption.style.display = 'block';
            // Hide close position option
            closePositionOption.style.display = 'none';
        }
    }
    
    // Check if right-clicked on a position row
    if (e.target.closest('#open-positions-table tr') && !e.target.closest('th')) {
        const row = e.target.closest('tr');
        if (row.dataset.symbol && row.dataset.quantity) {
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            
            // Store the position details in the context menu for later use
            contextMenu.dataset.symbol = row.dataset.symbol;
            contextMenu.dataset.quantity = row.dataset.quantity;
            contextMenu.dataset.positionType = row.dataset.positionType;
            
            // Hide trade against option
            tradeAgainstOption.style.display = 'none';
            // Show close position option
            closePositionOption.style.display = 'block';
        }
    }
});

// Handle trade against option
tradeAgainstOption.addEventListener('click', () => {
    const side = contextMenu.dataset.side;
    const symbol = contextMenu.dataset.symbol;
    const price = contextMenu.dataset.price;
    const qty = contextMenu.dataset.qty;
    
    // Set opposite side
    document.getElementById('side').value = side === 'BID' ? 'Sell' : 'Buy';
    
    // Set other fields
    document.getElementById('symbol').value = symbol;
    document.getElementById('price').value = price;
    document.getElementById('quantity').value = qty;
    
    // Hide context menu and show modal
    contextMenu.style.display = 'none';
    modal.style.display = 'block';
});

// Handle close position option
closePositionOption.addEventListener('click', () => {
    const symbol = contextMenu.dataset.symbol;
    const quantity = contextMenu.dataset.quantity;
    const positionType = contextMenu.dataset.positionType;
    
    // Set opposite side of the position
    document.getElementById('side').value = positionType === 'Long' ? 'Sell' : 'Buy';
    
    // Set other fields
    document.getElementById('symbol').value = symbol;
    document.getElementById('quantity').value = quantity;
    
    // Get current market price for the symbol
    fetch('/get_market_price', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        if (data.price) {
            document.getElementById('price').value = data.price;
        }
        
        // Hide context menu and show modal
        contextMenu.style.display = 'none';
        modal.style.display = 'block';
    })
    .catch(error => {
        console.error('Error getting market price:', error);
        // Still show the modal even if we couldn't get the price
        contextMenu.style.display = 'none';
        modal.style.display = 'block';
    });
});

// Modal Functionality
const modal = document.getElementById('order-entry-modal');
const openOrderEntryBtn = document.getElementById('open-order-entry');
const floatingOrderEntryBtn = document.getElementById('floating-order-entry');
const closeModalBtn = document.querySelector('.close-modal');

// Open modal when clicking the New Order button
openOrderEntryBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

// Open modal when clicking the floating New Order button
floatingOrderEntryBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

// Close modal when clicking the X button
closeModalBtn.addEventListener('click', () => {
    closeOrderEntry();
});

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        closeOrderEntry();
    }
});

// Function to close the order entry modal
function closeOrderEntry() {
    modal.style.display = 'none';
}

// Global variables
let currentTraderId = 'TRADER1';
let orderBlotter = new Map(); // Map to store order status
let previousOrderStates = new Map(); // Map to store previous order states

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set initial trader ID
    document.getElementById('sender').value = currentTraderId;
    
    // Add event listeners
    document.getElementById('update-trader-id').addEventListener('click', updateTraderId);
    document.getElementById('reset-filter').addEventListener('click', function() {
        document.getElementById('symbol-filter').value = '';
        updateOrderBlotter();
    });
    
    // Add event listener for symbol filter input
    document.getElementById('symbol-filter').addEventListener('input', function() {
        updateOrderBlotter();
    });
    
    // Start polling for updates
    setInterval(updateOrderBlotter, 1000);
    setInterval(updateRecentTrades, 1000);
});

// Update trader ID
function updateTraderId() {
    const newTraderId = document.getElementById('trader-id').value.trim();
    if (newTraderId) {
        currentTraderId = newTraderId;
        document.getElementById('sender').value = currentTraderId;
        updateOrderBlotter(); // Refresh blotter for new trader
    }
}

// Update order blotter
function updateOrderBlotter() {
    fetch('/get_order_book')
        .then(response => response.json())
        .then(data => {
            const blotterBody = document.getElementById('blotter-body');
            blotterBody.innerHTML = ''; // Clear the blotter first
            const currentOrderStates = new Map();
            
            // Get the current filter value
            const filterSymbol = document.getElementById('symbol-filter').value.trim().toUpperCase();
            
            // Process all orders and find those belonging to current trader
            for (const symbol in data) {
                // Skip if filter is active and symbol doesn't match
                if (filterSymbol && !symbol.toUpperCase().includes(filterSymbol)) {
                    continue;
                }
                
                const book = data[symbol];
                
                // Process buy orders
                book.buys.forEach(order => {
                    if (order.sender === currentTraderId) {
                        currentOrderStates.set(order.order_id, {
                            filled: order.original_qty - order.remaining_qty,
                            originalQty: order.original_qty
                        });
                        addOrderToMainBlotter(order, 'Buy', currentOrderStates);
                    }
                });
                
                // Process sell orders
                book.sells.forEach(order => {
                    if (order.sender === currentTraderId) {
                        currentOrderStates.set(order.order_id, {
                            filled: order.original_qty - order.remaining_qty,
                            originalQty: order.original_qty
                        });
                        addOrderToMainBlotter(order, 'Sell', currentOrderStates);
                    }
                });
            }
            
            // Show "No orders" message if blotter is empty
            if (blotterBody.children.length === 0) {
                const noOrdersRow = document.createElement('tr');
                noOrdersRow.innerHTML = `
                    <td colspan="9" class="no-orders-message">
                        ${filterSymbol ? `No orders found for symbol: ${filterSymbol}` : 'No active orders'}
                    </td>
                `;
                blotterBody.appendChild(noOrdersRow);
            }
            
            // Update previous states for next comparison
            previousOrderStates = currentOrderStates;
            
            // Also refresh open positions in the order entry tab
            loadOrderEntryOpenPositions();
        })
        .catch(error => console.error('Error updating order blotter:', error));
}

// Add order to main blotter
function addOrderToMainBlotter(order, side, currentOrderStates) {
    const blotterBody = document.getElementById('blotter-body');
    const row = document.createElement('tr');
    
    // Calculate filled and remaining quantities
    const filled = order.original_qty - order.remaining_qty;
    const status = getOrderStatus(filled, order.original_qty);
    
    // Check if this is a new order or if the status has changed
    const previousState = previousOrderStates.get(order.order_id);
    const currentState = currentOrderStates.get(order.order_id);
    
    // Only add animation class if there's a change in status
    if (!previousState) {
        // New order
        row.classList.add('new-order');
    } else if (previousState.filled !== currentState.filled) {
        // Status changed
        if (filled === order.original_qty) {
            row.classList.add('full-fill');
        } else if (filled > 0) {
            row.classList.add('partial-fill');
        }
    }
    
    row.innerHTML = `
        <td>${order.time || ''}</td>
        <td>${order.order_id}</td>
        <td>${order.symbol}</td>
        <td>${side}</td>
        <td>${order.price}</td>
        <td>${order.original_qty}</td>
        <td>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${(filled / order.original_qty) * 100}%"></div>
                <div class="progress-text">${filled}/${order.original_qty}</div>
            </div>
        </td>
        <td class="status-${status.toLowerCase()}">${status}</td>
    `;
    
    blotterBody.appendChild(row);
}

// Get order status
function getOrderStatus(filled, originalQty) {
    if (filled === 0) return 'NEW';
    if (filled === originalQty) return 'FILLED';
    return 'PARTIAL';
}

// Update recent trades
function updateRecentTrades() {
    fetch('/get_recent_trades')
        .then(response => response.json())
        .then(trades => {
            const tradeTicker = document.getElementById('trade-ticker');
            
            if (trades.length === 0) {
                tradeTicker.innerHTML = '<div class="no-trades-message">No recent trades</div>';
                return;
            }
            
            tradeTicker.innerHTML = '';
            trades.forEach(trade => {
                const tradeItem = document.createElement('div');
                tradeItem.className = `trade-item ${trade.side.toLowerCase()}`;
                
                tradeItem.innerHTML = `
                    <div class="trade-time">${trade.time}</div>
                    <div class="trade-details">
                        ${trade.symbol} ${trade.quantity} @ ${trade.price}
                        (${trade.buyer} ↔ ${trade.seller})
                    </div>
                `;
                
                tradeTicker.appendChild(tradeItem);
            });
        })
        .catch(error => console.error('Error updating recent trades:', error));
}

// Initialize minimizable blotters
function initMinimizableBlotters() {
    const minimizeButtons = document.querySelectorAll('.minimize-button');
    const blotterContents = document.querySelectorAll('.blotter-content');
    
    minimizeButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            blotterContents[index].classList.toggle('minimized');
            button.textContent = blotterContents[index].classList.contains('minimized') ? '+' : '−';
        });
    });
}

// Update both scopechat blotters
function updateScopeChatBlotters() {
    fetch('/get_order_book')
        .then(response => response.json())
        .then(data => {
            const traderBlotterBody = document.getElementById('trader-blotter-body');
            const scopeBlotterBody = document.getElementById('scope-blotter-body');
            
            // Clear both blotters
            traderBlotterBody.innerHTML = '';
            scopeBlotterBody.innerHTML = '';
            
            // Get current trader ID and scope ID
            const currentTraderId = document.getElementById('trader-id').value;
            const currentScopeId = document.getElementById('scope-id').value;
            
            // Process all orders
            for (const symbol in data) {
                const book = data[symbol];
                
                // Process buy orders
                book.buys.forEach(order => {
                    if (order.sender === currentTraderId) {
                        addOrderToScopeBlotter(order, 'Buy', traderBlotterBody);
                    } else if (order.sender === currentScopeId) {
                        addOrderToScopeBlotter(order, 'Buy', scopeBlotterBody);
                    }
                });
                
                // Process sell orders
                book.sells.forEach(order => {
                    if (order.sender === currentTraderId) {
                        addOrderToScopeBlotter(order, 'Sell', traderBlotterBody);
                    } else if (order.sender === currentScopeId) {
                        addOrderToScopeBlotter(order, 'Sell', scopeBlotterBody);
                    }
                });
            }
            
            // Show "No orders" message if blotters are empty
            if (traderBlotterBody.children.length === 0) {
                traderBlotterBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="no-orders-message">No active orders for ${currentTraderId}</td>
                    </tr>
                `;
            }
            
            if (scopeBlotterBody.children.length === 0) {
                scopeBlotterBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="no-orders-message">No active orders for ${currentScopeId || 'connected scope'}</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error updating scopechat blotters:', error);
        });
}

// Helper function to add an order to a scopechat blotter
function addOrderToScopeBlotter(order, side, blotterBody) {
    const row = document.createElement('tr');
    
    // Calculate fill progress
    const fillProgress = ((order.original_qty - order.remaining_qty) / order.original_qty) * 100;
    const status = getOrderStatus(fillProgress, order.original_qty);
    
    row.innerHTML = `
        <td>${order.time}</td>
        <td>${order.order_id}</td>
        <td>${order.symbol}</td>
        <td>${side}</td>
        <td>${formatPrice(order.price)}</td>
        <td>${formatQuantity(order.remaining_qty)}</td>
        <td>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${fillProgress}%"></div>
                <div class="progress-text">${fillProgress.toFixed(0)}%</div>
            </div>
        </td>
        <td class="status-${status.toLowerCase()}">${status}</td>
    `;
    
    blotterBody.appendChild(row);
}

// Profile functionality
function updateProfileDisplay(scopeId) {
    fetch(`/api/profile/${encodeURIComponent(scopeId)}`)
        .then(response => response.json())
        .then(profile => {
            const profileDisplay = document.getElementById('profile-display');
            if (profile && Object.keys(profile).length > 0) {
                profileDisplay.style.display = 'block';
                document.getElementById('profile-picture').src = profile.picture_url || '';
                document.getElementById('profile-name').textContent = profile.name || scopeId;
                document.getElementById('profile-title').textContent = profile.title || 'No title';
                document.getElementById('profile-department').textContent = profile.department || 'No department';
                
                // Create a comprehensive prompt that includes name, title, department, and bio
                let customPrompt = 'You are roleplaying as: ';
                if (profile.name) customPrompt += `${profile.name}\n`;
                if (profile.title) customPrompt += `Title: ${profile.title}\n`;
                if (profile.department) customPrompt += `Department: ${profile.department}\n`;
                if (profile.bio) customPrompt += `\nBio:\n${profile.bio}`;
                
                if (customPrompt) {
                    document.getElementById('custom-prompt').value = customPrompt;
                }
            } else {
                profileDisplay.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching profile:', error);
            document.getElementById('profile-display').style.display = 'none';
        });
}

// Add event listener for view profile button
document.getElementById('view-profile').addEventListener('click', function() {
    const scopeId = document.getElementById('scope-id').value.trim();
    if (scopeId) {
        window.location.href = `/profile/${encodeURIComponent(scopeId)}`;
    } else {
        alert('Please enter a SCOPE ID first');
    }
});

function displayChatMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : ''}`;
    
    const profilePicture = isUser ? 
        document.getElementById('profile-picture')?.src || '' : 
        '{{ url_for("static", filename="images/ai-avatar.png") }}';
    
    messageDiv.innerHTML = `
        <img src="${profilePicture}" alt="Avatar" class="message-avatar">
        <div class="message-content">
            <p class="message-text">${message}</p>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Random trade generator functionality
let randomTradeInterval = null;

// Load random trade settings when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadRandomTradeSettings();
});

function loadRandomTradeSettings() {
    fetch('/get_random_trade_settings')
        .then(response => response.json())
        .then(data => {
            document.getElementById('random-trades-toggle').checked = data.enabled;
            document.getElementById('interval-seconds').value = data.interval_seconds;
            document.getElementById('orders-per-interval').value = data.orders_per_interval;
            document.getElementById('max-orders-before-refresh').value = data.max_orders_before_refresh;
            
            // If enabled, start the interval
            if (data.enabled) {
                startRandomTradeGenerator(data.interval_seconds, data.orders_per_interval);
            }
        })
        .catch(error => console.error('Error loading random trade settings:', error));
}

function saveRandomTradeSettings() {
    const settings = {
        enabled: document.getElementById('random-trades-toggle').checked,
        interval_seconds: parseInt(document.getElementById('interval-seconds').value),
        orders_per_interval: parseInt(document.getElementById('orders-per-interval').value),
        max_orders_before_refresh: parseInt(document.getElementById('max-orders-before-refresh').value)
    };
    
    fetch('/update_random_trade_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        // Update the interval if enabled
        if (settings.enabled) {
            startRandomTradeGenerator(settings.interval_seconds, settings.orders_per_interval);
        } else {
            stopRandomTradeGenerator();
        }
        
        // Show success message
        updateStatus('Random trade settings saved');
    })
    .catch(error => {
        console.error('Error saving random trade settings:', error);
        updateStatus('Error saving settings');
    });
}

function startRandomTradeGenerator(intervalSeconds, ordersPerInterval) {
    // Clear any existing interval
    stopRandomTradeGenerator();
    
    // Start a new interval
    randomTradeInterval = setInterval(() => {
        // Generate the specified number of orders
        for (let i = 0; i < ordersPerInterval; i++) {
            generateRandomTrade();
        }
    }, intervalSeconds * 1000);
    
    updateStatus('Random trade generator started');
}

function stopRandomTradeGenerator() {
    if (randomTradeInterval) {
        clearInterval(randomTradeInterval);
        randomTradeInterval = null;
        updateStatus('Random trade generator stopped');
    }
}

function generateRandomTrade() {
    fetch('/generate_random_trade', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Update the output box
        const outputBox = document.getElementById('output-box');
        outputBox.innerHTML += '<br>' + data.output;
        outputBox.scrollTop = outputBox.scrollHeight;
        
        // Update the status
        updateStatus(data.status);
        
        // Update the order book and recent trades
        updateOrderBook();
        updateRecentTrades();
    })
    .catch(error => {
        console.error('Error generating random trade:', error);
        updateStatus('Error generating random trade');
    });
}

// Add event listeners for the random trade controls
document.getElementById('random-trades-toggle').addEventListener('change', function() {
    // This will be handled when settings are saved
});

document.getElementById('save-random-trade-settings').addEventListener('click', saveRandomTradeSettings);

// Market price functionality
document.getElementById('get-market-price').addEventListener('click', async function() {
    const symbolInput = document.getElementById('symbol');
    const priceInput = document.getElementById('price');
    const button = this;
    
    if (!symbolInput.value) {
        alert('Please enter a symbol first');
        return;
    }
    
    // Disable button while fetching
    button.disabled = true;
    button.textContent = 'Loading...';
    
    try {
        const response = await fetch('/get_market_price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbolInput.value
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch market price');
        }
        
        const data = await response.json();
        if (data.price) {
            priceInput.value = data.price;
        } else {
            alert('Unable to fetch market price for ' + symbolInput.value);
        }
    } catch (error) {
        console.error('Error fetching market price:', error);
        alert('Error fetching market price. Please try again.');
    } finally {
        // Re-enable button
        button.disabled = false;
        button.textContent = 'Get Market Price';
    }
});

// Portfolio Functions
function loadPortfolio() {
    const traderId = document.getElementById('trader-id').value;
    if (!traderId) {
        updateStatus('Error: Trader ID is required');
        return;
    }
    
    updateStatus('Loading portfolio...');
    
    // First check if baripool is accessible
    fetch('/test_baripool')
        .then(response => {
            if (!response.ok) {
                throw new Error('baripool module not accessible');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            console.log('baripool test successful:', data);
            
            // Now try to load the portfolio
            return fetch(`/get_portfolio?trader_id=${traderId}`);
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updatePortfolioUI(data);
            updateStatus('Portfolio loaded successfully');
        })
        .catch(error => {
            console.error('Error loading portfolio:', error);
            updateStatus('Error loading portfolio: ' + error.message);
            
            // Display empty portfolio UI
            updatePortfolioUI({
                open_positions: [],
                filled_trades: [],
                total_realized_pnl: 0,
                total_unrealized_pnl: 0,
                total_pnl: 0
            });
        });
}

// Add the missing updateStatus function
function updateStatus(message) {
    const statusDisplay = document.getElementById('status-display');
    if (statusDisplay) {
        statusDisplay.textContent = message;
    } else {
        console.log('Status:', message);
    }
}

function updatePortfolioUI(data) {
    // Update summary values
    document.getElementById('total-pnl').textContent = formatCurrency(data.total_pnl);
    document.getElementById('realized-pnl').textContent = formatCurrency(data.total_realized_pnl);
    document.getElementById('unrealized-pnl').textContent = formatCurrency(data.total_unrealized_pnl);
    document.getElementById('open-positions-count').textContent = data.open_positions.length;
    
    // Update open positions table
    const openPositionsBody = document.getElementById('open-positions-body');
    openPositionsBody.innerHTML = '';
    
    if (data.open_positions.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="8" class="no-data-message">No open positions</td>';
        openPositionsBody.appendChild(emptyRow);
    } else {
        data.open_positions.forEach(position => {
            const row = document.createElement('tr');
            
            // Determine position type and styling
            const positionType = position.quantity > 0 ? 'Long' : 'Short';
            const positionClass = position.quantity > 0 ? 'position-long' : 'position-short';
            
            // Calculate market value
            const marketValue = Math.abs(position.quantity) * position.current_price;
            
            // Calculate PnL percentage
            const pnlPercentage = position.quantity > 0 
                ? ((position.current_price - position.avg_price) / position.avg_price) * 100
                : ((position.avg_price - position.current_price) / position.avg_price) * 100;
            
            // Determine PnL styling
            const pnlClass = position.unrealized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
            
            // Add data attributes for context menu
            row.dataset.symbol = position.symbol;
            row.dataset.quantity = Math.abs(position.quantity);
            row.dataset.positionType = positionType;
            
            row.innerHTML = `
                <td>${position.symbol}</td>
                <td class="${positionClass}">${positionType}</td>
                <td>${Math.abs(position.quantity)}</td>
                <td>${formatCurrency(position.avg_price)}</td>
                <td>${formatCurrency(position.current_price)}</td>
                <td>${formatCurrency(marketValue)}</td>
                <td class="${pnlClass}">${formatCurrency(position.unrealized_pnl)}</td>
                <td class="${pnlClass}">${formatNumber(pnlPercentage)}%</td>
            `;
            
            // Add right-click event listener for context menu
            row.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                
                // Show context menu
                const contextMenu = document.getElementById('context-menu');
                contextMenu.style.display = 'block';
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.style.top = `${e.pageY}px`;
                
                // Store position details in context menu for later use
                contextMenu.dataset.symbol = position.symbol;
                contextMenu.dataset.quantity = Math.abs(position.quantity);
                contextMenu.dataset.positionType = positionType;
                
                // Show close position option and hide trade against option
                document.getElementById('close-position').style.display = 'block';
                document.getElementById('trade-against').style.display = 'none';
            });
            
            openPositionsBody.appendChild(row);
        });
    }
    
    // Update filled trades table
    const filledTradesBody = document.getElementById('filled-trades-body');
    filledTradesBody.innerHTML = '';
    
    if (data.filled_trades.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="7" class="no-data-message">No filled trades</td>';
        filledTradesBody.appendChild(emptyRow);
    } else {
        data.filled_trades.forEach(trade => {
            const row = document.createElement('tr');
            
            // Determine side styling
            const sideClass = trade.side === '1' ? 'position-long' : 'position-short';
            const sideText = trade.side === '1' ? 'Buy' : 'Sell';
            
            row.innerHTML = `
                <td>${trade.time}</td>
                <td>${trade.order_id}</td>
                <td>${trade.symbol}</td>
                <td class="${sideClass}">${sideText}</td>
                <td>${trade.quantity}</td>
                <td>${formatCurrency(trade.price)}</td>
                <td>${trade.status}</td>
            `;
            
            filledTradesBody.appendChild(row);
        });
    }
}

function formatCurrency(value) {
    return '$' + parseFloat(value).toFixed(2);
}

function formatNumber(value) {
    return parseFloat(value).toFixed(2);
}

// Function to load open positions for the order entry tab
function loadOrderEntryOpenPositions() {
    const traderId = document.getElementById('trader-id').value;
    if (!traderId) {
        updateStatus('Error: Trader ID is required');
        return;
    }
    
    updateStatus('Loading open positions...');
    
    // First check if baripool is accessible
    fetch('/test_baripool')
        .then(response => {
            if (!response.ok) {
                throw new Error('baripool module not accessible');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            
            // Now try to load the portfolio
            return fetch(`/get_portfolio?trader_id=${traderId}`);
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateOrderEntryOpenPositionsUI(data);
            updateStatus('Open positions loaded successfully');
        })
        .catch(error => {
            console.error('Error loading open positions:', error);
            updateStatus('Error loading open positions: ' + error.message);
            
            // Display empty open positions UI
            updateOrderEntryOpenPositionsUI({
                open_positions: [],
                total_unrealized_pnl: 0
            });
        });
}

// Function to update the open positions UI in the order entry tab
function updateOrderEntryOpenPositionsUI(data) {
    // Update open positions count
    document.getElementById('open-positions-count').textContent = data.open_positions.length;
    
    // Update open positions table
    const openPositionsBody = document.getElementById('order-entry-open-positions-body');
    openPositionsBody.innerHTML = '';
    
    if (data.open_positions.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="8" class="no-data-message">No open positions</td>';
        openPositionsBody.appendChild(emptyRow);
    } else {
        data.open_positions.forEach(position => {
            const row = document.createElement('tr');
            
            // Determine position type and styling
            const positionType = position.quantity > 0 ? 'Long' : 'Short';
            const positionClass = position.quantity > 0 ? 'position-long' : 'position-short';
            
            // Calculate market value
            const marketValue = Math.abs(position.quantity) * position.current_price;
            
            // Calculate PnL percentage
            const pnlPercentage = position.quantity > 0 
                ? ((position.current_price - position.avg_price) / position.avg_price) * 100
                : ((position.avg_price - position.current_price) / position.avg_price) * 100;
            
            // Determine PnL styling
            const pnlClass = position.unrealized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
            
            // Add data attributes for context menu
            row.dataset.symbol = position.symbol;
            row.dataset.quantity = Math.abs(position.quantity);
            row.dataset.positionType = positionType;
            
            row.innerHTML = `
                <td>${position.symbol}</td>
                <td class="${positionClass}">${positionType}</td>
                <td>${Math.abs(position.quantity)}</td>
                <td>${formatCurrency(position.avg_price)}</td>
                <td>${formatCurrency(position.current_price)}</td>
                <td>${formatCurrency(marketValue)}</td>
                <td class="${pnlClass}">${formatCurrency(position.unrealized_pnl)}</td>
                <td class="${pnlClass}">${formatNumber(pnlPercentage)}%</td>
            `;
            
            // Add right-click event listener for context menu
            row.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                
                // Show context menu
                const contextMenu = document.getElementById('context-menu');
                contextMenu.style.display = 'block';
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.style.top = `${e.pageY}px`;
                
                // Store position details in context menu for later use
                contextMenu.dataset.symbol = position.symbol;
                contextMenu.dataset.quantity = Math.abs(position.quantity);
                contextMenu.dataset.positionType = positionType;
                
                // Show close position option and hide trade against option
                document.getElementById('close-position').style.display = 'block';
                document.getElementById('trade-against').style.display = 'none';
            });
            
            openPositionsBody.appendChild(row);
        });
    }
}

// Add event listener for close position option in context menu
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Add event listener for close position option
    const closePositionOption = document.getElementById('close-position');
    if (closePositionOption) {
        closePositionOption.addEventListener('click', function() {
            const contextMenu = document.getElementById('context-menu');
            const symbol = contextMenu.dataset.symbol;
            const quantity = contextMenu.dataset.quantity;
            const positionType = contextMenu.dataset.positionType;
            
            // Hide context menu
            contextMenu.style.display = 'none';
            
            // Open order entry modal
            const modal = document.getElementById('order-entry-modal');
            modal.style.display = 'block';
            
            // Set form values for closing position
            document.getElementById('side').value = positionType === 'Long' ? 'Sell' : 'Buy';
            document.getElementById('symbol').value = symbol;
            document.getElementById('quantity').value = quantity;
            
            // Get current market price for the symbol
            fetch('/get_market_price', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol: symbol })
            })
            .then(response => response.json())
            .then(data => {
                if (data.price) {
                    document.getElementById('price').value = data.price;
                }
            })
            .catch(error => {
                console.error('Error getting market price:', error);
            });
        });
    }
    
    // Add event listener for cancel order option
    const cancelOrderOption = document.getElementById('cancel-order');
    if (cancelOrderOption) {
        cancelOrderOption.addEventListener('click', function() {
            const contextMenu = document.getElementById('context-menu');
            const orderId = contextMenu.dataset.orderId;
            const symbol = contextMenu.dataset.symbol;
            
            // Hide context menu
            contextMenu.style.display = 'none';
            
            // Confirm cancellation
            if (confirm(`Are you sure you want to cancel order ${orderId} for ${symbol}?`)) {
                // Send cancel order request
                fetch('/cancel_order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ order_id: orderId })
                })
                .then(response => response.json())
                .then(data => {
                    // Update output box with cancellation message
                    const outputBox = document.getElementById('output-box');
                    outputBox.innerHTML += '\n' + data.output;
                    // Auto-scroll to the bottom
                    outputBox.scrollTop = outputBox.scrollHeight;
                    
                    // Update status and reset after delay
                    document.getElementById('status-display').textContent = data.status;
                    setTimeout(() => {
                        document.getElementById('status-display').textContent = 'READY';
                    }, 2000);
                    
                    // Refresh the order book to show the cancellation
                    updateOrderBook();
                })
                .catch(error => {
                    console.error('Error canceling order:', error);
                    updateStatus('Error canceling order: ' + error.message);
                });
            }
        });
    }
    
    // Hide context menu when clicking elsewhere
    document.addEventListener('click', function() {
        const contextMenu = document.getElementById('context-menu');
        if (contextMenu) {
            contextMenu.style.display = 'none';
        }
    });
});