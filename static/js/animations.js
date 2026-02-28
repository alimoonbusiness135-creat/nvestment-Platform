/**
 * animations.js - Handle level-based animations
 * This script helps with automatically applying animations based on scroll events,
 * user interactions, and other triggers.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all animations
    initAnimations();

    // Set up scroll-based animations
    setupScrollAnimations();

    // Set up click animations
    setupClickAnimations();

    // Add animation to staggered lists on page load
    animateStaggeredLists();
});

/**
 * Initialize all animations that should start on page load
 */
function initAnimations() {
    // Add visible class to on-load elements after a small delay
    setTimeout(function() {
        document.querySelectorAll('.on-load').forEach(function(element) {
            element.classList.add('visible');
        });
    }, 100);

    // Apply level-based animations to elements with data-animate attribute
    document.querySelectorAll('[data-animate]').forEach(function(element) {
        const animationType = element.getAttribute('data-animate');
        const delay = element.getAttribute('data-delay') || 0;
        
        setTimeout(function() {
            element.classList.add(animationType);
        }, delay * 1000);
    });

    // Initialize progress bar animations
    document.querySelectorAll('.progress-animate').forEach(function(progressBar) {
        setTimeout(function() {
            progressBar.classList.add('animate');
        }, 500);
    });
}

/**
 * Set up scroll-based animations using Intersection Observer
 */
function setupScrollAnimations() {
    // Check if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // If element is in viewport
                if (entry.isIntersecting) {
                    // Add the animation class
                    if (entry.target.classList.contains('fade-in-section')) {
                        entry.target.classList.add('is-visible');
                    }

                    // Add animate class to sequence containers
                    if (entry.target.classList.contains('sequence-fade') || 
                        entry.target.classList.contains('sequence-zoom') ||
                        entry.target.classList.contains('stagger-list')) {
                        entry.target.classList.add('animate');
                    }

                    // Add the animate class to js-animate elements
                    if (entry.target.classList.contains('js-animate')) {
                        entry.target.classList.add('animate');
                    }

                    // If the element has been animated, stop observing it
                    observer.unobserve(entry.target);
                }
            });
        }, {
            root: null, // viewport
            threshold: 0.1, // 10% of element visible
            rootMargin: '0px 0px -50px 0px' // trigger slightly before element is in view
        });

        // Observe elements that should animate on scroll
        document.querySelectorAll('.fade-in-section, .sequence-fade, .sequence-zoom, .stagger-list, .js-animate').forEach(item => {
            observer.observe(item);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        document.querySelectorAll('.fade-in-section, .sequence-fade, .sequence-zoom, .stagger-list, .js-animate').forEach(item => {
            item.classList.add('is-visible', 'animate');
        });
    }
}

/**
 * Set up click-based animations
 */
function setupClickAnimations() {
    // Add ripple effect to elements with ripple-animation class
    document.querySelectorAll('.ripple-animation').forEach(function(element) {
        element.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            
            const rect = element.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = e.clientX - rect.left - size / 2 + 'px';
            ripple.style.top = e.clientY - rect.top - size / 2 + 'px';
            
            element.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Apply level-based animations on click for elements with data-click-animate
    document.querySelectorAll('[data-click-animate]').forEach(function(element) {
        element.addEventListener('click', function() {
            const animationType = element.getAttribute('data-click-animate');
            
            // Remove any existing animation classes
            element.classList.remove(
                'level-bounce', 'level-flash', 'level-pulse-glow', 
                'level-shake', 'level-tada', 'level-jello', 
                'level-swing', 'level-heartbeat', 'level-flip-x', 
                'level-flip-y', 'level-light-speed', 'level-roll'
            );
            
            // Force reflow to restart animation
            void element.offsetWidth;
            
            // Add the new animation class
            element.classList.add(animationType);
        });
    });
}

/**
 * Animate staggered lists
 */
function animateStaggeredLists() {
    document.querySelectorAll('.stagger-list').forEach(function(list) {
        // If the list is in the initial viewport, animate it
        const rect = list.getBoundingClientRect();
        const isInViewport = (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (isInViewport) {
            list.classList.add('animate');
        }
    });
}

/**
 * Helper function to manually trigger animations
 * @param {string} selector - CSS selector for elements to animate
 * @param {string} animationClass - Animation class to apply
 * @param {boolean} removeAfter - Whether to remove the class after animation
 */
function triggerAnimation(selector, animationClass, removeAfter = false) {
    document.querySelectorAll(selector).forEach(function(element) {
        // Remove the class first to restart animation
        element.classList.remove(animationClass);
        
        // Force reflow
        void element.offsetWidth;
        
        // Add the animation class
        element.classList.add(animationClass);
        
        if (removeAfter) {
            // Get the animation duration
            const style = window.getComputedStyle(element);
            const duration = parseFloat(style.animationDuration) * 1000;
            
            // Remove the class after animation completes
            setTimeout(function() {
                element.classList.remove(animationClass);
            }, duration);
        }
    });
}

/**
 * Apply sequence animation to any container
 * @param {string} selector - CSS selector for container
 * @param {string} animationName - Animation name to apply
 * @param {number} baseDelay - Base delay before starting sequence (in ms)
 * @param {number} stepDelay - Delay between each item (in ms)
 */
function applySequenceAnimation(selector, animationName, baseDelay = 0, stepDelay = 100) {
    const container = document.querySelector(selector);
    if (!container) return;
    
    const children = Array.from(container.children);
    
    children.forEach((child, index) => {
        child.style.opacity = '0';
        
        setTimeout(() => {
            child.style.animation = `${animationName} 0.5s forwards`;
            child.style.opacity = '1';
        }, baseDelay + (index * stepDelay));
    });
}

// Make functions available globally
window.triggerAnimation = triggerAnimation;
window.applySequenceAnimation = applySequenceAnimation; 