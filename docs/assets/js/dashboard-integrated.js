// Integrated Dashboard - 통합 리포트 전용 대시보드

class IntegratedDashboard {
    constructor() {
        this.reports = [];
        this.filteredReports = [];
        this.currentPage = 1;
        this.reportsPerPage = 12;
        this.filters = {
            search: '',
            type: 'integrated', // 통합 리포트만
            date: '',
            sort: 'newest'
        };
        
        this.init();
    }

    async init() {
        console.log('통합 대시보드 초기화 시작...');
        this.setupEventListeners();
        this.updateCurrentTime();
        this.startTimeUpdater();
        await this.loadData();
        this.renderDashboard();
        this.initializeSearch();
        console.log('통합 대시보드 초기화 완료');
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

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                if (typeof Theme !== 'undefined') {
                    Theme.toggle();
                }
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refresh();
            });
        }
    }

    async loadData() {
        try {
            console.log('리포트 데이터 로드 중...');
            const response = await fetch('docs/reports_index.json');
            const data = await response.json();
            
            // 통합 리포트만 필터링
            this.reports = (data.reports || []).filter(r => r.type === 'integrated');
            this.filteredReports = [...this.reports];
            
            console.log(`통합 리포트 ${this.reports.length}개 로드됨`);
            
            // 최신순 정렬
            this.reports.sort((a, b) => new Date(b.createdAt || b.date) - new Date(a.createdAt || a.date));
            
        } catch (error) {
            console.error('리포트 로드 실패:', error);
            this.reports = [];
            this.filteredReports = [];
        }
    }

    renderDashboard() {
        this.updateStatusDisplay();
        this.updateReportsList();
        this.updatePagination();
        
        // 통합 차트 시스템 초기화
        if (typeof IntegratedCharts === 'function') {
            if (window.integratedCharts) {
                window.integratedCharts.updateAllCharts();
            } else {
                window.integratedCharts = new IntegratedCharts(this);
                // 차트 생성
                setTimeout(() => {
                    window.integratedCharts.createTrendChart('trendChart');
                    window.integratedCharts.createStatusChart('statusChart');
                    window.integratedCharts.createTimePatternChart('timePatternChart');
                }, 100);
            }
        }
    }

    updateStatusDisplay() {
        const latestReport = this.reports.length > 0 ? this.reports[0] : null;

        // 통합 리포트 상태
        this.updateElement('integratedReportTime', latestReport?.time || '--:--');
        this.updateElement('integratedReportStatus', latestReport ? '최신' : '대기중', 
                          latestReport ? 'status-badge active' : 'status-badge');

        // 시스템 상태
        this.updateElement('systemStatusTime', '통합 리포트');
        this.updateElement('systemStatus', '활성', 'status-badge active');

        // 총 리포트 수
        this.updateElement('totalReportsCount', this.reports.length.toString());
        this.updateElement('reportsCountStatus', '통합', 'status-badge');

        // 최신 리포트 시간
        if (latestReport) {
            const reportDate = new Date(latestReport.createdAt || latestReport.date);
            const timeStr = reportDate.toLocaleTimeString('ko-KR', {
                hour: '2-digit',
                minute: '2-digit'
            });
            this.updateElement('latestReportTime', timeStr);
            this.updateElement('latestReportStatus', '생성됨', 'status-badge active');
        } else {
            this.updateElement('latestReportTime', '--:--');
            this.updateElement('latestReportStatus', '대기중', 'status-badge');
        }

        console.log('상태 표시 업데이트 완료:', {
            totalReports: this.reports.length,
            latestReport: latestReport?.filename || 'none'
        });
    }

    updateElement(id, text, className = null) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
            if (className) {
                element.className = className;
            }
        }
    }

    updateReportsList() {
        const container = document.getElementById('reportsContainer');
        if (!container) {
            console.warn('reportsContainer 요소를 찾을 수 없습니다');
            return;
        }

        if (this.filteredReports.length === 0) {
            container.innerHTML = `
                <div class="no-reports">
                    <i class="fas fa-chart-pie"></i>
                    <h3>통합 리포트가 없습니다</h3>
                    <p>새로운 통합 리포트가 생성되면 여기에 표시됩니다.</p>
                </div>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.reportsPerPage;
        const endIndex = startIndex + this.reportsPerPage;
        const pageReports = this.filteredReports.slice(startIndex, endIndex);

        const reportsHTML = pageReports.map(report => this.createReportCard(report)).join('');
        container.innerHTML = reportsHTML;

        console.log(`리포트 목록 업데이트: ${pageReports.length}개 표시`);
    }

    createReportCard(report) {
        const reportDate = new Date(report.createdAt || report.date);
        const formattedDate = reportDate.toLocaleDateString('ko-KR');
        const formattedTime = reportDate.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const insights = report.summary?.keyInsights || ['환율 분석', '증시 동향', '뉴욕 시장'];
        const insightsHTML = insights.slice(0, 3).map(insight => 
            `<span class="insight-tag">${insight}</span>`
        ).join('');

        return `
            <div class="report-card integrated" data-report-id="${report.id}">
                <div class="report-header">
                    <div class="report-type integrated">
                        <i class="fas fa-chart-pie"></i>
                        통합 리포트
                    </div>
                    <div class="report-date">
                        <i class="fas fa-calendar"></i>
                        ${formattedDate}
                    </div>
                </div>
                
                <div class="report-content">
                    <h3 class="report-title">${report.title || 'POSCO 뉴스 통합 분석 리포트'}</h3>
                    <p class="report-summary">
                        ${report.summary?.newsCount || 3}개 뉴스 통합 분석 완료 
                        (${report.summary?.marketSentiment || '긍정'} 전망)
                    </p>
                    
                    <div class="report-insights">
                        ${insightsHTML}
                    </div>
                </div>
                
                <div class="report-footer">
                    <div class="report-meta">
                        <span class="report-time">
                            <i class="fas fa-clock"></i>
                            ${formattedTime}
                        </span>
                        <span class="report-size">
                            <i class="fas fa-file-alt"></i>
                            ${this.formatFileSize(report.size || 0)}
                        </span>
                    </div>
                    
                    <div class="report-actions">
                        <a href="${report.url}" target="_blank" class="btn-primary">
                            <i class="fas fa-external-link-alt"></i>
                            리포트 보기
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredReports.length / this.reportsPerPage);
        const paginationContainer = document.getElementById('pagination');
        
        if (!paginationContainer || totalPages <= 1) {
            if (paginationContainer) paginationContainer.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // 이전 버튼
        if (this.currentPage > 1) {
            paginationHTML += `<button class="pagination-btn" onclick="window.dashboard.goToPage(${this.currentPage - 1})">이전</button>`;
        }

        // 페이지 번호
        for (let i = 1; i <= totalPages; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            paginationHTML += `<button class="pagination-btn ${activeClass}" onclick="window.dashboard.goToPage(${i})">${i}</button>`;
        }

        // 다음 버튼
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="pagination-btn" onclick="window.dashboard.goToPage(${this.currentPage + 1})">다음</button>`;
        }

        paginationContainer.innerHTML = paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.updateReportsList();
        this.updatePagination();
    }

    applyFilters() {
        this.filteredReports = this.reports.filter(report => {
            // 검색 필터
            if (this.filters.search) {
                const searchTerm = this.filters.search.toLowerCase();
                const searchableText = [
                    report.title,
                    report.summary?.marketSentiment,
                    ...(report.summary?.keyInsights || [])
                ].join(' ').toLowerCase();
                
                if (!searchableText.includes(searchTerm)) {
                    return false;
                }
            }

            // 날짜 필터
            if (this.filters.date) {
                if (report.date !== this.filters.date) {
                    return false;
                }
            }

            return true;
        });

        // 정렬
        this.sortReports();
        
        this.currentPage = 1;
        this.updateReportsList();
        this.updatePagination();
    }

    sortReports() {
        this.filteredReports.sort((a, b) => {
            const dateA = new Date(a.createdAt || a.date);
            const dateB = new Date(b.createdAt || b.date);
            
            switch (this.filters.sort) {
                case 'newest':
                    return dateB - dateA;
                case 'oldest':
                    return dateA - dateB;
                default:
                    return dateB - dateA;
            }
        });
    }

    updateCurrentTime() {
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString('ko-KR');
        }
    }

    startTimeUpdater() {
        this.updateCurrentTime();
        setInterval(() => {
            this.updateCurrentTime();
        }, 1000);

        // 5분마다 데이터 새로고침
        setInterval(async () => {
            await this.loadData();
            this.renderDashboard();
        }, 5 * 60 * 1000);
    }

    initializeSearch() {
        // 검색 기능은 이미 setupEventListeners에서 설정됨
        console.log('검색 시스템 초기화 완료');
    }

    async refresh() {
        console.log('수동 새로고침 시작...');
        await this.loadData();
        this.renderDashboard();
        
        // 새로고침 피드백
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 새로고침 중...';
            refreshBtn.disabled = true;
            
            setTimeout(() => {
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
            }, 1000);
        }
        
        console.log('수동 새로고침 완료');
    }
}

// 유틸리티 함수
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

// 전역에서 사용할 수 있도록 export
window.IntegratedDashboard = IntegratedDashboard;

// DOM 로드 완료 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM 로드 완료, 통합 대시보드 초기화...');
    window.dashboard = new IntegratedDashboard();
});