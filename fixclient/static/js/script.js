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
function createOrderTable(orders, sideLabel) {
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

// Function to fetch and update the order book
function updateOrderBook() {
    fetch('/get_order_book')
        .then(response => response.json())
        .then(data => {
            // Store the full data
            fullOrderBookData = data;
            
            // Display filtered data
            displayOrderBook(data);
        })
        .catch(error => {
            console.error('Error fetching order book:', error);
            document.getElementById('order-book-container').innerHTML = 
                '<div class="error-message">Error loading order book data</div>';
        });
}

// Function to display order book with optional filtering
function displayOrderBook(data) {
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
        
        // Buy side (bids)
        const buyTable = createOrderTable(bookData.buys, 'BID');
        buyTable.className = 'order-table buy-table';
        
        // Sell side (asks)
        const sellTable = createOrderTable(bookData.sells, 'ASK');
        sellTable.className = 'order-table sell-table';
        
        // Add tables to book display
        bookDisplay.appendChild(buyTable);
        bookDisplay.appendChild(sellTable);
        symbolSection.appendChild(bookDisplay);
        
        // Add the symbol section to the container
        container.appendChild(symbolSection);
    }
}

// Add this to your existing window.onload function
window.onload = function() {
    // Your existing code...
    
    // Initial update of the order book
    updateOrderBook();
    
    // Set interval to update the order book (every 5 seconds)
    setInterval(updateOrderBook, 5000);
    
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