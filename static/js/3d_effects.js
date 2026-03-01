/**
 * 3d_effects.js - High-performance 3D Tilt and Entrance Animations using GSAP
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize 3D Tilt Effect for cards
    initTiltEffect();

    // 2. Dashboard Entrance Animations
    initEntranceAnimations();
});

function initTiltEffect() {
    const cards = document.querySelectorAll('.tilt-card');
    
    if (window.innerWidth < 768) return; // Disable on mobile for performance

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -10; // Max 10 degrees
            const rotateY = ((x - centerX) / centerX) * 10;  // Max 10 degrees
            
            gsap.to(card, {
                duration: 0.5,
                rotateX: rotateX,
                rotateY: rotateY,
                transformPerspective: 1000,
                ease: 'power2.out'
            });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                duration: 0.5,
                rotateX: 0,
                rotateY: 0,
                ease: 'power2.out'
            });
        });
    });
}

function initEntranceAnimations() {
    // Staggered entrance for stat cards
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards.length > 0) {
        gsap.from(statCards, {
            duration: 0.8,
            y: 50,
            opacity: 0,
            stagger: 0.1,
            ease: 'back.out(1.7)',
            delay: 0.2
        });
    }

    // Fade in for main dashboard sections
    const sections = document.querySelectorAll('.dashboard-stats, .row > .col > .card');
    if (sections.length > 0) {
        gsap.from(sections, {
            duration: 1,
            opacity: 0,
            y: 30,
            stagger: 0.15,
            ease: 'power3.out',
            delay: 0.1
        });
    }
}
