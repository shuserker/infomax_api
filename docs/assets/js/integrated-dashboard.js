// Integrated Dashboard - 통합 리포트 전용 대시보드 업데이트

class IntegratedDashboard {
    constructor() {
        this.reports = [];
        this.init();
    }

    async init() {
        await this.loadReports();
        this.updateStatusDisplay();
        this.updateReportsList();
        this.startAutoRefresh();
    }

    async loadReports() {
        try {
            const response = await fetch('docs/reports_index.json');
            const data = await response.json();
            // 통합 리포트만 필터링
            this.reports = (data.reports || []).filter(r => r.type === 'integrated');
            console.log('통합 리포트 로드됨:', this.reports.length, '개');
            console.log('로드된 리포트:', this.reports);
        } catch (error) {
            console.error('리포트 로드 실패:', error);
            // 개발 중에는 빈 배열 대신 테스트 데이터 사용
            this.reports = [];
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
        if (!container) return;

        if (this.reports.length === 0) {
            container.innerHTML = `
                <div class="no-reports">
                    <i class="fas fa-chart-pie"></i>
                    <h3>통합 리포트가 없습니다</h3>
                    <p>새로운 통합 리포트가 생성되면 여기에 표시됩니다.</p>
                </div>
            `;
            return;
        }

        const reportsHTML = this.reports.map(report => this.createReportCard(report)).join('');
        container.innerHTML = reportsHTML;
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

    startAutoRefresh() {
        // 5분마다 자동 새로고침
        setInterval(async () => {
            await this.loadReports();
            this.updateStatusDisplay();
            this.updateReportsList();
        }, 5 * 60 * 1000);
    }

    // 수동 새로고침
    async refresh() {
        await this.loadReports();
        this.updateStatusDisplay();
        this.updateReportsList();
        
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
    }
}

// 전역에서 사용할 수 있도록 export
window.IntegratedDashboard = IntegratedDashboard;

// DOM 로드 완료 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.integratedDashboard = new IntegratedDashboard();
});