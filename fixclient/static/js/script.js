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