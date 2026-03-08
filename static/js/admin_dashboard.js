/* ======================================================================
   Custom Admin Dashboard JavaScript
   ====================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    const btnCloseSidebar = document.getElementById('sidebarToggle');
    
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    if (btnCloseSidebar) {
        btnCloseSidebar.addEventListener('click', function() {
            sidebar.classList.remove('show');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnToggle = sidebarToggleBtn && sidebarToggleBtn.contains(event.target);
        
        if (!isClickInsideSidebar && !isClickOnToggle) {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Table row selection
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const selectAllCheckbox = document.getElementById('selectAll');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Add hover effects to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                // Handle search
                const query = this.value;
                console.log('Searching for:', query);
            }
        });
    }
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const confirmed = confirm(this.getAttribute('onclick').match(/'([^']*)'/)[1]);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
    
    // Notification badge animation
    const notificationBadge = document.querySelector('.badge:not(.list-group-item .badge)');
    if (notificationBadge) {
        setInterval(() => {
            notificationBadge.style.animation = 'pulse 2s infinite';
        }, 1000);
    }
    
    // Status badge colors based on status
    const statusBadges = document.querySelectorAll('[class*="badge"]');
    statusBadges.forEach(badge => {
        const text = badge.textContent.toLowerCase();
        
        if (text.includes('published') || text.includes('approved') || text.includes('active')) {
            badge.classList.add('bg-success');
        } else if (text.includes('draft') || text.includes('pending') || text.includes('inactive')) {
            badge.classList.add('bg-warning', 'text-dark');
        } else if (text.includes('admin') || text.includes('staff')) {
            badge.classList.add('bg-danger');
        }
    });
    
    // Smooth scroll to sections
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // ESC to close modals and dropdowns
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
    
    // Add loading state to buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            // Uncomment to show loading state
            // this.disabled = true;
            // this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        });
    });
    
    // Tooltip initialization (Bootstrap 5)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popover initialization (Bootstrap 5)
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Real-time search in tables
    const tableSearchInputs = document.querySelectorAll('input[placeholder*="Search"]');
    tableSearchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchText)) {
                    row.style.display = '';
                    row.style.animation = 'fadeIn 0.3s ease';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
    
    // Auto-update timestamp relative text
    function updateTimeAgo() {
        const elements = document.querySelectorAll('[data-timestamp]');
        elements.forEach(el => {
            const timestamp = parseInt(el.getAttribute('data-timestamp'));
            const date = new Date(timestamp * 1000);
            const seconds = Math.floor((new Date() - date) / 1000);
            
            let timeAgo = '';
            if (seconds < 60) {
                timeAgo = 'just now';
            } else if (seconds < 3600) {
                timeAgo = Math.floor(seconds / 60) + ' minutes ago';
            } else if (seconds < 86400) {
                timeAgo = Math.floor(seconds / 3600) + ' hours ago';
            } else {
                timeAgo = Math.floor(seconds / 86400) + ' days ago';
            }
            
            el.textContent = timeAgo;
        });
    }
    
    // Update time ago every minute
    setInterval(updateTimeAgo, 60000);
    updateTimeAgo();
    
    // Export data functionality
    const exportButton = document.getElementById('exportData');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            const table = document.querySelector('table');
            let csv = '';
            
            // Get table headers
            const headers = table.querySelectorAll('thead th');
            headers.forEach(header => {
                csv += header.textContent + ',';
            });
            csv += '\n';
            
            // Get table rows
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {
                    csv += '"' + cell.textContent.replace(/"/g, '""') + '"' + ',';
                });
                csv += '\n';
            });
            
            // Download CSV
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'export_' + new Date().getTime() + '.csv';
            a.click();
        });
    }
    
    // Print functionality
    const printButton = document.getElementById('printData');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Responsive sidebar on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('show');
        }
    });
});

// CSS3 animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Console message
console.log('%c🎉 Custom Admin Dashboard Loaded', 'color: #6366f1; font-size: 16px; font-weight: bold;');
