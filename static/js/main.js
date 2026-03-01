// Main JavaScript file for the investment platform

document.addEventListener('DOMContentLoaded', function () {
    // Initialize common UI elements
    initializeTooltips();
    initializeNotificationBadges();
    initializeSidebar();
    initializeFlashMessages();
    initializeResponsiveAdjustments();

    // Initialize page-specific functionality
    const currentPath = window.location.pathname;

    if (currentPath.includes('/deposit')) {
        initializeDepositForm();
    } else if (currentPath.includes('/withdrawal')) {
        initializeWithdrawalForm();
    } else if (currentPath.includes('/referrals')) {
        initializeReferralPage();
    } else if (currentPath.includes('/profile')) {
        initializeProfilePage();
    } else if (currentPath.includes('/settings')) {
        initializeSettingsPage();
    } else if (currentPath.includes('/dashboard')) {
        initializeDashboard();
    }

    // Initialize admin-specific functionality
    if (currentPath.includes('/admin')) {
        initializeAdminInterface();
    }
});

// Initialize tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        // Tooltips are CSS-only, no additional JS needed
    });
}

// Initialize notification badges
function initializeNotificationBadges() {
    const notificationBadges = document.querySelectorAll('.notification-badge');
    notificationBadges.forEach(badge => {
        // Ensure the count is displayed correctly
        const count = badge.getAttribute('data-count');
        if (count && parseInt(count) > 0) {
            badge.classList.add('has-notifications');
        } else {
            badge.classList.remove('has-notifications');
        }
    });
}

// Initialize sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            // Prevent scrolling when sidebar is open on mobile
            if (sidebar.classList.contains('open') && window.innerWidth <= 768) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close sidebar when clicking outside on small screens
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 &&
                !e.target.closest('.sidebar') &&
                !e.target.closest('.sidebar-toggle') &&
                sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                document.body.style.overflow = '';
            }
        });

        // Close button in sidebar for mobile
        const closeSidebar = document.querySelector('.close-sidebar');
        if (closeSidebar) {
            closeSidebar.addEventListener('click', () => {
                sidebar.classList.remove('open');
                document.body.style.overflow = '';
            });
        }
    }
}

// Initialize responsive adjustments
function initializeResponsiveAdjustments() {
    // Fix input zooming on mobile
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta && window.innerWidth < 768) {
        viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0');
    }

    // Improve touch targets on mobile
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        const smallButtons = document.querySelectorAll('.btn-sm');
        smallButtons.forEach(btn => {
            btn.classList.add('touch-friendly');
        });
    }

    // Responsive tables
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });

    // Adjust padding for status pills on mobile
    if (window.innerWidth < 576) {
        const badges = document.querySelectorAll('.badge');
        badges.forEach(badge => {
            badge.style.padding = '4px 6px';
        });
    }
}

// Initialize flash messages with auto-dismiss
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        // Add close button
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'close';
        closeButton.style.float = 'right';
        closeButton.style.border = 'none';
        closeButton.style.background = 'none';
        closeButton.style.fontSize = '1.5rem';
        closeButton.style.fontWeight = 'bold';
        closeButton.style.cursor = 'pointer';
        closeButton.style.marginLeft = '10px';

        closeButton.addEventListener('click', () => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        });

        message.prepend(closeButton);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);

        // Add transition
        message.style.transition = 'opacity 0.3s ease';
    });
}

