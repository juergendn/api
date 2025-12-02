// Konfiguration
let config = {
    terminal_ip: '127.0.0.1',
    terminal_port: 11111
};

// Event Source für Live-Updates
let eventSource = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
    connectEventSource();
    setupAgeCheckbox();
});

// Altersverifikation Checkbox Handler
function setupAgeCheckbox() {
    const ageCheck = document.getElementById('age-check');
    const ageInput = document.getElementById('custom-age');
    
    ageCheck.addEventListener('change', function() {
        ageInput.disabled = !this.checked;
    });
}

// Konfiguration laden
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        config = await response.json();
        document.getElementById('terminal-ip').value = config.terminal_ip;
        document.getElementById('terminal-port').value = config.terminal_port;
    } catch (error) {
        console.error('Fehler beim Laden der Konfiguration:', error);
    }
}

// Konfiguration speichern
async function saveConfig() {
    const terminal_ip = document.getElementById('terminal-ip').value;
    const terminal_port = document.getElementById('terminal-port').value;
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                terminal_ip: terminal_ip,
                terminal_port: parseInt(terminal_port)
            })
        });
        
        const result = await response.json();
        config = result.config;
        
        showStatus('config-status', 'Konfiguration gespeichert!', 'success');
        addLog('info', `Terminal konfiguriert: ${config.terminal_ip}:${config.terminal_port}`);
    } catch (error) {
        showStatus('config-status', 'Fehler beim Speichern!', 'error');
        console.error('Fehler:', error);
    }
}

// Test durchführen
async function runTest(amount, minAge = null) {
    clearLog();
    addLog('info', `Starte Test: ${amount/100} EUR${minAge ? ' mit Altersverifikation ' + minAge + '+' : ''}`);
    
    try {
        const payload = {
            amount: amount
        };
        
        if (minAge) {
            payload.min_age = minAge;
        }
        
        const response = await fetch('/api/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.status === 'started') {
            addLog('info', 'Test wurde gestartet...');
        }
    } catch (error) {
        addLog('error', `Fehler beim Starten des Tests: ${error}`);
    }
}

// Benutzerdefinierter Test
function runCustomTest() {
    const amount = parseInt(document.getElementById('custom-amount').value);
    const ageCheck = document.getElementById('age-check').checked;
    const minAge = ageCheck ? parseInt(document.getElementById('custom-age').value) : null;
    
    if (!amount || amount <= 0) {
        addLog('error', 'Bitte einen gültigen Betrag eingeben!');
        return;
    }
    
    if (ageCheck && (!minAge || minAge < 0)) {
        addLog('error', 'Bitte ein gültiges Mindestalter eingeben!');
        return;
    }
    
    runTest(amount, minAge);
}

// Event Source für Live-Updates
function connectEventSource() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/api/stream');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        addLog(data.type, data.message, data.timestamp);
    };
    
    eventSource.onerror = function(error) {
        console.error('EventSource Fehler:', error);
        // Automatisch wieder verbinden nach 5 Sekunden
        setTimeout(connectEventSource, 5000);
    };
}

// Log-Eintrag hinzufügen
function addLog(type, message, timestamp = null) {
    const logContainer = document.getElementById('log');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    
    const time = timestamp ? new Date(timestamp).toLocaleTimeString('de-DE') : new Date().toLocaleTimeString('de-DE');
    
    const icon = {
        'info': 'ℹ️',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
    }[type] || '•';
    
    entry.innerHTML = `<span class="log-time">[${time}]</span> ${icon} ${message}`;
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Log leeren
function clearLog() {
    const logContainer = document.getElementById('log');
    logContainer.innerHTML = '';
}

// Status-Nachricht anzeigen
function showStatus(elementId, message, type) {
    const statusElement = document.getElementById(elementId);
    statusElement.textContent = message;
    statusElement.className = `status-message ${type} show`;
    
    setTimeout(() => {
        statusElement.classList.remove('show');
    }, 3000);
}

// Betrag formatieren
function formatAmount(cents) {
    return (cents / 100).toFixed(2) + ' EUR';
}
