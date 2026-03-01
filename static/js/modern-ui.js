// Modern Dashboard Animations & Interactions

document.addEventListener('DOMContentLoaded', function() {
    initializeAnimations();
    initializeInteractions();
    setupScrollAnimations();
});

/**
 * Initialize page entrance animations
 */
function initializeAnimations() {
    // Fade in on page load
    const fadeInElements = document.querySelectorAll('.animate-fade-in');
    fadeInElements.forEach((el, index) => {
        el.style.animation = `fadeInUp 0.6s ease-out ${index * 0.1}s both`;
    });

    // Animate stat cards on scroll
    observeElements('.stat-card', 'fadeInUp');
}

/**
 * Initialize interactive elements
 */
function initializeInteractions() {
    // Hover lift effect for cards
    const hoverLiftCards = document.querySelectorAll('.hover-lift');
    hoverLiftCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Glow effect on hover
    const hoverGlowElements = document.querySelectorAll('.hover-glow');
    hoverGlowElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.4)';
        });
        el.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'none';
        });
    });

    // Button ripple effect
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
}

/**
 * Create ripple effect on button click
 */
function createRipple(e) {
    const button = e.currentTarget;
    const x = e.clientX - button.getBoundingClientRect().left;
    const y = e.clientY - button.getBoundingClientRect().top;

    const ripple = document.createElement('span');
    ripple.style.width = ripple.style.height = '20px';
    ripple.style.left = x - 10 + 'px';
    ripple.style.top = y - 10 + 'px';
    ripple.style.position = 'absolute';
    ripple.style.background = 'rgba(255, 255, 255, 0.5)';
    ripple.style.borderRadius = '50%';
    ripple.style.pointerEvents = 'none';
    ripple.style.animation = 'ripple-expand 0.6s ease-out';

    button.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
}

/**
 * Intersection Observer for scroll animations
 */
function observeElements(selector, animationClass) {
    const elements = document.querySelectorAll(selector);
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add(animationClass);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });

    elements.forEach(el => observer.observe(el));
}

/**
 * Setup scroll-triggered animations
 */
function setupScrollAnimations() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderColor = 'var(--accent-green)';
            this.style.boxShadow = '0 0 30px rgba(16, 185, 129, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.borderColor = 'var(--border-light)';
            this.style.boxShadow = 'none';
        });
    });
}

/**
 * Smooth number counter for stat cards
 */
function animateCounter(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 50);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 50);
}

/**
 * Initialize counter animations when page loads
 */
window.addEventListener('load', function() {
    // Animate stat card values
    const statValues = document.querySelectorAll('.stat-card-value');
    statValues.forEach(value => {
        const text = value.textContent;
        const numberMatch = text.match(/[\d.]+/);
        
        if (numberMatch) {
            const target = parseFloat(numberMatch[0]);
            if (!isNaN(target)) {
                // Optional: Uncomment to animate counters
                // animateCounter(value, target, 2000);
            }
        }
    });
});

/**
 * Form validation with visual feedback
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    
    form.addEventListener('submit', function(e) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
            showNotification('Please fill in all required fields', 'warning');
        }
    });
}

/**
 * Toast notification system
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        animation: slideInNotification 0.4s ease-out;
        min-width: 300px;
    `;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Get icon based on notification type
 */
function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Smooth scroll behavior
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
}

/**
 * Initialize theme switching
 */
function initializeThemeSwitcher() {
    const themeSwitcher = document.getElementById('theme-switcher');
    
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
}

/**
 * Initialize tooltips and popovers
 */
function initializeTooltips() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Add animations to newly added elements
 */
function animateNewElement(element) {
    element.classList.add('animate-bounce');
    setTimeout(() => {
        element.classList.remove('animate-bounce');
    }, 600);
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for scroll events
 */
function throttle(func, limit) {
    let inThrottle;
    
    return function() {
        const args = arguments;
        const context = this;
        
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        }
    };
}

/**
 * Initialize all UI enhancements on page load
 */
function initializeUI() {
    setupSmoothScroll();
    initializeThemeSwitcher();
    initializeTooltips();
    
    // Setup animations for dynamically added content
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element node
                    if (node.classList.contains('card')) {
                        node.classList.add('animate-fade-in');
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

/**
 * Run initialization when DOM is fully loaded
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUI);
} else {
    initializeUI();
}
