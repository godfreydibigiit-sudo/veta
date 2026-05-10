/**
 * VETA Hotel Booking System
 * Main JavaScript File
 */

(function() {
    'use strict';

    // ============================================
    // DOM READY
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initNavigation();
        initAlerts();
        initDateInputs();
        initModals();
        initTooltips();
        initPrintButtons();
        initRealtimeUpdates();
    });

    // ============================================
    // NAVIGATION
    // ============================================

    function initNavigation() {
        const toggleBtn = document.querySelector('.navbar-toggle');
        const navbarNav = document.querySelector('.navbar-nav');
        
        if (toggleBtn && navbarNav) {
            toggleBtn.addEventListener('click', function() {
                navbarNav.classList.toggle('active');
                const isExpanded = navbarNav.classList.contains('active');
                toggleBtn.setAttribute('aria-expanded', isExpanded);
                
                // Animate icon
                const icon = toggleBtn.querySelector('i');
                if (icon) {
                    icon.className = isExpanded ? 'fas fa-times' : 'fas fa-bars';
                }
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!toggleBtn.contains(event.target) && !navbarNav.contains(event.target)) {
                    navbarNav.classList.remove('active');
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    const icon = toggleBtn.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-bars';
                    }
                }
            });
            
            // Close menu on window resize
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    navbarNav.classList.remove('active');
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    const icon = toggleBtn.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-bars';
                    }
                }
            });
        }
        
        // Active link highlighting
        highlightActiveLink();
    }

    function highlightActiveLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href) && href !== '/') {
                link.classList.add('active');
            } else if (href === '/' && currentPath === '/') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // ============================================
    // ALERTS & MESSAGES
    // ============================================

    function initAlerts() {
        // Auto-dismiss alerts
        const alerts = document.querySelectorAll('.alert-dismissible');
        
        alerts.forEach(alert => {
            // Add close button functionality
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    dismissAlert(alert);
                });
            }
            
            // Auto-dismiss after 5 seconds for success/info messages
            if (alert.classList.contains('alert-success') || 
                alert.classList.contains('alert-info')) {
                setTimeout(() => {
                    dismissAlert(alert);
                }, 5000);
            }
        });
    }

    function dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        alert.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            alert.remove();
        }, 300);
    }

    // ============================================
    // DATE INPUTS
    // ============================================

    function initDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            // Set minimum date to today
            if (!input.getAttribute('min')) {
                const today = new Date().toISOString().split('T')[0];
                input.setAttribute('min', today);
            }
            
            // Auto-set checkout date based on checkin
            if (input.name === 'check_in') {
                input.addEventListener('change', function() {
                    const checkOut = document.querySelector('input[name="check_out"]');
                    if (checkOut && this.value) {
                        const nextDay = new Date(this.value);
                        nextDay.setDate(nextDay.getDate() + 1);
                        checkOut.setAttribute('min', nextDay.toISOString().split('T')[0]);
                        
                        if (checkOut.value && checkOut.value <= this.value) {
                            checkOut.value = nextDay.toISOString().split('T')[0];
                        }
                    }
                });
            }
        });
    }

    // ============================================
    // MODALS
    // ============================================

    function initModals() {
        // Open modal
        document.querySelectorAll('[data-modal-target]').forEach(button => {
            button.addEventListener('click', function() {
                const modalId = this.getAttribute('data-modal-target');
                const modal = document.getElementById(modalId);
                if (modal) {
                    openModal(modal);
                }
            });
        });
        
        // Close modal
        document.querySelectorAll('.modal-overlay, [data-modal-close]').forEach(element => {
            element.addEventListener('click', function(event) {
                if (event.target === this || this.hasAttribute('data-modal-close')) {
                    const modal = this.closest('.modal-overlay');
                    if (modal) {
                        closeModal(modal);
                    }
                }
            });
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const openModal = document.querySelector('.modal-overlay.active');
                if (openModal) {
                    closeModal(openModal);
                }
            }
        });
    }

    function openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input if exists
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    function closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // ============================================
    // TOOLTIPS
    // ============================================

    function initTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', function(event) {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = this.getAttribute('data-tooltip');
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
                tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
                
                this._tooltip = tooltip;
            });
            
            element.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });
    }

    // ============================================
    // PRINT FUNCTIONALITY
    // ============================================

    function initPrintButtons() {
        document.querySelectorAll('[data-print]').forEach(button => {
            button.addEventListener('click', function() {
                window.print();
            });
        });
    }

    // ============================================
    // REAL-TIME UPDATES (Dashboard)
    // ============================================

    function initRealtimeUpdates() {
        const dashboardStats = document.getElementById('dashboard-stats');
        if (!dashboardStats) return;
        
        // Update every 30 seconds
        setInterval(updateDashboardStats, 30000);
    }

    function updateDashboardStats() {
        fetch('/staff/api/realtime-stats/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            updateStatValue('available-rooms', data.available_rooms);
            updateStatValue('occupied-rooms', data.occupied_rooms);
            updateStatValue('checked-in-today', data.checked_in_today);
            updateStatValue('today-revenue', formatCurrency(data.today_revenue));
            updateStatValue('pending-bookings', data.pending_bookings);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
    }

    function updateStatValue(id, value) {
        const element = document.getElementById(id);
        if (element) {
            // Animate value change
            element.style.transform = 'scale(1.1)';
            element.style.transition = 'transform 0.3s ease';
            element.textContent = value;
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 300);
        }
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    function formatCurrency(amount) {
        return 'TZS ' + Number(amount).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    // ============================================
    // FORM VALIDATION
    // ============================================

    window.validateForm = function(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    };

    // ============================================
    // CONFIRMATION DIALOG
    // ============================================

    window.confirmAction = function(message, callback) {
        if (confirm(message || 'Are you sure you want to proceed?')) {
            if (typeof callback === 'function') {
                callback();
            }
        }
    };

    // ============================================
    // AJAX HELPERS
    // ============================================

    window.ajaxPost = function(url, data, successCallback, errorCallback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            if (errorCallback) errorCallback(error);
            else console.error('Error:', error);
        });
    };

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    // ============================================
    // ANIMATIONS
    // ============================================

    // Intersection Observer for fade-in animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        document.querySelectorAll('.fade-in').forEach(element => {
            observer.observe(element);
        });
    }

})();