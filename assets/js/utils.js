// Utility functions for the dashboard

/**
 * Format date to Korean locale string
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format time to HH:MM format
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted time string
 */
function formatTime(date) {
    const d = new Date(date);
    return d.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

/**
 * Format date and time together
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted datetime string
 */
function formatDateTime(date) {
    const d = new Date(date);
    return d.toLocaleString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

/**
 * Get relative time string (e.g., "2시간 전")
 * @param {Date|string} date - Date to compare
 * @returns {string} Relative time string
 */
function getRelativeTime(date) {
    const now = new Date();
    const target = new Date(date);
    const diffMs = now - target;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    
    return formatDate(date);
}

/**
 * Parse report filename to extract metadata
 * @param {string} filename - Report filename
 * @returns {object} Parsed metadata
 */
function parseReportFilename(filename) {
    // Pattern: posco_analysis_type_YYYYMMDD_HHMMSS.html
    // or: posco_integrated_analysis_YYYYMMDD_HHMMSS.html
    const match = filename.match(/posco_(?:(integrated_)?analysis_)?(.+?)_(\d{8})_(\d{6})\.html$/);
    
    if (!match) {
        return {
            type: 'unknown',
            date: null,
            time: null,
            title: filename
        };
    }

    const [, isIntegrated, type, dateStr, timeStr] = match;
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const hour = timeStr.substring(0, 2);
    const minute = timeStr.substring(2, 4);
    const second = timeStr.substring(4, 6);

    const date = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);

    let reportType = type;
    let title = '';

    if (isIntegrated) {
        reportType = 'integrated';
        title = 'POSCO 뉴스 통합 분석 리포트';
    } else {
        switch (type) {
            case 'integrated':
                title = 'POSCO 뉴스 통합 분석 리포트';
                break;
            default:
                title = `POSCO ${type} 분석 리포트`;
        }
    }

    return {
        type: reportType,
        date: date,
        time: formatTime(date),
        title: title,
        dateStr: formatDate(date)
    };
}

/**
 * Get type display name in Korean
 * @param {string} type - Report type
 * @returns {string} Korean display name
 */
function getTypeDisplayName(type) {
    const typeNames = {
        'integrated': '통합 리포트'
    };
    return typeNames[type] || type;
}

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
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
 * Throttle function to limit function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local storage helper functions
 */
const Storage = {
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error writing to localStorage:', error);
            return false;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    }
};

/**
 * Theme management
 */
const Theme = {
    get() {
        return Storage.get('theme', 'light');
    },

    set(theme) {
        Storage.set('theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeIcon(theme);
    },

    toggle() {
        const current = this.get();
        const newTheme = current === 'light' ? 'dark' : 'light';
        this.set(newTheme);
        return newTheme;
    },

    updateThemeIcon(theme) {
        const icon = document.querySelector('#themeToggle i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    },

    init() {
        const savedTheme = this.get();
        this.set(savedTheme);
    }
};

/**
 * Favorites management
 */
const Favorites = {
    key: 'dashboard-favorites',

    get() {
        return Storage.get(this.key, []);
    },

    add(reportId) {
        const favorites = this.get();
        if (!favorites.includes(reportId)) {
            favorites.push(reportId);
            Storage.set(this.key, favorites);
        }
        return favorites;
    },

    remove(reportId) {
        const favorites = this.get();
        const index = favorites.indexOf(reportId);
        if (index > -1) {
            favorites.splice(index, 1);
            Storage.set(this.key, favorites);
        }
        return favorites;
    },

    toggle(reportId) {
        const favorites = this.get();
        if (favorites.includes(reportId)) {
            return this.remove(reportId);
        } else {
            return this.add(reportId);
        }
    },

    has(reportId) {
        return this.get().includes(reportId);
    }
};

/**
 * Recent reports management
 */
const RecentReports = {
    key: 'dashboard-recent',
    maxItems: 10,

    get() {
        return Storage.get(this.key, []);
    },

    add(reportId) {
        let recent = this.get();
        
        // Remove if already exists
        recent = recent.filter(id => id !== reportId);
        
        // Add to beginning
        recent.unshift(reportId);
        
        // Limit to maxItems
        if (recent.length > this.maxItems) {
            recent = recent.slice(0, this.maxItems);
        }
        
        Storage.set(this.key, recent);
        return recent;
    },

    clear() {
        Storage.remove(this.key);
    }
};

/**
 * API helper functions
 */
const API = {
    async fetchReports() {
        try {
            const response = await fetch('./reports_index.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching reports:', error);
            return { reports: [], lastUpdate: null };
        }
    },

    async fetchStatus() {
        try {
            const response = await fetch('./status.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching status:', error);
            return null;
        }
    }
};

/**
 * DOM helper functions
 */
const DOM = {
    /**
     * Create element with attributes and content
     */
    create(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else {
                element.setAttribute(key, value);
            }
        });
        
        if (content && typeof content === 'string') {
            element.textContent = content;
        }
        
        return element;
    },

    /**
     * Show loading spinner
     */
    showLoading(container) {
        container.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>데이터를 불러오는 중...</p>
            </div>
        `;
    },

    /**
     * Show error message
     */
    showError(container, message = '데이터를 불러올 수 없습니다.') {
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    },

    /**
     * Show empty state
     */
    showEmpty(container, message = '표시할 데이터가 없습니다.') {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>${message}</p>
            </div>
        `;
    }
};

/**
 * Export utilities for use in other scripts
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        formatTime,
        formatDateTime,
        getRelativeTime,
        parseReportFilename,
        getTypeDisplayName,
        debounce,
        throttle,
        Storage,
        Theme,
        Favorites,
        RecentReports,
        API,
        DOM
    };
}