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
            
            // Add data attributes for context menu
            row.dataset.side = sideLabel;
            row.dataset.symbol = symbol;
            row.dataset.price = order.price;
            row.dataset.qty = order.remaining_qty;
            
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
    
    // Initialize ScopeChat
    initScopeChat();
    
    // Initialize minimizable blotters
    initMinimizableBlotters();
    
    // Update scopechat blotters periodically
    updateScopeChatBlotters();
    setInterval(updateScopeChatBlotters, 1000);
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
    
    // Only show context menu for order book rows
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

// Random trade generator
let randomTradeInterval = null;

function startRandomTrades() {
    if (randomTradeInterval) return;
    
    randomTradeInterval = setInterval(() => {
        fetch('/generate_random_trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update the output box
            const outputBox = document.getElementById('output-box');
            outputBox.innerHTML += `<br>${data.output}`;
            outputBox.scrollTop = outputBox.scrollHeight;
            
            // Update the status display
            document.getElementById('status-display').textContent = data.status;
            
            // Refresh the order book and recent trades
            updateOrderBook();
            updateRecentTrades();
        })
        .catch(error => {
            console.error('Error generating random trade:', error);
            document.getElementById('status-display').textContent = 'ERROR';
        });
    }, 15000); // 15 seconds
}

function stopRandomTrades() {
    if (randomTradeInterval) {
        clearInterval(randomTradeInterval);
        randomTradeInterval = null;
    }
}

// Add event listener for the random trades toggle
document.addEventListener('DOMContentLoaded', () => {
    const randomTradesToggle = document.getElementById('random-trades-toggle');
    if (randomTradesToggle) {
        randomTradesToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                startRandomTrades();
            } else {
                stopRandomTrades();
            }
        });
    }
});