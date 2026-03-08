// ============================================
// PERSONAL BLOG - AUTHENTICATION SYSTEM
// JavaScript for interactivity and UX improvements
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functions
    initializePasswordToggle();
    initializeFormValidation();
    initializeMessageAutoClose();
});

/**
 * Toggle password visibility in input fields
 * Useful for login and password change forms
 */
function initializePasswordToggle() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(field => {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.textContent = '👁️';
        toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
        
        // Wrap field and add button
        field.parentElement.style.position = 'relative';
        field.parentElement.appendChild(toggleBtn);
        
        // Toggle visibility
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const isPassword = field.type === 'password';
            field.type = isPassword ? 'text' : 'password';
            toggleBtn.textContent = isPassword ? '🙈' : '👁️';
            toggleBtn.classList.toggle('active');
        });
    });
}

/**
 * Basic client-side form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form, .profile-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Remove error class on input
        form.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
            });
        });
    });
}

/**
 * Auto-close message alerts after 5 seconds
 */
function initializeMessageAutoClose() {
    const messages = document.querySelectorAll('.message');
    
    messages.forEach(message => {
        // Auto close after 5 seconds
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease-in-out forwards';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Smooth scroll behavior for links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

/**
 * Add active state to current navigation link
 */
function updateActiveNavLink() {
    const currentLocation = location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Update active link on page load
updateActiveNavLink();

/**
 * Handle remember me checkbox
 */
const rememberMeCheckbox = document.querySelector('input[name="remember_me"]');
if (rememberMeCheckbox) {
    // Check if was previously checked
    if (localStorage.getItem('remember_me') === 'true') {
        rememberMeCheckbox.checked = true;
    }
    
    // Save state when changed
    rememberMeCheckbox.addEventListener('change', function() {
        localStorage.setItem('remember_me', this.checked);
    });
}

/**
 * Prevent multiple form submissions
 */
document.querySelectorAll('.auth-form, .profile-form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Please wait...';
        }
    });
});
