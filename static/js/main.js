/* ProjectFlow - Main JavaScript */

// Theme toggle function (global, called from onclick)
function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('pf-theme', next);

    var icon = document.getElementById('theme-icon');
    if (icon) {
        icon.textContent = next === 'light' ? 'dark_mode' : 'light_mode';
    }

    // Sync to server
    fetch('/accounts/theme/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({theme: next}),
    }).catch(function() {});
}

function getCsrfToken() {
    var cookie = document.cookie.split(';').find(function(c) {
        return c.trim().startsWith('csrftoken=');
    });
    return cookie ? cookie.split('=')[1] : '';
}

document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.add('show');
            overlay.classList.add('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar?.classList.remove('show');
            overlay.classList.remove('show');
            // Close dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(function(el) {
                el.classList.remove('show');
            });
            document.querySelectorAll('.user-dropdown.show').forEach(function(el) {
                el.classList.remove('show');
            });
        });
    }

    // User dropdown toggle
    const userMenuToggle = document.getElementById('user-menu-toggle');
    const userDropdown = document.getElementById('user-dropdown');

    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
    }

    // Dropdown toggles
    document.querySelectorAll('[data-dropdown-toggle]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const target = document.getElementById(button.getAttribute('data-dropdown-toggle'));
            if (target) {
                // Close other open dropdowns first
                document.querySelectorAll('.dropdown-menu.show').forEach(function(el) {
                    if (el !== target) {
                        el.classList.remove('show');
                    }
                });
                target.classList.toggle('show');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[data-dropdown-toggle]')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(el) {
                el.classList.remove('show');
            });
        }
    });

    // Modal functionality
    document.querySelectorAll('[data-modal-open]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = button.getAttribute('data-modal-open');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                overlay?.classList.add('show');
            }
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(function(button) {
        button.addEventListener('click', function() {
            const modal = button.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
                overlay?.classList.remove('show');
            }
        });
    });

    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(function(modal) {
                modal.classList.remove('show');
            });
            overlay?.classList.remove('show');
            document.querySelectorAll('.dropdown-menu.show').forEach(function(el) {
                el.classList.remove('show');
            });
            document.querySelectorAll('.user-dropdown.show').forEach(function(el) {
                el.classList.remove('show');
            });
        }
    });

    // Auto-dismiss toasts/messages after 5 seconds
    const messages = document.querySelectorAll('.message, .toast');
    messages.forEach(function(message) {
        let dismissed = false;
        function dismiss() {
            if (dismissed) {
                return;
            }
            dismissed = true;
            message.classList.add('is-hiding');
            setTimeout(function() {
                message.remove();
            }, 300);
        }
        const closeBtn = message.querySelector('.message-close, .toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', dismiss);
        }
        setTimeout(dismiss, 5000);
    });

    // Progress bar animation
    document.querySelectorAll('.progress-bar-fill').forEach(function(bar) {
        var percent = bar.getAttribute('data-percent') || 0;
        bar.style.width = percent + '%';
    });

    // Notification badge polling
    var badge = document.getElementById('notification-badge');
    if (badge) {
        function updateNotificationBadge() {
            fetch('/notifications/unread-count/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.unread_count > 0) {
                        badge.textContent = data.unread_count;
                        badge.style.display = 'flex';
                    } else {
                        badge.style.display = 'none';
                    }
                })
                .catch(function() {});
        }
        updateNotificationBadge();
        setInterval(updateNotificationBadge, 60000);
    }
});
