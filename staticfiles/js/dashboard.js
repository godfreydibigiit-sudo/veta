/**
 * VETA Hotel Dashboard - Responsive Controller
 */
(function() {
    'use strict';

    const sidebar = document.getElementById('dashboardSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.getElementById('sidebarToggle');

    // Toggle sidebar
    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Hamburger button
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    // Close on overlay click
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Auto-close sidebar on window resize to desktop size
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768 && sidebar && sidebar.classList.contains('open')) {
                closeSidebar();
            }
        }, 250);
    });

    // Active link highlighting
    function setActiveLink() {
        const path = window.location.pathname;
        const links = document.querySelectorAll('.sidebar-link');
        
        links.forEach(function(link) {
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Remove all active first
            link.classList.remove('active');
            
            // Check if current path matches
            if (path === href || (href !== '/staff/' && path.startsWith(href))) {
                link.classList.add('active');
            }
        });
    }

    // Quick search
    const searchForm = document.getElementById('navbarSearchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = this.querySelector('input');
            if (input && input.value.trim()) {
                window.location.href = '/bookings/staff/search/?q=' + encodeURIComponent(input.value.trim());
            }
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        setActiveLink();
    });

})();