// Initialize deposit form
function initializeDepositForm() {
    const amountInput = document.getElementById('amount');
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentMethodInput = document.getElementById('payment_method');
    const depositForm = document.getElementById('deposit-form');

    if (amountInput && paymentMethods.length > 0 && paymentMethodInput && depositForm) {
        // Validate amount input
        amountInput.addEventListener('input', () => {
            const amount = parseFloat(amountInput.value);
            if (isNaN(amount) || amount < 30 || amount > 5000) {
                amountInput.classList.add('is-invalid');
                document.getElementById('amount-feedback').textContent = 'Amount must be between $30 and $5000';
            } else {
                amountInput.classList.remove('is-invalid');
                amountInput.classList.add('is-valid');
                document.getElementById('amount-feedback').textContent = '';
            }
        });

        // Handle payment method selection
        paymentMethods.forEach(method => {
            method.addEventListener('click', () => {
                // Remove selected class from all methods
                paymentMethods.forEach(m => m.classList.remove('selected'));

                // Add selected class to clicked method
                method.classList.add('selected');

                // Update hidden input value
                paymentMethodInput.value = method.getAttribute('data-method');

                // Add haptic feedback for mobile
                if (window.navigator && window.navigator.vibrate) {
                    window.navigator.vibrate(50);
                }
            });
        });

        // Add touch feedback for mobile
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            paymentMethods.forEach(method => {
                method.addEventListener('touchstart', () => {
                    method.style.transform = 'scale(0.98)';
                });

                method.addEventListener('touchend', () => {
                    method.style.transform = 'scale(1)';
                });
            });
        }

        // Form submission validation
        depositForm.addEventListener('submit', (e) => {
            const amount = parseFloat(amountInput.value);
            const method = paymentMethodInput.value;

            if (isNaN(amount) || amount < 30 || amount > 5000 || !method) {
                e.preventDefault();

                if (isNaN(amount) || amount < 30 || amount > 5000) {
                    amountInput.classList.add('is-invalid');
                    document.getElementById('amount-feedback').textContent = 'Amount must be between $30 and $5000';
                    amountInput.focus();
                }

                if (!method) {
                    alert('Please select a payment method');
                }
            }
        });
    }
}

// Initialize withdrawal form
function initializeWithdrawalForm() {
    const amountInput = document.getElementById('amount');
    const walletAddressInput = document.getElementById('wallet_address');
    const withdrawalForm = document.getElementById('withdrawal-form');
    const availableBalance = document.getElementById('available-balance');

    if (amountInput && walletAddressInput && withdrawalForm && availableBalance) {
        const maxAmount = parseFloat(availableBalance.getAttribute('data-balance'));

        // Validate amount input
        amountInput.addEventListener('input', () => {
            const amount = parseFloat(amountInput.value);
            if (isNaN(amount) || amount <= 0) {
                amountInput.classList.add('is-invalid');
                document.getElementById('amount-feedback').textContent = 'Amount must be greater than zero';
            } else if (amount > maxAmount) {
                amountInput.classList.add('is-invalid');
                document.getElementById('amount-feedback').textContent = 'Amount exceeds available balance';
            } else {
                amountInput.classList.remove('is-invalid');
                amountInput.classList.add('is-valid');
                document.getElementById('amount-feedback').textContent = '';
            }
        });

        // Make all inputs more touch-friendly on mobile
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            const allInputs = withdrawalForm.querySelectorAll('input, select');
            allInputs.forEach(input => {
                input.style.fontSize = '16px';  // Prevents zoom on focus in iOS
                input.style.padding = '10px 14px';
            });
        }

        // Form submission validation
        withdrawalForm.addEventListener('submit', (e) => {
            const amount = parseFloat(amountInput.value);
            const wallet = walletAddressInput.value.trim();

            if (isNaN(amount) || amount <= 0 || amount > maxAmount || !wallet) {
                e.preventDefault();

                if (isNaN(amount) || amount <= 0) {
                    amountInput.classList.add('is-invalid');
                    document.getElementById('amount-feedback').textContent = 'Amount must be greater than zero';
                } else if (amount > maxAmount) {
                    amountInput.classList.add('is-invalid');
                    document.getElementById('amount-feedback').textContent = 'Amount exceeds available balance';
                }

                if (!wallet) {
                    walletAddressInput.classList.add('is-invalid');
                    document.getElementById('wallet-feedback').textContent = 'Wallet address is required';
                }
            }
        });
    }
}

