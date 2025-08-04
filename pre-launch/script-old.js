// Mobile Navigation
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelector('.nav-links');
    const navLinksItems = navLinks.querySelectorAll('a');

    // Toggle mobile menu
    if (mobileMenu) {
        mobileMenu.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            
            // Animate menu icon
            const icon = mobileMenu.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.className = 'ph ph-x';
                document.body.style.overflow = 'hidden'; // Prevent background scroll
            } else {
                icon.className = 'ph ph-list';
                document.body.style.overflow = '';
            }
        });
    }

    // Close mobile menu when clicking on links
    navLinksItems.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                navLinks.classList.remove('active');
                const icon = mobileMenu.querySelector('i');
                icon.className = 'ph ph-list';
                document.body.style.overflow = '';
            }
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navLinks.contains(event.target) || mobileMenu.contains(event.target);
        
        if (!isClickInsideNav && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            const icon = mobileMenu.querySelector('i');
            icon.className = 'ph ph-list';
            document.body.style.overflow = '';
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navLinks.classList.remove('active');
            const icon = mobileMenu.querySelector('i');
            icon.className = 'ph ph-list';
            document.body.style.overflow = '';
        }
    });
});

// Smooth Scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.offsetTop;
            const offsetPosition = elementPosition - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar scroll effect with debouncing
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

const debouncedScrollHandler = debounce(function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
}, 10);

window.addEventListener('scroll', debouncedScrollHandler);

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Initialize animations
document.addEventListener('DOMContentLoaded', function() {
    const animateElements = document.querySelectorAll('.feature-card, .timeline-item, .community-card, .highlight');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Button click handlers
document.addEventListener('DOMContentLoaded', function() {
    // Get Early Access buttons
    const earlyAccessButtons = document.querySelectorAll('.btn-primary');
    earlyAccessButtons.forEach(button => {
        if (button.textContent.includes('Start Your Journey') || 
            button.textContent.includes('Get Early Access') ||
            button.textContent.includes('Join the Journey') ||
            button.textContent.includes('Join the Community')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('early-access');
            });
        }
    });

    // Watch Demo button
    const demoButtons = document.querySelectorAll('.btn-secondary');
    demoButtons.forEach(button => {
        if (button.textContent.includes('Watch Demo')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('demo');
            });
        }
        if (button.textContent.includes('Stay Updated')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('newsletter');
            });
        }
    });
});

