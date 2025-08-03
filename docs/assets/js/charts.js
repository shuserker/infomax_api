// Advanced Chart System for POSCO Dashboard

class ChartSystem {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = new Map();
        this.chartConfigs = new Map();
        this.animationDuration = 750;
        this.colorScheme = {
            primary: '#003d82',
            secondary: '#0066cc',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            info: '#3b82f6',
            muted: '#64748b'
        };
        
        this.init();
    }

    init() {
        this.setupChartDefaults();
        this.createChartsContainer();
        this.initializeCharts();
    }

    setupChartDefaults() {
        // Chart.js 기본 설정
        Chart.defaults.font.family = "'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim();
        Chart.defaults.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue('--bg-tertiary').trim();
        
        // 반응형 설정
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // 애니메이션 설정
        Chart.defaults.animation.duration = this.animationDuration;
        Chart.defaults.animation.easing = 'easeInOutQuart';
    }

    createChartsContainer() {
        // 기존 통계 섹션을 차트 컨테이너로 확장
        const statsSection = document.getElementById('statsSection');
        if (!statsSection) return;

        // 차트 섹션 추가
        const chartsSection = DOM.create('section', {
            className: 'charts-section mb-8',
            id: 'chartsSection'
        });

        chartsSection.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2 class="text-xl font-semibold text-primary">
                        <i class="fas fa-chart-bar"></i>
                        통계 및 분석
                    </h2>
                    <div class="chart-controls">
                        <select id="chartPeriod" class="filter-select">
                            <option value="7">최근 7일</option>
                            <option value="30" selected>최근 30일</option>
                            <option value="90">최근 90일</option>
                        </select>
                        <button class="btn btn-outline btn-sm" id="refreshCharts">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="charts-grid">
                        <!-- 리포트 생성 트렌드 차트 -->
                        <div class="chart-container">
                            <div class="chart-header">
                                <h3 class="chart-title">리포트 생성 추이</h3>
                                <div class="chart-legend" id="trendLegend"></div>
                            </div>
                            <div class="chart-wrapper">
                                <canvas id="reportTrendChart"></canvas>
                            </div>
                        </div>

                        <!-- 타입별 분포 차트 -->
                        <div class="chart-container">
                            <div class="chart-header">
                                <h3 class="chart-title">타입별 분포</h3>
                                <div class="chart-stats" id="typeStats"></div>
                            </div>
                            <div class="chart-wrapper">
                                <canvas id="typeDistributionChart"></canvas>
                            </div>
                        </div>

                        <!-- 시간대별 발행 패턴 차트 -->
                        <div class="chart-container">
                            <div class="chart-header">
                                <h3 class="chart-title">시간대별 발행 패턴</h3>
                                <div class="chart-info">
                                    <i class="fas fa-info-circle" title="24시간 기준 리포트 생성 패턴"></i>
                                </div>
                            </div>
                            <div class="chart-wrapper">
                                <canvas id="timePatternChart"></canvas>
                            </div>
                        </div>

                        <!-- 성공률 및 성능 차트 -->
                        <div class="chart-container">
                            <div class="chart-header">
                                <h3 class="chart-title">시스템 성능</h3>
                                <div class="performance-indicators" id="performanceIndicators"></div>
                            </div>
                            <div class="chart-wrapper">
                                <canvas id="performanceChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 통계 섹션 다음에 삽입
        statsSection.parentNode.insertBefore(chartsSection, statsSection.nextSibling);

        // 이벤트 리스너 설정
        this.setupChartControls();
    }

    setupChartControls() {
        // 기간 선택
        const periodSelect = document.getElementById('chartPeriod');
        if (periodSelect) {
            periodSelect.addEventListener('change', (e) => {
                this.updateChartsForPeriod(parseInt(e.target.value));
            });
        }

        // 새로고침 버튼
        const refreshBtn = document.getElementById('refreshCharts');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshAllCharts();
            });
        }
    }

    initializeCharts() {
        this.createReportTrendChart();
        this.createTypeDistributionChart();
        this.createTimePatternChart();
        this.createPerformanceChart();
        
        // 테마 변경 감지
        this.observeThemeChanges();
    }

    createReportTrendChart() {
        const canvas = document.getElementById('reportTrendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.generateTrendData();

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: '통합리포트',
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
                    },
                    {
                        label: '서환마감',
                        data: data.exchangeRate,
                        borderColor: this.colorScheme.success,
                        backgroundColor: this.colorScheme.success + '20',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: this.colorScheme.success,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: '증시마감',
                        data: data.kospiClose,
                        borderColor: this.colorScheme.info,
                        backgroundColor: this.colorScheme.info + '20',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: this.colorScheme.info,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: '뉴욕마켓워치',
                        data: data.newyorkWatch,
                        borderColor: this.colorScheme.warning,
                        backgroundColor: this.colorScheme.warning + '20',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: this.colorScheme.warning,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false // 커스텀 범례 사용
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colorScheme.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            title: (context) => {
                                return `${context[0].label}`;
                            },
                            label: (context) => {
                                return `${context.dataset.label}: ${context.parsed.y}개`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            maxTicksLimit: 7
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return value + '개';
                            }
                        }
                    }
                },
                animation: {
                    duration: this.animationDuration,
                    easing: 'easeInOutQuart'
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set('reportTrend', chart);
        this.chartConfigs.set('reportTrend', config);

        // 커스텀 범례 생성
        this.createCustomLegend('trendLegend', config.data.datasets);
    }

    createTypeDistributionChart() {
        const canvas = document.getElementById('typeDistributionChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.generateTypeDistributionData();

        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        this.colorScheme.primary,
                        this.colorScheme.success,
                        this.colorScheme.info,
                        this.colorScheme.warning
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 3,
                    hoverBorderWidth: 4,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colorScheme.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: (context) => {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed}개 (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: this.animationDuration
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set('typeDistribution', chart);
        this.chartConfigs.set('typeDistribution', config);

        // 중앙 텍스트 추가
        this.addDoughnutCenterText(chart, data.total);

        // 타입별 통계 표시
        this.updateTypeStats(data);
    }

    createTimePatternChart() {
        const canvas = document.getElementById('timePatternChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.generateTimePatternData();

        const config = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '리포트 수',
                    data: data.values,
                    backgroundColor: data.values.map((value, index) => {
                        // 시간대별 색상 그라데이션
                        const intensity = value / Math.max(...data.values);
                        return `rgba(0, 61, 130, ${0.3 + intensity * 0.7})`;
                    }),
                    borderColor: this.colorScheme.primary,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colorScheme.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            title: (context) => {
                                return `${context[0].label}시`;
                            },
                            label: (context) => {
                                return `리포트: ${context.parsed.y}개`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            callback: function(value, index) {
                                return index % 2 === 0 ? this.getLabelForValue(value) : '';
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return value + '개';
                            }
                        }
                    }
                },
                animation: {
                    duration: this.animationDuration,
                    easing: 'easeInOutQuart'
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set('timePattern', chart);
        this.chartConfigs.set('timePattern', config);
    }

    createPerformanceChart() {
        const canvas = document.getElementById('performanceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.generatePerformanceData();

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: '성공률 (%)',
                        data: data.successRate,
                        borderColor: this.colorScheme.success,
                        backgroundColor: this.colorScheme.success + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: '응답시간 (ms)',
                        data: data.responseTime,
                        borderColor: this.colorScheme.warning,
                        backgroundColor: this.colorScheme.warning + '20',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colorScheme.primary,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + 'ms';
                            }
                        }
                    }
                },
                animation: {
                    duration: this.animationDuration,
                    easing: 'easeInOutQuart'
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set('performance', chart);
        this.chartConfigs.set('performance', config);

        // 성능 지표 업데이트
        this.updatePerformanceIndicators(data);
    }

    // 데이터 생성 메서드들
    generateTrendData(days = 30) {
        const labels = [];
        const integrated = [];
        const exchangeRate = [];
        const kospiClose = [];
        const newyorkWatch = [];

        const reports = this.dashboard.reports || [];
        const now = new Date();

        // 날짜별 데이터 집계
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));

            // 해당 날짜의 리포트 수 계산
            const dayReports = reports.filter(r => r.date === dateStr);
            
            integrated.push(dayReports.filter(r => r.type === 'integrated').length);
            exchangeRate.push(dayReports.filter(r => r.type === 'exchange-rate').length);
            kospiClose.push(dayReports.filter(r => r.type === 'kospi-close').length);
            newyorkWatch.push(dayReports.filter(r => r.type === 'newyork-market-watch').length);
        }

        return { labels, integrated, exchangeRate, kospiClose, newyorkWatch };
    }

    generateTypeDistributionData() {
        const reports = this.dashboard.reports || [];
        const typeCounts = {
            'integrated': 0,
            'exchange-rate': 0,
            'kospi-close': 0,
            'newyork-market-watch': 0
        };

        reports.forEach(report => {
            if (typeCounts.hasOwnProperty(report.type)) {
                typeCounts[report.type]++;
            }
        });

        return {
            labels: ['통합리포트', '서환마감', '증시마감', '뉴욕마켓워치'],
            values: Object.values(typeCounts),
            total: Object.values(typeCounts).reduce((a, b) => a + b, 0),
            breakdown: typeCounts
        };
    }

    generateTimePatternData() {
        const reports = this.dashboard.reports || [];
        const hourCounts = new Array(24).fill(0);

        reports.forEach(report => {
            if (report.time) {
                const hour = parseInt(report.time.split(':')[0]);
                if (hour >= 0 && hour < 24) {
                    hourCounts[hour]++;
                }
            }
        });

        return {
            labels: Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0')),
            values: hourCounts
        };
    }

    generatePerformanceData(days = 7) {
        // 실제 성능 데이터가 없으므로 시뮬레이션
        const labels = [];
        const successRate = [];
        const responseTime = [];

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));

            // 시뮬레이션 데이터
            successRate.push(95 + Math.random() * 4); // 95-99%
            responseTime.push(100 + Math.random() * 200); // 100-300ms
        }

        return { labels, successRate, responseTime };
    }

    // 유틸리티 메서드들
    createCustomLegend(containerId, datasets) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const legendHTML = datasets.map(dataset => `
            <div class="legend-item">
                <div class="legend-color" style="background-color: ${dataset.borderColor}"></div>
                <span class="legend-label">${dataset.label}</span>
            </div>
        `).join('');

        container.innerHTML = `<div class="custom-legend">${legendHTML}</div>`;
    }

    addDoughnutCenterText(chart, totalValue) {
        const originalDraw = chart.draw;
        chart.draw = function() {
            originalDraw.apply(this, arguments);
            
            const ctx = this.ctx;
            const width = this.width;
            const height = this.height;
            
            ctx.restore();
            ctx.font = "bold 24px 'Noto Sans KR'";
            ctx.textBaseline = "middle";
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim();
            
            const text = totalValue.toString();
            const textX = Math.round((width - ctx.measureText(text).width) / 2);
            const textY = height / 2 - 10;
            
            ctx.fillText(text, textX, textY);
            
            ctx.font = "12px 'Noto Sans KR'";
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
            const subText = "총 리포트";
            const subTextX = Math.round((width - ctx.measureText(subText).width) / 2);
            const subTextY = height / 2 + 15;
            
            ctx.fillText(subText, subTextX, subTextY);
            ctx.save();
        };
    }

    updateTypeStats(data) {
        const container = document.getElementById('typeStats');
        if (!container) return;

        const statsHTML = Object.entries(data.breakdown).map(([type, count]) => {
            const percentage = data.total > 0 ? ((count / data.total) * 100).toFixed(1) : 0;
            const displayName = getTypeDisplayName(type);
            
            return `
                <div class="type-stat">
                    <span class="type-name">${displayName}</span>
                    <span class="type-count">${count}개 (${percentage}%)</span>
                </div>
            `;
        }).join('');

        container.innerHTML = statsHTML;
    }

    updatePerformanceIndicators(data) {
        const container = document.getElementById('performanceIndicators');
        if (!container) return;

        const avgSuccessRate = (data.successRate.reduce((a, b) => a + b, 0) / data.successRate.length).toFixed(1);
        const avgResponseTime = Math.round(data.responseTime.reduce((a, b) => a + b, 0) / data.responseTime.length);

        container.innerHTML = `
            <div class="performance-indicator">
                <div class="indicator-value success">${avgSuccessRate}%</div>
                <div class="indicator-label">평균 성공률</div>
            </div>
            <div class="performance-indicator">
                <div class="indicator-value warning">${avgResponseTime}ms</div>
                <div class="indicator-label">평균 응답시간</div>
            </div>
        `;
    }

    // 차트 업데이트 메서드들
    updateChartsForPeriod(days) {
        const trendChart = this.charts.get('reportTrend');
        if (trendChart) {
            const newData = this.generateTrendData(days);
            trendChart.data.labels = newData.labels;
            trendChart.data.datasets[0].data = newData.integrated;
            trendChart.data.datasets[1].data = newData.exchangeRate;
            trendChart.data.datasets[2].data = newData.kospiClose;
            trendChart.data.datasets[3].data = newData.newyorkWatch;
            trendChart.update('active');
        }

        const performanceChart = this.charts.get('performance');
        if (performanceChart) {
            const newData = this.generatePerformanceData(Math.min(days, 30));
            performanceChart.data.labels = newData.labels;
            performanceChart.data.datasets[0].data = newData.successRate;
            performanceChart.data.datasets[1].data = newData.responseTime;
            performanceChart.update('active');
            
            this.updatePerformanceIndicators(newData);
        }
    }

    refreshAllCharts() {
        // 새로고침 버튼 애니메이션
        const refreshBtn = document.getElementById('refreshCharts');
        if (refreshBtn) {
            refreshBtn.classList.add('spinning');
            setTimeout(() => refreshBtn.classList.remove('spinning'), 1000);
        }

        // 모든 차트 데이터 새로고침
        this.charts.forEach((chart, key) => {
            switch (key) {
                case 'reportTrend':
                    const trendData = this.generateTrendData();
                    chart.data.labels = trendData.labels;
                    chart.data.datasets[0].data = trendData.integrated;
                    chart.data.datasets[1].data = trendData.exchangeRate;
                    chart.data.datasets[2].data = trendData.kospiClose;
                    chart.data.datasets[3].data = trendData.newyorkWatch;
                    break;

                case 'typeDistribution':
                    const typeData = this.generateTypeDistributionData();
                    chart.data.datasets[0].data = typeData.values;
                    this.updateTypeStats(typeData);
                    break;

                case 'timePattern':
                    const timeData = this.generateTimePatternData();
                    chart.data.datasets[0].data = timeData.values;
                    break;

                case 'performance':
                    const perfData = this.generatePerformanceData();
                    chart.data.datasets[0].data = perfData.successRate;
                    chart.data.datasets[1].data = perfData.responseTime;
                    this.updatePerformanceIndicators(perfData);
                    break;
            }
            
            chart.update('active');
        });
    }

    observeThemeChanges() {
        // 고급 테마 시스템 이벤트 리스너
        document.addEventListener('themechange', (event) => {
            console.log('🎨 차트 테마 업데이트:', event.detail.theme);
            this.updateChartsForTheme();
        });

        // 기존 MutationObserver도 유지 (호환성)
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    this.updateChartsForTheme();
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    updateChartsForTheme() {
        // 테마 변경 시 차트 색상 업데이트
        const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim();

        Chart.defaults.color = textColor;
        Chart.defaults.borderColor = borderColor;

        this.charts.forEach(chart => {
            chart.update('none');
        });
    }

    // 차트 제거
    destroyAllCharts() {
        this.charts.forEach(chart => {
            chart.destroy();
        });
        this.charts.clear();
        this.chartConfigs.clear();
    }

    // 차트 데이터 내보내기
    exportChartData(chartKey) {
        const chart = this.charts.get(chartKey);
        if (!chart) return null;

        return {
            labels: chart.data.labels,
            datasets: chart.data.datasets.map(dataset => ({
                label: dataset.label,
                data: dataset.data
            }))
        };
    }
}

// 전역 차트 시스템 인스턴스
let chartSystem = null;

// 차트 시스템 초기화 함수
function initializeChartSystem(dashboard) {
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js가 로드되지 않았습니다');
        return null;
    }

    chartSystem = new ChartSystem(dashboard);
    console.log('📊 차트 시스템 초기화 완료');
    return chartSystem;
}

// 차트 시스템 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartSystem, initializeChartSystem };
}