// Initialize referral page
function initializeReferralPage() {
    const copyBtn = document.getElementById('copy-referral-link');
    const referralLink = document.getElementById('referral-link');

    if (copyBtn && referralLink) {
        copyBtn.addEventListener('click', () => {
            // Create temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = referralLink.textContent;
            textarea.setAttribute('readonly', '');
            textarea.style.position = 'absolute';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);

            // Select and copy the text
            textarea.select();
            document.execCommand('copy');

            // Remove the textarea
            document.body.removeChild(textarea);

            // Update button text temporarily
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.classList.add('btn-success');
            copyBtn.classList.remove('btn-primary');

            // Revert button text after 2 seconds
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-primary');
            }, 2000);
        });
    }
}

// Initialize profile page
function initializeProfilePage() {
    const profileTabs = document.querySelectorAll('.profile-tab');
    const profileTabContents = document.querySelectorAll('.profile-tab-content');

    if (profileTabs.length > 0 && profileTabContents.length > 0) {
        profileTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();

                // Remove active class from all tabs
                profileTabs.forEach(t => t.classList.remove('active'));

                // Hide all tab contents
                profileTabContents.forEach(content => content.style.display = 'none');

                // Add active class to clicked tab
                tab.classList.add('active');

                // Show corresponding tab content
                const targetId = tab.getAttribute('data-target');
                document.getElementById(targetId).style.display = 'block';
            });
        });
    }

    // Profile form validation
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();

            if (!username || !email) {
                e.preventDefault();
                alert('Username and email are required');
            }
        });
    }
}

// Initialize settings page
function initializeSettingsPage() {
    const passwordForm = document.getElementById('password-form');

    if (passwordForm) {
        passwordForm.addEventListener('submit', (e) => {
            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (!currentPassword || !newPassword || !confirmPassword) {
                e.preventDefault();
                alert('All password fields are required');
            } else if (newPassword !== confirmPassword) {
                e.preventDefault();
                alert('New passwords do not match');
            } else if (newPassword.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long');
            }
        });
    }

    // Add account deletion confirmation
    const deleteAccountForm = document.getElementById('delete-account-form');
    if (deleteAccountForm) {
        deleteAccountForm.addEventListener('submit', (e) => {
            const password = document.getElementById('delete_password').value;
            const confirmCheckbox = document.getElementById('confirm_delete');

            if (!password) {
                e.preventDefault();
                alert('Please enter your password to confirm account deletion');
                return;
            }

            if (!confirmCheckbox.checked) {
                e.preventDefault();
                alert('You must confirm that you understand the consequences of account deletion');
                return;
            }

            // Final confirmation
            const confirmed = confirm(
                'WARNING: You are about to permanently delete your account.\n\n' +
                'All your data including deposits, withdrawals, earnings, and personal information will be permanently removed.\n\n' +
                'This action CANNOT be undone.\n\n' +
                'Are you absolutely sure you want to proceed?'
            );

            if (!confirmed) {
                e.preventDefault();
            } else if (window.navigator && window.navigator.vibrate) {
                // Provide haptic feedback for this serious action
                window.navigator.vibrate([100, 50, 100]);
            }
        });
    }
}

// Initialize dashboard
function initializeDashboard() {
    // Add any dashboard-specific functionality
    // For example, updating real-time data or initializing charts
}

// Initialize admin interface
function initializeAdminInterface() {
    // Initialize admin tabs if present
    const adminTabs = document.querySelectorAll('.admin-tab');
    const adminTabContents = document.querySelectorAll('.admin-tab-content');

    if (adminTabs.length > 0 && adminTabContents.length > 0) {
        adminTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();

                // Remove active class from all tabs
                adminTabs.forEach(t => t.classList.remove('active'));

                // Hide all tab contents
                adminTabContents.forEach(content => content.style.display = 'none');

                // Add active class to clicked tab
                tab.classList.add('active');

                // Show corresponding tab content
                const targetId = tab.getAttribute('data-target');
                document.getElementById(targetId).style.display = 'block';
            });
        });
    }

    // Initialize action confirmation
    const confirmActions = document.querySelectorAll('[data-confirm]');

    if (confirmActions.length > 0) {
        confirmActions.forEach(action => {
            action.addEventListener('click', (e) => {
                const message = action.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }
} 