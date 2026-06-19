/**
 * VETA Hotel Admin - Custom JavaScript
 * Professional Enhancements
 */
(function() {
    'use strict';

    // ============================================
    // MOBILE SIDEBAR ENHANCEMENT
    // ============================================
    function enhanceMobileSidebar() {
        const sidebar = document.querySelector('.main-sidebar');
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-mobile-overlay';
        overlay.style.cssText = `
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1030;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(overlay);

        // Toggle sidebar on mobile
        document.querySelector('[data-widget="pushmenu"]')?.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                if (sidebar?.classList.contains('open')) {
                    overlay.style.display = 'block';
                    document.body.style.overflow = 'hidden';
                } else {
                    overlay.style.display = 'none';
                    document.body.style.overflow = '';
                }
            }
        });

        // Close on overlay click
        overlay.addEventListener('click', function() {
            document.querySelector('[data-widget="pushmenu"]')?.click();
            this.style.display = 'none';
            document.body.style.overflow = '';
        });
    }

    // ============================================
    // TABLE ROW CLICKABLE
    // ============================================
    function makeTableRowsClickable() {
        document.querySelectorAll('.table-clickable tbody tr').forEach(row => {
            const link = row.querySelector('a');
            if (link) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function(e) {
                    if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
                        window.location = link.href;
                    }
                });
            }
        });
    }

    // ============================================
    // AUTO-HIDE ALERTS
    // ============================================
    function autoHideAlerts() {
        document.querySelectorAll('.alert-success, .alert-info').forEach(alert => {
            setTimeout(() => {
                alert.style.transition = 'all 0.3s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        });
    }

    // ============================================
    // CONFIRM DANGEROUS ACTIONS
    // ============================================
    function confirmDangerActions() {
        document.querySelectorAll('.btn-danger:not([data-no-confirm])').forEach(btn => {
            btn.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to perform this action? This cannot be undone.')) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
        });
    }

    // ============================================
    // FORM ENHANCEMENTS
    // ============================================
    function enhanceForms() {
        // Auto-focus first input on forms
        const firstInput = document.querySelector('form:not(.navbar-search-block) .form-control:not([type="hidden"]):not([readonly])');
        if (firstInput && window.innerWidth > 768) {
            firstInput.focus();
        }

        // Add character counter to textareas with maxlength
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            const max = textarea.getAttribute('maxlength');
            const counter = document.createElement('small');
            counter.className = 'text-muted char-counter';
            counter.style.cssText = 'display: block; text-align: right; margin-top: 4px;';
            counter.textContent = `0 / ${max} characters`;
            textarea.parentNode.appendChild(counter);

            textarea.addEventListener('input', function() {
                counter.textContent = `${this.value.length} / ${max} characters`;
                if (this.value.length > max * 0.9) {
                    counter.style.color = '#ef4444';
                } else {
                    counter.style.color = '#6b7280';
                }
            });
        });
    }

    // ============================================
    // DATE INPUT ENHANCEMENTS
    // ============================================
    function enhanceDateInputs() {
        document.querySelectorAll('input[type="date"]').forEach(input => {
            if (!input.getAttribute('min')) {
                const today = new Date().toISOString().split('T')[0];
                input.setAttribute('min', today);
            }
        });
    }

    // ============================================
    // INITIALIZE
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        enhanceMobileSidebar();
        makeTableRowsClickable();
        autoHideAlerts();
        confirmDangerActions();
        enhanceForms();
        enhanceDateInputs();
    });

})();