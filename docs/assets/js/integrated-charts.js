// Integrated Report Charts - 통합 리포트 전용 차트 시스템

class IntegratedCharts {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.colorScheme = {
            primary: '#2563eb',
            success: '#059669',
            warning: '#d97706',
            danger: '#dc2626',
            info: '#0891b2',
            secondary: '#6b7280'
        };
        this.charts = {};
    }

    // 통합 리포트 트렌드 차트
    createTrendChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const data = this.generateTrendData();

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: '통합 리포트',
                        data: data.integrated,
                        borderColor: this.colorScheme.primary,
                        backgroundColor: this.colorScheme.primary + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: this.colorScheme.primary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '통합 리포트 생성 추이',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: '리포트 수'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '날짜'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        this.charts.trend = chart;
        return chart;
    }

    // 통합 리포트 상태 분포 차트
    createStatusChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const data = this.generateStatusData();

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        this.colorScheme.success,
                        this.colorScheme.warning,
                        this.colorScheme.danger
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '리포트 상태 분포',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        this.charts.status = chart;
        return chart;
    }

    // 시간대별 리포트 생성 패턴 차트
    createTimePatternChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const data = this.generateTimePatternData();

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '리포트 생성 수',
                    data: data.values,
                    backgroundColor: this.colorScheme.info + '80',
                    borderColor: this.colorScheme.info,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '시간대별 리포트 생성 패턴',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });

        this.charts.timePattern = chart;
        return chart;
    }

    // 트렌드 데이터 생성
    generateTrendData() {
        const labels = [];
        const integrated = [];
        const reports = this.dashboard.reports || [];

        // 최근 7일 데이터
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            labels.push(date.toLocaleDateString('ko-KR', { 
                month: 'short', 
                day: 'numeric' 
            }));
            
            const dayReports = reports.filter(r => r.date === dateStr && r.type === 'integrated');
            integrated.push(dayReports.length);
        }

        return { labels, integrated };
    }

    // 상태 데이터 생성
    generateStatusData() {
        const reports = this.dashboard.reports || [];
        const integratedReports = reports.filter(r => r.type === 'integrated');
        
        const statusCounts = {
            success: 0,
            warning: 0,
            error: 0
        };

        integratedReports.forEach(report => {
            const completionRate = parseFloat(report.summary?.completionRate || '100%');
            if (completionRate >= 90) {
                statusCounts.success++;
            } else if (completionRate >= 70) {
                statusCounts.warning++;
            } else {
                statusCounts.error++;
            }
        });

        return {
            labels: ['정상', '주의', '오류'],
            values: Object.values(statusCounts)
        };
    }

    // 시간 패턴 데이터 생성
    generateTimePatternData() {
        const reports = this.dashboard.reports || [];
        const integratedReports = reports.filter(r => r.type === 'integrated');
        
        const hourCounts = new Array(24).fill(0);
        
        integratedReports.forEach(report => {
            if (report.time) {
                const hour = parseInt(report.time.split(':')[0]);
                if (hour >= 0 && hour < 24) {
                    hourCounts[hour]++;
                }
            }
        });

        const labels = [];
        const values = [];
        
        // 주요 시간대만 표시 (6시간 간격)
        for (let i = 0; i < 24; i += 6) {
            labels.push(`${i}:00`);
            values.push(hourCounts[i]);
        }

        return { labels, values };
    }

    // 모든 차트 업데이트
    updateAllCharts() {
        if (this.charts.trend) {
            const trendData = this.generateTrendData();
            this.charts.trend.data.labels = trendData.labels;
            this.charts.trend.data.datasets[0].data = trendData.integrated;
            this.charts.trend.update('active');
        }

        if (this.charts.status) {
            const statusData = this.generateStatusData();
            this.charts.status.data.labels = statusData.labels;
            this.charts.status.data.datasets[0].data = statusData.values;
            this.charts.status.update('active');
        }

        if (this.charts.timePattern) {
            const timeData = this.generateTimePatternData();
            this.charts.timePattern.data.labels = timeData.labels;
            this.charts.timePattern.data.datasets[0].data = timeData.values;
            this.charts.timePattern.update('active');
        }
    }

    // 차트 제거
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// 전역에서 사용할 수 있도록 export
window.IntegratedCharts = IntegratedCharts;