// Main JavaScript file for the Flask application

document.addEventListener('DOMContentLoaded', function() {
    console.log('Flask application loaded successfully');
    
    // Initialize tooltips and popovers if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading state utility function
    window.showLoading = function(element) {
        if (element) {
            const originalText = element.innerHTML;
            element.innerHTML = '<span class="spinner me-2"></span>Loading...';
            element.disabled = true;
            
            return function hideLoading() {
                element.innerHTML = originalText;
                element.disabled = false;
            };
        }
    };
    
    // Form validation helper
    window.validateForm = function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        });
        
        return isValid;
    };
    
    // Generic AJAX helper function
    window.makeRequest = async function(url, options = {}) {
        try {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            const config = { ...defaultOptions, ...options };
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    };
    
    // Add click handlers for dynamic content
    document.addEventListener('click', function(e) {
        // Handle dynamic button clicks
        if (e.target.matches('.btn-loading')) {
            const hideLoading = showLoading(e.target);
            
            // Simulate async operation
            setTimeout(() => {
                hideLoading();
            }, 2000);
        }
    });
    
    // Health check function to verify backend connectivity
    async function performHealthCheck() {
        try {
            const result = await makeRequest('/health');
            console.log('Health check passed:', result);
        } catch (error) {
            console.warn('Health check failed:', error);
        }
    }
    
    // Perform initial health check
    performHealthCheck();
});

// Utility functions available globally
window.utils = {
    // Format date strings
    formatDate: function(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return new Date(dateString).toLocaleDateString('en-US', options);
    },
    
    // Debounce function for search inputs
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    // Show toast notifications (if using Bootstrap toasts)
    showToast: function(message, type = 'info') {
        // This would require a toast container in the HTML
        console.log(`${type.toUpperCase()}: ${message}`);
    }
};