// Modal functionality
function showModal(type) {
    let title, content, buttonText;
    
    switch(type) {
        case 'early-access':
            title = 'Join MantraPath Early Access';
            content = `
                <p>Thank you for your interest in MantraPath! We're currently in beta and preparing for our official launch.</p>
                <div style="margin: 20px 0;">
                    <input type="email" placeholder="Enter your email address" id="modalEmail" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px;">
                    <p style="font-size: 14px; color: #666;">We'll notify you as soon as early access becomes available!</p>
                </div>
            `;
            buttonText = 'Join Waitlist';
            break;
        case 'demo':
            title = 'MantraPath Demo';
            content = `
                <p>We're preparing an exciting walkthrough of MantraPath's features!</p>
                <p>Our demo will showcase:</p>
                <ul style="text-align: left; margin: 15px 0; padding-left: 20px;">
                    <li>AI-powered companion interactions</li>
                    <li>Smart mood tracking and analytics</li>
                    <li>Guided journaling experience</li>
                    <li>Community support features</li>
                </ul>
                <p style="margin-top: 20px;">Demo video coming soon! Leave your email to be notified when it's ready.</p>
                <input type="email" placeholder="Your email address" id="modalEmail" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0;">
            `;
            buttonText = 'Notify Me';
            break;
        case 'newsletter':
            title = 'Stay Updated';
            content = `
                <p>Get the latest updates on MantraPath's development and be the first to know about our launch!</p>
                <div style="margin: 20px 0;">
                    <input type="email" placeholder="Enter your email address" id="modalEmail" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 15px;">
                    <label style="display: flex; align-items: center; font-size: 14px; color: #666;">
                        <input type="checkbox" id="modalUpdates" style="margin-right: 8px;">
                        I'd like to receive updates about MantraPath's progress and launch
                    </label>
                </div>
            `;
            buttonText = 'Subscribe';
            break;
    }
    
    const modalHTML = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="closeModal()">
                        <i class="ph ph-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="closeModal()">Cancel</button>
                    <button class="btn-primary" onclick="submitModal('${type}')">${buttonText}</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles if they don't exist
    if (!document.querySelector('#modal-styles')) {
        const modalStyles = document.createElement('style');
        modalStyles.id = 'modal-styles';
        modalStyles.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                padding: 20px;
                backdrop-filter: blur(5px);
            }
            
            .modal-content {
                background: white;
                border-radius: 16px;
                max-width: 500px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: modalSlideIn 0.3s ease-out;
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 24px 24px 0;
                border-bottom: 1px solid #eee;
                margin-bottom: 24px;
            }
            
            .modal-header h3 {
                margin: 0;
                color: #2c3e50;
                font-size: 1.5rem;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
                padding: 4px;
                border-radius: 4px;
                transition: background 0.2s;
            }
            
            .modal-close:hover {
                background: #f5f5f5;
            }
            
            .modal-body {
                padding: 0 24px 24px;
                color: #5a6c7d;
                line-height: 1.6;
            }
            
            .modal-footer {
                padding: 24px;
                border-top: 1px solid #eee;
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            @keyframes modalSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            @media (max-width: 768px) {
                .modal-content {
                    margin: 20px;
                    max-height: calc(100vh - 40px);
                }
                
                .modal-footer {
                    flex-direction: column;
                }
                
                .modal-footer .btn-primary,
                .modal-footer .btn-secondary {
                    width: 100%;
                    margin: 0;
                }
            }
        `;
        document.head.appendChild(modalStyles);
    }
    
    // Create and show modal
    const modalElement = document.createElement('div');
    modalElement.innerHTML = modalHTML;
    modalElement.id = 'active-modal';
    document.body.appendChild(modalElement);
    document.body.style.overflow = 'hidden';
    
    // Focus on email input
    setTimeout(() => {
        const emailInput = document.getElementById('modalEmail');
        if (emailInput) emailInput.focus();
    }, 100);
}

function closeModal() {
    const modal = document.getElementById('active-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

function submitModal(type) {
    const email = document.getElementById('modalEmail')?.value;
    
    if (email && email.includes('@')) {
        // In a real application, this would send data to your backend
        console.log('Submitting:', { type, email });
        closeModal();
        showThankYouMessage();
    } else if (email) {
        alert('Please enter a valid email address.');
    } else {
        alert('Please enter your email address.');
    }
}

function showThankYouMessage() {
    const thankYouHTML = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Thank You! 🎉</h3>
                    <button class="modal-close" onclick="closeModal()">
                        <i class="ph ph-x"></i>
                    </button>
                </div>
                <div class="modal-body" style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 16px;">✅</div>
                    <p>We've received your information and will keep you updated on MantraPath's progress!</p>
                    <p style="font-size: 14px; color: #666; margin-top: 16px;">Keep an eye on your inbox for exciting updates about your wellness journey.</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="closeModal()" style="width: 100%;">Continue Exploring</button>
                </div>
            </div>
        </div>
    `;
    
    const thankYouElement = document.createElement('div');
    thankYouElement.innerHTML = thankYouHTML;
    thankYouElement.id = 'active-modal';
    document.body.appendChild(thankYouElement);
}

// Keyboard accessibility
document.addEventListener('keydown', function(e) {
    // Handle ESC key for modals
    if (e.key === 'Escape') {
        const modal = document.getElementById('active-modal');
        if (modal) {
            closeModal();
            return;
        }
        
        // Handle ESC for mobile menu
        const navLinks = document.querySelector('.nav-links');
        const mobileMenu = document.getElementById('mobileMenu');
        
        if (navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            const icon = mobileMenu.querySelector('i');
            icon.className = 'ph ph-list';
            document.body.style.overflow = '';
            mobileMenu.focus();
        }
    }
});

// Touch and swipe optimizations for mobile
let touchStartY = 0;
let touchStartX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartY = e.touches[0].clientY;
    touchStartX = e.touches[0].clientX;
}, { passive: true });

document.addEventListener('touchmove', function(e) {
    // Add any touch-specific optimizations here
}, { passive: true });

// Performance optimizations
// Lazy load non-critical resources
window.addEventListener('load', function() {
    // Preload critical resources
    const criticalResources = [
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/phosphor-icons/2.0.2/phosphor.min.css'
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = resource;
        document.head.appendChild(link);
    });
});

// Console welcome message
console.log(`
🌟 Welcome to MantraPath Pre-launch Site! 🌟

MantraPath is your intelligent companion for mental wellness and personal growth.

Built with ❤️ for better mental health support.

Features:
- 📱 Mobile-first responsive design
- 🎨 Modern UI with smooth animations  
- ♿ Accessibility-focused
- 🚀 Performance optimized
- 🔒 Privacy-conscious

Ready to transform mental wellness support!
`);

