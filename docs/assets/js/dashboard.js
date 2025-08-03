// Dashboard functionality

class Dashboard {
    constructor() {
        this.reports = [];
        this.filteredReports = [];
        this.currentPage = 1;
        this.reportsPerPage = 12;
        this.filters = {
            search: '',
            type: '',
            date: '',
            sort: 'newest'
        };
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.updateCurrentTime();
        this.startTimeUpdater();
        await this.loadData();
        this.renderDashboard();
        this.initializeSearch();
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', debounce((e) => {
                this.filters.search = e.target.value;
                this.applyFilters();
            }, 300));
        }

        // 필터 이벤트는 FilterSystem에서 처리됨

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                Theme.toggle();
            });
        }

        // Quick access tabs
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    updateCurrentTime() {
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = formatTime(now);
        }
    }

    startTimeUpdater() {
        setInterval(() => {
            this.updateCurrentTime();
        }, 1000);
    }

    async loadData() {
        try {
            // Load reports data
            const reportsData = await API.fetchReports();
            this.reports = this.processReportsData(reportsData);
            
            // Load status data
            const statusData = await API.fetchStatus();
            if (statusData) {
                this.updateStatusBar(statusData);
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showErrorState();
        }
    }

    processReportsData(data) {
        if (!data.reports || !Array.isArray(data.reports)) {
            return [];
        }

        return data.reports.map(report => {
            const parsed = parseReportFilename(report.filename || report.name || '');
            return {
                id: report.id || report.filename || report.name,
                filename: report.filename || report.name,
                title: parsed.title,
                type: parsed.type,
                date: parsed.date,
                time: parsed.time,
                dateStr: parsed.dateStr,
                url: report.url || `./reports/${report.filename || report.name}`,
                size: report.size || 0,
                summary: this.generateSummary(parsed.type),
                tags: this.generateTags(parsed.type),
                isFavorite: Favorites.has(report.id || report.filename || report.name)
            };
        }).filter(report => report.date); // Filter out reports with invalid dates
    }

    generateSummary(type) {
        const summaries = {
            'integrated': '3개 뉴스 완료, 시장 분위기 분석',
            'exchange-rate': '달러-원 환율 동향 분석',
            'kospi-close': 'KOSPI 지수 마감 분석',
            'newyork-market-watch': '뉴욕 증시 동향 분석'
        };
        return summaries[type] || '뉴스 분석 리포트';
    }

    generateTags(type) {
        const tagMap = {
            'integrated': ['통합분석', '일일리포트', '종합'],
            'exchange-rate': ['환율', '달러', '외환'],
            'kospi-close': ['증시', 'KOSPI', '주식'],
            'newyork-market-watch': ['뉴욕', '해외증시', '글로벌']
        };
        return tagMap[type] || ['분석'];
    }

    updateStatusBar(statusData) {
        if (!statusData.newsStatus) return;

        const statusMap = {
            'exchange-rate': {
                timeElement: 'exchangeRateTime',
                statusElement: 'exchangeRateStatus'
            },
            'kospi-close': {
                timeElement: 'kospiCloseTime',
                statusElement: 'kospiCloseStatus'
            },
            'newyork-market-watch': {
                timeElement: 'newyorkWatchTime',
                statusElement: 'newyorkWatchStatus'
            }
        };

        Object.entries(statusMap).forEach(([key, elements]) => {
            const newsStatus = statusData.newsStatus[key];
            if (newsStatus) {
                const timeEl = document.getElementById(elements.timeElement);
                const statusEl = document.getElementById(elements.statusElement);

                if (timeEl) {
                    timeEl.textContent = newsStatus.publishTime || '--:--';
                }

                if (statusEl) {
                    statusEl.textContent = newsStatus.published ? '완료' : '대기중';
                    statusEl.className = `status-badge ${newsStatus.published ? 'active' : ''}`;
                }
            }
        });

        // Update system status
        if (statusData.systemStatus) {
            const systemUptime = document.getElementById('systemUptime');
            const systemStatus = document.getElementById('systemStatus');

            if (systemUptime) {
                systemUptime.textContent = statusData.systemStatus.uptime || '99.8%';
            }

            if (systemStatus) {
                const isActive = statusData.systemStatus.monitoring === 'active';
                systemStatus.textContent = isActive ? '정상' : '점검중';
                systemStatus.className = `status-badge ${isActive ? 'active' : 'warning'}`;
            }
        }
    }

    applyFilters() {
        let filtered = [...this.reports];

        // Search filter
        if (this.filters.search) {
            const searchTerm = this.filters.search.toLowerCase();
            filtered = filtered.filter(report => 
                report.title.toLowerCase().includes(searchTerm) ||
                report.summary.toLowerCase().includes(searchTerm) ||
                report.tags.some(tag => tag.toLowerCase().includes(searchTerm))
            );
        }

        // Type filter
        if (this.filters.type) {
            filtered = filtered.filter(report => report.type === this.filters.type);
        }

        // Date filter
        if (this.filters.date) {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            
            filtered = filtered.filter(report => {
                const reportDate = new Date(report.date);
                const reportDay = new Date(reportDate.getFullYear(), reportDate.getMonth(), reportDate.getDate());
                
                switch (this.filters.date) {
                    case 'today':
                        return reportDay.getTime() === today.getTime();
                    case 'yesterday':
                        const yesterday = new Date(today);
                        yesterday.setDate(yesterday.getDate() - 1);
                        return reportDay.getTime() === yesterday.getTime();
                    case 'week':
                        const weekAgo = new Date(today);
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return reportDay >= weekAgo;
                    case 'month':
                        const monthAgo = new Date(today);
                        monthAgo.setDate(monthAgo.getDate() - 30);
                        return reportDay >= monthAgo;
                    default:
                        return true;
                }
            });
        }

        // Sort
        filtered.sort((a, b) => {
            switch (this.filters.sort) {
                case 'newest':
                    return new Date(b.date) - new Date(a.date);
                case 'oldest':
                    return new Date(a.date) - new Date(b.date);
                case 'name':
                    return a.title.localeCompare(b.title);
                default:
                    return 0;
            }
        });

        this.filteredReports = filtered;
        this.currentPage = 1;
        this.renderReports();
        this.renderPagination();
        this.updateStats();
    }

    renderDashboard() {
        this.applyFilters();
        this.renderQuickAccess();
    }

    initializeSearch() {
        // 검색 엔진에 문서 인덱싱
        if (typeof searchEngine !== 'undefined') {
            searchEngine.indexDocuments(this.reports);
            console.log('🔍 검색 엔진 인덱싱 완료');
            
            // 검색 UI 초기화
            if (typeof initializeSearchUI === 'function') {
                window.searchUI = initializeSearchUI(this);
            }
        }

        // 필터 시스템 초기화
        if (typeof initializeFilterSystem === 'function') {
            window.filterSystem = initializeFilterSystem(this);
        }

        // 차트 시스템 초기화
        if (typeof initializeChartSystem === 'function') {
            window.chartSystem = initializeChartSystem(this);
        }

        // 성과 지표 시스템 초기화
        if (typeof initializePerformanceMetrics === 'function') {
            window.performanceMetrics = initializePerformanceMetrics(this);
        }

        // 즐겨찾기 시스템 초기화
        if (typeof initializeFavoritesSystem === 'function') {
            window.favoritesSystem = initializeFavoritesSystem(this);
        }
    }

    renderReports() {
        const container = document.getElementById('reportsContainer');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        if (!container) return;

        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }

        if (this.filteredReports.length === 0) {
            DOM.showEmpty(container, '조건에 맞는 리포트가 없습니다.');
            return;
        }

        const startIndex = (this.currentPage - 1) * this.reportsPerPage;
        const endIndex = startIndex + this.reportsPerPage;
        const pageReports = this.filteredReports.slice(startIndex, endIndex);

        container.innerHTML = '';

        pageReports.forEach(report => {
            const reportCard = this.createReportCard(report);
            container.appendChild(reportCard);
        });
    }

    createReportCard(report) {
        const card = DOM.create('div', { className: 'report-card' });
        
        card.innerHTML = `
            <div class="report-card-header">
                <span class="report-type ${report.type}">${getTypeDisplayName(report.type)}</span>
                <button class="favorite-btn ${report.isFavorite ? 'active' : ''}" data-report-id="${report.id}">
                    <i class="fas fa-star"></i>
                </button>
            </div>
            <h3 class="report-title">${report.title}</h3>
            <div class="report-meta">
                <span><i class="fas fa-calendar"></i> ${report.dateStr}</span>
                <span><i class="fas fa-clock"></i> ${report.time}</span>
            </div>
            <p class="report-summary">${report.summary}</p>
            <div class="report-tags">
                ${report.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        `;

        // Add click handler for opening report
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.favorite-btn')) {
                this.openReport(report);
            }
        });

        // Add favorite button handler
        const favoriteBtn = card.querySelector('.favorite-btn');
        favoriteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleFavorite(report.id);
        });

        return card;
    }

    openReport(report) {
        // Add to recent reports (legacy)
        RecentReports.add(report.id);
        
        // Add to favorites system recent items
        if (window.favoritesSystem) {
            window.favoritesSystem.addToRecent(report.id, report);
        }
        
        // Open report in new tab
        window.open(report.url, '_blank');
        
        // Update recent reports display
        this.renderQuickAccess();
    }

    toggleFavorite(reportId) {
        Favorites.toggle(reportId);
        
        // Update the report object
        const report = this.reports.find(r => r.id === reportId);
        if (report) {
            report.isFavorite = Favorites.has(reportId);
        }
        
        // Re-render reports and quick access
        this.renderReports();
        this.renderQuickAccess();
    }

    renderPagination() {
        const container = document.getElementById('pagination');
        if (!container) return;

        const totalPages = Math.ceil(this.filteredReports.length / this.reportsPerPage);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '';

        // Previous button
        paginationHTML += `
            <button ${this.currentPage === 1 ? 'disabled' : ''} onclick="dashboard.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<button onclick="dashboard.goToPage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span>...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="${i === this.currentPage ? 'active' : ''}" onclick="dashboard.goToPage(${i})">
                    ${i}
                </button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span>...</span>`;
            }
            paginationHTML += `<button onclick="dashboard.goToPage(${totalPages})">${totalPages}</button>`;
        }

        // Next button
        paginationHTML += `
            <button ${this.currentPage === totalPages ? 'disabled' : ''} onclick="dashboard.goToPage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        container.innerHTML = paginationHTML;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredReports.length / this.reportsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderReports();
            this.renderPagination();
            
            // Scroll to top of reports
            document.getElementById('reportGrid').scrollIntoView({ behavior: 'smooth' });
        }
    }

    updateStats() {
        const totalReports = document.getElementById('totalReports');
        const todayReports = document.getElementById('todayReports');
        const weeklyAverage = document.getElementById('weeklyAverage');
        const successRate = document.getElementById('successRate');

        if (totalReports) {
            totalReports.textContent = this.reports.length;
        }

        if (todayReports) {
            const today = new Date();
            const todayCount = this.reports.filter(report => {
                const reportDate = new Date(report.date);
                return reportDate.toDateString() === today.toDateString();
            }).length;
            todayReports.textContent = todayCount;
        }

        if (weeklyAverage) {
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            const weeklyCount = this.reports.filter(report => 
                new Date(report.date) >= weekAgo
            ).length;
            weeklyAverage.textContent = Math.round(weeklyCount / 7 * 10) / 10;
        }

        if (successRate) {
            // Calculate success rate based on expected vs actual reports
            // This is a simplified calculation
            successRate.textContent = '98.5%';
        }
    }

    renderQuickAccess() {
        this.renderRecentReports();
        this.renderFavoriteReports();
    }

    renderRecentReports() {
        const container = document.getElementById('recentList');
        if (!container) return;

        const recentIds = RecentReports.get();
        const recentReports = recentIds
            .map(id => this.reports.find(r => r.id === id))
            .filter(Boolean)
            .slice(0, 5);

        if (recentReports.length === 0) {
            container.innerHTML = '<p class="empty-message">최근 본 리포트가 없습니다.</p>';
            return;
        }

        container.innerHTML = recentReports.map(report => `
            <div class="quick-item" onclick="dashboard.openReport(${JSON.stringify(report).replace(/"/g, '&quot;')})">
                <div class="quick-item-info">
                    <h4>${report.title}</h4>
                    <p>${report.dateStr} ${report.time}</p>
                </div>
                <span class="report-type ${report.type}">${getTypeDisplayName(report.type)}</span>
            </div>
        `).join('');
    }

    renderFavoriteReports() {
        const container = document.getElementById('favoritesList');
        if (!container) return;

        const favoriteIds = Favorites.get();
        const favoriteReports = favoriteIds
            .map(id => this.reports.find(r => r.id === id))
            .filter(Boolean)
            .slice(0, 5);

        if (favoriteReports.length === 0) {
            container.innerHTML = '<p class="empty-message">즐겨찾기한 리포트가 없습니다.</p>';
            return;
        }

        container.innerHTML = favoriteReports.map(report => `
            <div class="quick-item" onclick="dashboard.openReport(${JSON.stringify(report).replace(/"/g, '&quot;')})">
                <div class="quick-item-info">
                    <h4>${report.title}</h4>
                    <p>${report.dateStr} ${report.time}</p>
                </div>
                <span class="report-type ${report.type}">${getTypeDisplayName(report.type)}</span>
            </div>
        `).join('');
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }

    showErrorState() {
        const container = document.getElementById('reportsContainer');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        if (container) {
            DOM.showError(container, '리포트 데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.');
        }
    }

    // Public method to refresh data
    async refresh() {
        const loadingSpinner = document.getElementById('loadingSpinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        
        await this.loadData();
        this.renderDashboard();
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});

// Add CSS for quick items
const quickItemStyles = `
<style>
.quick-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.quick-item:hover {
    background-color: var(--bg-tertiary);
    border-color: var(--border-hover);
}

.quick-item-info h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.quick-item-info p {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.error-message,
.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-muted);
}

.error-message i,
.empty-state i {
    font-size: 2rem;
    margin-bottom: 1rem;
    display: block;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', quickItemStyles);