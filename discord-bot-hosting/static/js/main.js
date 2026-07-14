// Main JavaScript for Discord Bot Hosting

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm dangerous actions
    var dangerForms = document.querySelectorAll('form[data-confirm]');
    dangerForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var message = form.getAttribute('data-confirm') || 'هل أنت متأكد؟';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // File upload preview
    var fileInput = document.getElementById('zip_file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                var fileName = file.name;
                var fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                // Show file info
                var fileInfo = document.getElementById('fileInfo');
                if (fileInfo) {
                    fileInfo.innerHTML = '<i class="fas fa-file-archive"></i> ' + fileName + ' (' + fileSize + ' MB)';
                    fileInfo.style.display = 'block';
                }
                
                // Validate file type
                if (!fileName.endsWith('.zip')) {
                    alert('يجب أن يكون الملف بصيغة ZIP');
                    fileInput.value = '';
                }
                
                // Validate file size (50MB max)
                if (file.size > 50 * 1024 * 1024) {
                    alert('حجم الملف يجب أن يكون أقل من 50 ميجابايت');
                    fileInput.value = '';
                }
            }
        });
    }
    
    // Password visibility toggle
    var passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            var passwordInput = this.previousElementSibling;
            var type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });
});

// Function to refresh logs
function refreshLogs() {
    location.reload();
}

// Function to copy log content
function copyLogs() {
    var logContainer = document.getElementById('logContainer');
    if (logContainer) {
        var text = logContainer.innerText;
        navigator.clipboard.writeText(text).then(function() {
            alert('تم نسخ السجلات');
        });
    }
}

// Function to download logs
function downloadLogs() {
    var logContainer = document.getElementById('logContainer');
    if (logContainer) {
        var text = logContainer.innerText;
        var blob = new Blob([text], { type: 'text/plain' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'bot_logs.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
}

// Function to search in logs
function searchLogs(query) {
    var logContainer = document.getElementById('logContainer');
    if (logContainer && query) {
        var lines = logContainer.querySelectorAll('.log-line');
        lines.forEach(function(line) {
            if (line.textContent.toLowerCase().includes(query.toLowerCase())) {
                line.style.backgroundColor = 'rgba(88, 101, 242, 0.2)';
            } else {
                line.style.backgroundColor = 'transparent';
            }
        });
    }
}

// Real-time log updates (WebSocket would be better, but polling for simplicity)
var logUpdateInterval;
function startLogUpdates(botId) {
    logUpdateInterval = setInterval(function() {
        fetch('/api/bot/' + botId + '/logs')
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.logs) {
                    var logContainer = document.getElementById('logContainer');
                    if (logContainer) {
                        logContainer.innerHTML = data.logs.map(function(line) {
                            return '<div class="log-line">' + escapeHtml(line) + '</div>';
                        }).join('');
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                }
            });
    }, 5000);
}

function stopLogUpdates() {
    if (logUpdateInterval) {
        clearInterval(logUpdateInterval);
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}