console.log('MantraPath Pre-launch Site Loaded Successfully! 🎉');
        });
    });
    
    // Navbar scroll effect
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (scrollTop > lastScrollTop && scrollTop > 200) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .timeline-item, .community-card, .floating-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // Button interactions
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Lazy loading for images (if any are added later)
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Form handling (if forms are added later)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add form handling logic here
            console.log('Form submitted');
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMenuOpen) {
            toggleMobileMenu();
        }
    });
    
    // Touch gestures for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            if (swipeDistance > 0 && !isMenuOpen) {
                // Swipe right - could open menu or navigate
                console.log('Swipe right detected');
            } else if (swipeDistance < 0 && isMenuOpen) {
                // Swipe left - close menu
                toggleMobileMenu();
            }
        }
    }
    
    // Performance optimization - debounce resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Handle resize logic here
            if (window.innerWidth > 768 && isMenuOpen) {
                toggleMobileMenu();
            }
        }, 250);
    });
    
    // Add loading state management
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
        
        // Stagger animation of hero elements
        const heroElements = document.querySelectorAll('.hero-content > *');
        heroElements.forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('animate-in');
            }, index * 100);
        });
    });
    
    // Add stats counter animation
    const statNumbers = document.querySelectorAll('.stat-number');
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => statsObserver.observe(stat));
    
    function animateValue(element) {
        const text = element.textContent;
        const hasPlus = text.includes('+');
        const hasPercent = text.includes('%');
        const isInfinity = text.includes('∞');
        
        if (isInfinity) return; // Skip infinity symbol
        
        const value = parseInt(text.replace(/[^0-9]/g, ''));
        let current = 0;
        const increment = value / 50;
        const duration = 1000;
        const stepTime = duration / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
                current = value;
                clearInterval(timer);
            }
            
            let displayValue = Math.floor(current);
            if (displayValue >= 1000) {
                displayValue = Math.floor(displayValue / 1000) + 'k';
            }
            
            element.textContent = displayValue + (hasPlus ? '+' : '') + (hasPercent ? '%' : '');
        }, stepTime);
    }
    
    // Add error handling for failed resources
    window.addEventListener('error', function(e) {
        if (e.target.tagName === 'IMG') {
            e.target.style.display = 'none';
        }
    });
    
    // Add focus management for accessibility
    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    
    function trapFocus(element) {
        const focusableContent = element.querySelectorAll(focusableElements);
        const firstFocusableElement = focusableContent[0];
        const lastFocusableElement = focusableContent[focusableContent.length - 1];
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableElement) {
                        lastFocusableElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusableElement) {
                        firstFocusableElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }
    
    // Initialize tooltips (if needed)
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', showTooltip);
        trigger.addEventListener('mouseleave', hideTooltip);
        trigger.addEventListener('focus', showTooltip);
        trigger.addEventListener('blur', hideTooltip);
    });
    
    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }
    
    function hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
});

// Add CSS for mobile menu and animations
const additionalStyles = `
.mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    z-index: 999;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.mobile-overlay.active {
    opacity: 1;
    visibility: visible;
}

@media (max-width: 767px) {
    .nav-links {
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        padding: 32px 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transform: translateY(-100%);
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .nav-links.mobile-active {
        transform: translateY(0);
        opacity: 1;
        visibility: visible;
    }
    
    .nav-links a {
        padding: 12px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        font-size: 16px;
    }
    
    .nav-links a:last-child {
        border-bottom: none;
    }
    
    .nav-links .btn-primary {
        margin-top: 20px;
        width: 100%;
    }
}

.navbar.scrolled {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.navbar.hidden {
    transform: translateY(-100%);
}

.navbar {
    transition: all 0.3s ease;
}

/* Animation classes */
.animate-in {
    animation: slideInUp 0.6s ease forwards;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.feature-card,
.timeline-item,
.community-card {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s ease;
}

.feature-card.animate-in,
.timeline-item.animate-in,
.community-card.animate-in {
    opacity: 1;
    transform: translateY(0);
}

/* Button ripple effect */
.btn-primary,
.btn-secondary {
    position: relative;
    overflow: hidden;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: rippleAnimation 0.6s linear;
    pointer-events: none;
}

@keyframes rippleAnimation {
    to {
        transform: scale(2);
        opacity: 0;
    }
}

/* Loading states */
body:not(.loaded) .hero-content > * {
    opacity: 0;
    transform: translateY(20px);
}

.hero-content > * {
    transition: all 0.6s ease;
}

/* Tooltip styles */
.tooltip {
    position: absolute;
    background: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    white-space: nowrap;
    z-index: 1000;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s ease;
    pointer-events: none;
}

.tooltip.show {
    opacity: 1;
    transform: translateY(0);
}

.tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #333;
}

/* Dark mode styles for mobile menu */
@media (prefers-color-scheme: dark) {
    .mobile-overlay {
        background: rgba(0, 0, 0, 0.8);
    }
    
    @media (max-width: 767px) {
        .nav-links {
            background: #2d2d2d;
            color: white;
        }
        
        .nav-links a {
            color: white;
            border-bottom-color: rgba(255, 255, 255, 0.1);
        }
    }
}

/* High contrast mode for animations */
@media (prefers-contrast: high) {
    .animate-in {
        animation: none;
        opacity: 1 !important;
        transform: none !important;
    }
}

/* Focus indicators */
.nav-links a:focus,
.btn-primary:focus,
.btn-secondary:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

/* Improved touch targets */
@media (max-width: 768px) {
    .nav-links a,
    .btn-primary,
    .btn-secondary {
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
