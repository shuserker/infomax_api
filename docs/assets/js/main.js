// Main application initialization and global event handlers

document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced theme system
    if (typeof initializeThemeSystem === 'function') {
        initializeThemeSystem();
    } else {
        // Fallback to basic theme
        Theme.init();
    }
    
    // Initialize global event listeners
    initializeGlobalEvents();
    
    // Start periodic data refresh
    startPeriodicRefresh();
    
    // Initialize service worker for offline support (if available)
    initializeServiceWorker();
});

/**
 * Initialize global event listeners
 */
function initializeGlobalEvents() {
    // Handle keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Handle window resize for responsive adjustments
    window.addEventListener('resize', throttle(handleWindowResize, 250));
    
    // Handle visibility change for pausing/resuming updates
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Handle online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K: Focus search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Ctrl/Cmd + D: Toggle dark mode
    if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
        event.preventDefault();
        if (window.themeSystem) {
            themeSystem.toggleTheme();
        } else {
            Theme.toggle();
        }
    }
    
    // Escape: Clear search
    if (event.key === 'Escape') {
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput === document.activeElement) {
            searchInput.value = '';
            searchInput.blur();
            if (window.dashboard) {
                dashboard.filters.search = '';
                dashboard.applyFilters();
            }
        }
    }
    
    // F5 or Ctrl/Cmd + R: Refresh data
    if (event.key === 'F5' || ((event.ctrlKey || event.metaKey) && event.key === 'r')) {
        if (window.dashboard) {
            event.preventDefault();
            dashboard.refresh();
        }
    }
}

/**
 * Handle window resize
 */
function handleWindowResize() {
    // Adjust layout for mobile/desktop
    const isMobile = window.innerWidth < 768;
    document.body.classList.toggle('mobile-layout', isMobile);
    
    // Recalculate any dynamic layouts if needed
    if (window.dashboard) {
        // Force re-render of responsive elements
        dashboard.renderReports();
    }
}

/**
 * Handle visibility change (tab focus/blur)
 */
function handleVisibilityChange() {
    if (document.hidden) {
        // Page is hidden, pause updates
        pausePeriodicRefresh();
    } else {
        // Page is visible, resume updates and refresh data
        resumePeriodicRefresh();
        if (window.dashboard) {
            dashboard.refresh();
        }
    }
}

/**
 * Handle online status
 */
function handleOnlineStatus() {
    showNotification('연결이 복원되었습니다.', 'success');
    if (window.dashboard) {
        dashboard.refresh();
    }
}

/**
 * Handle offline status
 */
function handleOfflineStatus() {
    showNotification('인터넷 연결이 끊어졌습니다. 캐시된 데이터를 표시합니다.', 'warning');
}

/**
 * Periodic data refresh
 */
let refreshInterval;
const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

function startPeriodicRefresh() {
    refreshInterval = setInterval(() => {
        if (!document.hidden && window.dashboard) {
            dashboard.refresh();
        }
    }, REFRESH_INTERVAL);
}

function pausePeriodicRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function resumePeriodicRefresh() {
    if (!refreshInterval) {
        startPeriodicRefresh();
    }
}

/**
 * Service Worker initialization for offline support
 */
function initializeServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('./sw.js')
            .then(registration => {
                console.log('Service Worker registered successfully:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = DOM.create('div', {
        className: `notification notification-${type}`
    });
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Add close handler
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Error handling
 */
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showNotification('오류가 발생했습니다. 페이지를 새로고침해주세요.', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('데이터 로딩 중 오류가 발생했습니다.', 'error');
});

/**
 * Utility functions for global use
 */
window.utils = {
    showNotification,
    formatDate,
    formatTime,
    formatDateTime,
    getRelativeTime,
    parseReportFilename,
    getTypeDisplayName
};

// Add notification styles
const notificationStyles = `
<style>
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    min-width: 300px;
    max-width: 500px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    box-shadow: var(--shadow-lg);
    transform: translateX(100%);
    transition: transform 0.3s ease;
}

.notification.show {
    transform: translateX(0);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
}

.notification-content i:first-child {
    font-size: 1.25rem;
}

.notification-content span {
    flex: 1;
    color: var(--text-primary);
    font-size: 0.875rem;
}

.notification-close {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.25rem;
    transition: all 0.2s ease;
}

.notification-close:hover {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
}

.notification-success {
    border-left: 4px solid var(--success-color);
}

.notification-success .notification-content i:first-child {
    color: var(--success-color);
}

.notification-error {
    border-left: 4px solid var(--error-color);
}

.notification-error .notification-content i:first-child {
    color: var(--error-color);
}

.notification-warning {
    border-left: 4px solid var(--warning-color);
}

.notification-warning .notification-content i:first-child {
    color: var(--warning-color);
}

.notification-info {
    border-left: 4px solid var(--primary-color);
}

.notification-info .notification-content i:first-child {
    color: var(--primary-color);
}

@media (max-width: 480px) {
    .notification {
        left: 10px;
        right: 10px;
        min-width: auto;
        max-width: none;
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);