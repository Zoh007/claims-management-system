// Custom JavaScript for Claims Management System with robustness features

// Global variables for burger-themed functionality
const BURGER_CONFIG = {
    theme: 'burger',
    version: '1.0.0',
    robustness: true
};

// Initialize Alpine.js components
document.addEventListener('alpine:init', () => {
    Alpine.data('claimsManager', () => ({
        searchQuery: '',
        selectedStatus: '',
        selectedInsurer: '',
        isLoading: false,
        
        // Search functionality with robustness
        performSearch() {
            this.isLoading = true;
            const params = new URLSearchParams();
            
            if (this.searchQuery) params.append('search', this.searchQuery);
            if (this.selectedStatus) params.append('status', this.selectedStatus);
            if (this.selectedInsurer) params.append('insurer', this.selectedInsurer);
            
            window.location.href = `/?${params.toString()}`;
        },
        
        // Reset filters
        resetFilters() {
            this.searchQuery = '';
            this.selectedStatus = '';
            this.selectedInsurer = '';
            window.location.href = '/';
        }
    }));
});

// HTMX event handlers for robustness
document.addEventListener('htmx:beforeRequest', (event) => {
    // Show loading spinner
    const target = event.target;
    if (target.classList.contains('lazypaste-loading')) {
        target.innerHTML = '<div class="spinner"></div>';
    }
});

document.addEventListener('htmx:afterRequest', (event) => {
    // Hide loading spinner and show success message
    const target = event.target;
    if (target.classList.contains('lazypaste-loading')) {
        if (event.detail.successful) {
            showToast('Operation completed successfully!', 'success');
        } else {
            showToast('An error occurred. Please try again.', 'error');
        }
    }
});

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Flag claim functionality
function flagClaim(claimId) {
    const reason = prompt('Enter reason for flagging this claim:');
    if (!reason) return;
    
    fetch(`/claim/${claimId}/flag`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            reason: reason,
            user_id: 'admin'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Claim flagged successfully!', 'success');
            // Refresh the page to show updated flag
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to flag claim. Please try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while flagging the claim.', 'error');
    });
}

// Add note functionality
function addNote(claimId) {
    const content = document.getElementById('note-content').value;
    if (!content.trim()) {
        showToast('Please enter a note before submitting.', 'warning');
        return;
    }
    
    fetch(`/claim/${claimId}/note`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            user_id: 'admin'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Note added successfully!', 'success');
            // Refresh the page to show the new note
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to add note. Please try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while adding the note.', 'error');
    });
}

// Modal functionality
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('modal-enter');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('modal-enter');
    }
}

// Close modal when clicking outside
document.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal-backdrop')) {
        event.target.classList.add('hidden');
    }
});

// Keyboard shortcuts for robustness
document.addEventListener('keydown', (event) => {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        document.getElementById('search').focus();
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal:not(.hidden)');
        modals.forEach(modal => modal.classList.add('hidden'));
    }
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('border-red-500');
            isValid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Export functionality
function exportData() {
    fetch('/api/claims')
        .then(response => response.json())
        .then(data => {
            const csv = convertToCSV(data);
            downloadCSV(csv, 'claims_export.csv');
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            showToast('Failed to export data. Please try again.', 'error');
        });
}

// Convert data to CSV format
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return `"${value}"`;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Download CSV file
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Claims Management System initialized with robustness features');
    
    // Add burger-themed console message
    if (BURGER_CONFIG.robustness) {
        console.log('🍔 Burger mode activated for enhanced robustness!');
    }
    
    // Initialize tooltips and other UI components
    initializeUI();
});

// Initialize UI components
function initializeUI() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            if (button.classList.contains('lazypaste-loading')) {
                button.disabled = true;
                button.innerHTML = '<div class="spinner"></div>';
            }
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.lazypaste-stat, .lazypaste-info, .lazypaste-details');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
}
