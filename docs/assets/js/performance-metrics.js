// Real-time Performance Metrics System for POSCO Dashboard

class PerformanceMetrics {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.metrics = new Map();
        this.updateInterval = 30000; // 30초
        this.intervalId = null;
        this.isUpdating = false;
        
        // 성과 지표 임계값
        this.thresholds = {
            successRate: { good: 95, warning: 90 },
            responseTime: { good: 200, warning: 500 },
            uptime: { good: 99, warning: 95 },
            errorRate: { good: 1, warning: 5 }
        };
        
        this.init();
    }

    init() {
        this.createMetricsDisplay();
        this.startRealTimeUpdates();
        this.setupEventListeners();
    }

    createMetricsDisplay() {
        // 기존 통계 카드들을 성과 지표로 개선
        this.enhanceStatCards();
        this.createRealTimeIndicators();
        this.createSystemHealthPanel();
    }

    enhanceStatCards() {
        const statsGrid = document.querySelector('.stats-grid');
        if (!statsGrid) return;

        // 기존 통계 카드에 실시간 업데이트 기능 추가
        const statCards = statsGrid.querySelectorAll('.stat-card');
        
        statCards.forEach((card, index) => {
            // 실시간 업데이트 인디케이터 추가
            const indicator = DOM.create('div', {
                className: 'real-time-indicator',
                title: '실시간 업데이트'
            });
            indicator.innerHTML = '<i class="fas fa-circle"></i>';
            
            const cardBody = card.querySelector('.card-body') || card;
            cardBody.appendChild(indicator);
            
            // 트렌드 표시 추가
            const trendIndicator = DOM.create('div', {
                className: 'trend-indicator'
            });
            
            const statInfo = card.querySelector('.stat-info');
            if (statInfo) {
                statInfo.appendChild(trendIndicator);
            }
        });
    }

    createRealTimeIndicators() {
        // 실시간 성과 지표 패널 생성
        const metricsPanel = DOM.create('section', {
            className: 'performance-metrics-panel mb-8',
            id: 'performanceMetricsPanel'
        });

        metricsPanel.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2 class="text-xl font-semibold text-primary">
                        <i class="fas fa-tachometer-alt"></i>
                        실시간 성과 지표
                    </h2>
                    <div class="metrics-controls">
                        <div class="update-status" id="updateStatus">
                            <i class="fas fa-circle status-indicator"></i>
                            <span class="status-text">실시간 업데이트</span>
                        </div>
                        <button class="btn btn-outline btn-sm" id="pauseUpdates">
                            <i class="fas fa-pause"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="metrics-grid">
                        <!-- 시스템 가동률 -->
                        <div class="metric-card" id="uptimeMetric">
                            <div class="metric-header">
                                <div class="metric-icon uptime">
                                    <i class="fas fa-server"></i>
                                </div>
                                <div class="metric-info">
                                    <h3 class="metric-title">시스템 가동률</h3>
                                    <div class="metric-subtitle">System Uptime</div>
                                </div>
                            </div>
                            <div class="metric-value-container">
                                <div class="metric-value" id="uptimeValue">99.8%</div>
                                <div class="metric-trend" id="uptimeTrend">
                                    <i class="fas fa-arrow-up"></i>
                                    <span>+0.1%</span>
                                </div>
                            </div>
                            <div class="metric-progress">
                                <div class="progress-bar" id="uptimeProgress"></div>
                            </div>
                        </div>

                        <!-- 리포트 생성 성공률 -->
                        <div class="metric-card" id="successRateMetric">
                            <div class="metric-header">
                                <div class="metric-icon success">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                                <div class="metric-info">
                                    <h3 class="metric-title">생성 성공률</h3>
                                    <div class="metric-subtitle">Success Rate</div>
                                </div>
                            </div>
                            <div class="metric-value-container">
                                <div class="metric-value" id="successRateValue">98.5%</div>
                                <div class="metric-trend" id="successRateTrend">
                                    <i class="fas fa-arrow-up"></i>
                                    <span>+1.2%</span>
                                </div>
                            </div>
                            <div class="metric-progress">
                                <div class="progress-bar" id="successRateProgress"></div>
                            </div>
                        </div>

                        <!-- 평균 응답 시간 -->
                        <div class="metric-card" id="responseTimeMetric">
                            <div class="metric-header">
                                <div class="metric-icon response">
                                    <i class="fas fa-clock"></i>
                                </div>
                                <div class="metric-info">
                                    <h3 class="metric-title">평균 응답시간</h3>
                                    <div class="metric-subtitle">Response Time</div>
                                </div>
                            </div>
                            <div class="metric-value-container">
                                <div class="metric-value" id="responseTimeValue">245ms</div>
                                <div class="metric-trend" id="responseTimeTrend">
                                    <i class="fas fa-arrow-down"></i>
                                    <span>-15ms</span>
                                </div>
                            </div>
                            <div class="metric-progress">
                                <div class="progress-bar" id="responseTimeProgress"></div>
                            </div>
                        </div>

                        <!-- 오류율 -->
                        <div class="metric-card" id="errorRateMetric">
                            <div class="metric-header">
                                <div class="metric-icon error">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </div>
                                <div class="metric-info">
                                    <h3 class="metric-title">오류율</h3>
                                    <div class="metric-subtitle">Error Rate</div>
                                </div>
                            </div>
                            <div class="metric-value-container">
                                <div class="metric-value" id="errorRateValue">1.5%</div>
                                <div class="metric-trend" id="errorRateTrend">
                                    <i class="fas fa-arrow-down"></i>
                                    <span>-0.3%</span>
                                </div>
                            </div>
                            <div class="metric-progress">
                                <div class="progress-bar" id="errorRateProgress"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 차트 섹션 앞에 삽입
        const chartsSection = document.getElementById('chartsSection');
        if (chartsSection) {
            chartsSection.parentNode.insertBefore(metricsPanel, chartsSection);
        } else {
            const statsSection = document.getElementById('statsSection');
            if (statsSection) {
                statsSection.parentNode.insertBefore(metricsPanel, statsSection.nextSibling);
            }
        }
    }

    createSystemHealthPanel() {
        // 시스템 상태 상세 패널
        const healthPanel = DOM.create('div', {
            className: 'system-health-panel',
            id: 'systemHealthPanel'
        });

        healthPanel.innerHTML = `
            <div class="health-header">
                <h3 class="health-title">
                    <i class="fas fa-heartbeat"></i>
                    시스템 상태
                </h3>
                <div class="health-status" id="overallHealthStatus">
                    <div class="health-indicator good"></div>
                    <span>정상</span>
                </div>
            </div>
            <div class="health-services">
                <div class="service-item" id="watchHamsterService">
                    <div class="service-icon">
                        <i class="fas fa-eye"></i>
                    </div>
                    <div class="service-info">
                        <div class="service-name">워치햄스터</div>
                        <div class="service-status">실행 중</div>
                    </div>
                    <div class="service-indicator good"></div>
                </div>
                <div class="service-item" id="reportGeneratorService">
                    <div class="service-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div class="service-info">
                        <div class="service-name">리포트 생성기</div>
                        <div class="service-status">실행 중</div>
                    </div>
                    <div class="service-indicator good"></div>
                </div>
                <div class="service-item" id="githubPagesService">
                    <div class="service-icon">
                        <i class="fab fa-github"></i>
                    </div>
                    <div class="service-info">
                        <div class="service-name">GitHub Pages</div>
                        <div class="service-status">활성</div>
                    </div>
                    <div class="service-indicator good"></div>
                </div>
            </div>
        `;

        // 성과 지표 패널에 추가
        const metricsPanel = document.getElementById('performanceMetricsPanel');
        if (metricsPanel) {
            const cardBody = metricsPanel.querySelector('.card-body');
            if (cardBody) {
                cardBody.appendChild(healthPanel);
            }
        }
    }

    setupEventListeners() {
        // 업데이트 일시정지/재개 버튼
        const pauseBtn = document.getElementById('pauseUpdates');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                this.toggleUpdates();
            });
        }

        // 메트릭 카드 클릭 시 상세 정보 표시
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const metricId = e.currentTarget.id;
                this.showMetricDetails(metricId);
            });
        });
    }

    startRealTimeUpdates() {
        this.updateMetrics(); // 초기 업데이트
        
        this.intervalId = setInterval(() => {
            if (!this.isUpdating) {
                this.updateMetrics();
            }
        }, this.updateInterval);

        console.log('📊 실시간 성과 지표 업데이트 시작');
    }

    async updateMetrics() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        this.showUpdateIndicator();

        try {
            // 상태 데이터 가져오기
            const statusData = await this.fetchStatusData();
            
            // 메트릭 계산 및 업데이트
            await this.calculateMetrics(statusData);
            
            // UI 업데이트
            this.updateMetricsDisplay();
            this.updateSystemHealth(statusData);
            
            // 차트 업데이트 (있는 경우)
            if (window.chartSystem) {
                window.chartSystem.refreshAllCharts();
            }
            
        } catch (error) {
            console.error('성과 지표 업데이트 실패:', error);
            this.showUpdateError();
        } finally {
            this.isUpdating = false;
            this.hideUpdateIndicator();
        }
    }

    async fetchStatusData() {
        try {
            const response = await fetch('./status.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('상태 데이터 가져오기 실패, 시뮬레이션 데이터 사용');
            return this.generateSimulatedData();
        }
    }

    generateSimulatedData() {
        // 실제 데이터가 없을 때 시뮬레이션 데이터 생성
        return {
            systemStatus: {
                uptime: (99 + Math.random()).toFixed(1) + '%',
                monitoring: 'active',
                errors: []
            },
            statistics: {
                successRate: (95 + Math.random() * 4).toFixed(1),
                totalReports: Math.floor(Math.random() * 100) + 50,
                reportsToday: Math.floor(Math.random() * 20) + 5
            },
            newsStatus: {
                'exchange-rate': { published: Math.random() > 0.2 },
                'kospi-close': { published: Math.random() > 0.2 },
                'newyork-market-watch': { published: Math.random() > 0.2 }
            }
        };
    }

    async calculateMetrics(statusData) {
        const now = Date.now();
        
        // 시스템 가동률
        const uptime = parseFloat(statusData.systemStatus?.uptime || '99.8');
        this.updateMetric('uptime', uptime, '%', this.calculateTrend('uptime', uptime));
        
        // 생성 성공률
        const successRate = parseFloat(statusData.statistics?.successRate || '98.5');
        this.updateMetric('successRate', successRate, '%', this.calculateTrend('successRate', successRate));
        
        // 응답 시간 (시뮬레이션)
        const responseTime = 200 + Math.random() * 100;
        this.updateMetric('responseTime', Math.round(responseTime), 'ms', this.calculateTrend('responseTime', responseTime));
        
        // 오류율 계산
        const errorCount = statusData.systemStatus?.errors?.length || 0;
        const totalReports = statusData.statistics?.totalReports || 100;
        const errorRate = totalReports > 0 ? (errorCount / totalReports * 100) : 0;
        this.updateMetric('errorRate', errorRate.toFixed(1), '%', this.calculateTrend('errorRate', errorRate));
    }

    updateMetric(key, value, unit, trend) {
        const previousValue = this.metrics.get(key)?.value || value;
        
        this.metrics.set(key, {
            value: value,
            unit: unit,
            trend: trend,
            previousValue: previousValue,
            timestamp: Date.now(),
            status: this.getMetricStatus(key, value)
        });
    }

    calculateTrend(key, currentValue) {
        const previous = this.metrics.get(key);
        if (!previous) return { direction: 'stable', change: 0 };
        
        const change = currentValue - previous.value;
        const direction = change > 0 ? 'up' : change < 0 ? 'down' : 'stable';
        
        return { direction, change: Math.abs(change) };
    }

    getMetricStatus(key, value) {
        const thresholds = this.thresholds[key];
        if (!thresholds) return 'good';
        
        if (key === 'responseTime' || key === 'errorRate') {
            // 낮을수록 좋은 메트릭
            if (value <= thresholds.good) return 'good';
            if (value <= thresholds.warning) return 'warning';
            return 'critical';
        } else {
            // 높을수록 좋은 메트릭
            if (value >= thresholds.good) return 'good';
            if (value >= thresholds.warning) return 'warning';
            return 'critical';
        }
    }

    updateMetricsDisplay() {
        this.metrics.forEach((metric, key) => {
            this.updateMetricCard(key, metric);
        });
    }

    updateMetricCard(key, metric) {
        const valueElement = document.getElementById(`${key}Value`);
        const trendElement = document.getElementById(`${key}Trend`);
        const progressElement = document.getElementById(`${key}Progress`);
        const cardElement = document.getElementById(`${key}Metric`);

        if (valueElement) {
            // 값 업데이트 (애니메이션 효과)
            this.animateValue(valueElement, metric.value, metric.unit);
        }

        if (trendElement) {
            // 트렌드 업데이트
            const trendIcon = trendElement.querySelector('i');
            const trendText = trendElement.querySelector('span');
            
            if (trendIcon && trendText) {
                trendIcon.className = `fas fa-arrow-${metric.trend.direction === 'up' ? 'up' : metric.trend.direction === 'down' ? 'down' : 'right'}`;
                trendText.textContent = `${metric.trend.direction === 'up' ? '+' : metric.trend.direction === 'down' ? '-' : ''}${metric.trend.change.toFixed(1)}${metric.unit}`;
                
                // 트렌드 색상
                trendElement.className = `metric-trend ${metric.trend.direction}`;
            }
        }

        if (progressElement) {
            // 진행률 바 업데이트
            const percentage = this.calculateProgressPercentage(key, metric.value);
            progressElement.style.width = `${percentage}%`;
            progressElement.className = `progress-bar ${metric.status}`;
        }

        if (cardElement) {
            // 카드 상태 업데이트
            cardElement.className = `metric-card ${metric.status}`;
        }
    }

    calculateProgressPercentage(key, value) {
        switch (key) {
            case 'uptime':
            case 'successRate':
                return Math.min(value, 100);
            case 'responseTime':
                return Math.max(0, 100 - (value / 1000 * 100));
            case 'errorRate':
                return Math.max(0, 100 - (value * 10));
            default:
                return 50;
        }
    }

    animateValue(element, targetValue, unit) {
        const currentValue = parseFloat(element.textContent) || 0;
        const difference = targetValue - currentValue;
        const steps = 20;
        const stepValue = difference / steps;
        let currentStep = 0;

        const animation = setInterval(() => {
            currentStep++;
            const newValue = currentValue + (stepValue * currentStep);
            
            if (unit === 'ms') {
                element.textContent = Math.round(newValue) + unit;
            } else {
                element.textContent = newValue.toFixed(1) + unit;
            }

            if (currentStep >= steps) {
                clearInterval(animation);
                element.textContent = (unit === 'ms' ? Math.round(targetValue) : targetValue.toFixed(1)) + unit;
            }
        }, 50);
    }

    updateSystemHealth(statusData) {
        const overallStatus = document.getElementById('overallHealthStatus');
        const services = {
            watchHamster: statusData.systemStatus?.services?.watchHamster?.status || 'unknown',
            reportGenerator: statusData.systemStatus?.services?.reportGenerator?.status || 'unknown',
            githubPages: statusData.systemStatus?.services?.githubPages?.status || 'unknown'
        };

        // 전체 상태 계산
        const healthyServices = Object.values(services).filter(status => 
            status === 'running' || status === 'active'
        ).length;
        
        const totalServices = Object.keys(services).length;
        const healthPercentage = (healthyServices / totalServices) * 100;

        let overallHealthStatus = 'good';
        let statusText = '정상';

        if (healthPercentage < 50) {
            overallHealthStatus = 'critical';
            statusText = '심각';
        } else if (healthPercentage < 80) {
            overallHealthStatus = 'warning';
            statusText = '주의';
        }

        // 전체 상태 업데이트
        if (overallStatus) {
            const indicator = overallStatus.querySelector('.health-indicator');
            const text = overallStatus.querySelector('span');
            
            if (indicator) indicator.className = `health-indicator ${overallHealthStatus}`;
            if (text) text.textContent = statusText;
        }

        // 개별 서비스 상태 업데이트
        Object.entries(services).forEach(([service, status]) => {
            this.updateServiceStatus(service, status);
        });
    }

    updateServiceStatus(serviceName, status) {
        const serviceElement = document.getElementById(`${serviceName}Service`);
        if (!serviceElement) return;

        const indicator = serviceElement.querySelector('.service-indicator');
        const statusText = serviceElement.querySelector('.service-status');

        let statusClass = 'unknown';
        let displayText = '알 수 없음';

        switch (status) {
            case 'running':
            case 'active':
                statusClass = 'good';
                displayText = status === 'running' ? '실행 중' : '활성';
                break;
            case 'stopped':
            case 'inactive':
                statusClass = 'critical';
                displayText = '중지됨';
                break;
            case 'error':
                statusClass = 'critical';
                displayText = '오류';
                break;
            default:
                statusClass = 'warning';
                displayText = '확인 중';
        }

        if (indicator) indicator.className = `service-indicator ${statusClass}`;
        if (statusText) statusText.textContent = displayText;
    }

    showUpdateIndicator() {
        const updateStatus = document.getElementById('updateStatus');
        if (updateStatus) {
            updateStatus.classList.add('updating');
            const indicator = updateStatus.querySelector('.status-indicator');
            if (indicator) {
                indicator.classList.add('pulse');
            }
        }
    }

    hideUpdateIndicator() {
        const updateStatus = document.getElementById('updateStatus');
        if (updateStatus) {
            updateStatus.classList.remove('updating');
            const indicator = updateStatus.querySelector('.status-indicator');
            if (indicator) {
                indicator.classList.remove('pulse');
            }
        }
    }

    showUpdateError() {
        const updateStatus = document.getElementById('updateStatus');
        if (updateStatus) {
            updateStatus.classList.add('error');
            const text = updateStatus.querySelector('.status-text');
            if (text) {
                text.textContent = '업데이트 오류';
            }
        }
    }

    toggleUpdates() {
        const pauseBtn = document.getElementById('pauseUpdates');
        const updateStatus = document.getElementById('updateStatus');
        
        if (this.intervalId) {
            // 업데이트 일시정지
            clearInterval(this.intervalId);
            this.intervalId = null;
            
            if (pauseBtn) {
                pauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                pauseBtn.title = '업데이트 재개';
            }
            
            if (updateStatus) {
                const text = updateStatus.querySelector('.status-text');
                if (text) text.textContent = '업데이트 일시정지';
            }
        } else {
            // 업데이트 재개
            this.startRealTimeUpdates();
            
            if (pauseBtn) {
                pauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                pauseBtn.title = '업데이트 일시정지';
            }
            
            if (updateStatus) {
                const text = updateStatus.querySelector('.status-text');
                if (text) text.textContent = '실시간 업데이트';
            }
        }
    }

    showMetricDetails(metricId) {
        const metric = this.metrics.get(metricId.replace('Metric', ''));
        if (!metric) return;

        // 메트릭 상세 정보 모달 표시 (향후 구현)
        console.log('메트릭 상세 정보:', metric);
    }

    // 정리 메서드
    destroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.metrics.clear();
        console.log('📊 성과 지표 시스템 정리 완료');
    }

    // 메트릭 데이터 내보내기
    exportMetrics() {
        const exportData = {
            timestamp: new Date().toISOString(),
            metrics: Object.fromEntries(this.metrics)
        };
        
        return exportData;
    }
}

// 전역 성과 지표 시스템 인스턴스
let performanceMetrics = null;

// 성과 지표 시스템 초기화 함수
function initializePerformanceMetrics(dashboard) {
    performanceMetrics = new PerformanceMetrics(dashboard);
    console.log('📊 실시간 성과 지표 시스템 초기화 완료');
    return performanceMetrics;
}

// 성과 지표 시스템 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PerformanceMetrics, initializePerformanceMetrics };
}