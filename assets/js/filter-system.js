// Advanced Multi-Filter System for POSCO Dashboard

class FilterSystem {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.activeFilters = new Map();
        this.filterHistory = [];
        this.presets = new Map();
        
        this.init();
    }

    init() {
        this.setupFilterControls();
        this.loadFilterPresets();
        this.loadFilterHistory();
        this.setupFilterPersistence();
    }

    setupFilterControls() {
        // 기존 필터 컨트롤 개선
        this.setupTypeFilter();
        this.setupDateFilter();
        this.setupSortFilter();
        this.setupAdvancedFilters();
        this.setupFilterActions();
    }

    setupTypeFilter() {
        const typeFilter = document.getElementById('typeFilter');
        if (!typeFilter) return;

        // 다중 선택 지원을 위한 개선
        typeFilter.addEventListener('change', (e) => {
            this.updateFilter('type', e.target.value);
        });

        // 타입별 통계 표시
        this.updateTypeFilterStats();
    }

    setupDateFilter() {
        const dateFilter = document.getElementById('dateFilter');
        if (!dateFilter) return;

        // 커스텀 날짜 범위 옵션 추가
        const customOption = document.createElement('option');
        customOption.value = 'custom';
        customOption.textContent = '사용자 정의';
        dateFilter.appendChild(customOption);

        dateFilter.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                this.showCustomDatePicker();
            } else {
                this.updateFilter('date', e.target.value);
            }
        });
    }

    setupSortFilter() {
        const sortFilter = document.getElementById('sortFilter');
        if (!sortFilter) return;

        // 추가 정렬 옵션
        const additionalOptions = [
            { value: 'relevance', text: '관련성순' },
            { value: 'type', text: '타입순' },
            { value: 'size', text: '크기순' }
        ];

        additionalOptions.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.text;
            sortFilter.appendChild(optionElement);
        });

        sortFilter.addEventListener('change', (e) => {
            this.updateFilter('sort', e.target.value);
        });
    }

    setupAdvancedFilters() {
        this.createAdvancedFilterPanel();
    }

    createAdvancedFilterPanel() {
        const filterPanel = document.querySelector('.filter-panel .card-body');
        if (!filterPanel) return;

        // 고급 필터 토글 버튼
        const advancedToggle = DOM.create('button', {
            className: 'btn btn-outline btn-sm',
            id: 'advancedFilterToggle'
        });
        advancedToggle.innerHTML = '<i class="fas fa-sliders-h"></i> 고급 필터';
        
        // 고급 필터 패널
        const advancedPanel = DOM.create('div', {
            className: 'advanced-filters',
            id: 'advancedFilters'
        });

        advancedPanel.innerHTML = `
            <div class="advanced-filters-content">
                <div class="filter-group">
                    <label class="filter-label">태그</label>
                    <div class="tag-filter" id="tagFilter">
                        <!-- 태그 필터 동적 생성 -->
                    </div>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">파일 크기</label>
                    <div class="size-filter">
                        <input type="range" id="sizeRangeMin" min="0" max="1000000" step="10000">
                        <input type="range" id="sizeRangeMax" min="0" max="1000000" step="10000">
                        <div class="size-range-labels">
                            <span id="sizeMinLabel">0 KB</span>
                            <span id="sizeMaxLabel">1000 KB</span>
                        </div>
                    </div>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">생성 시간</label>
                    <div class="time-filter">
                        <select id="timeRangeFilter">
                            <option value="">전체 시간</option>
                            <option value="morning">오전 (06:00-12:00)</option>
                            <option value="afternoon">오후 (12:00-18:00)</option>
                            <option value="evening">저녁 (18:00-24:00)</option>
                            <option value="night">새벽 (00:00-06:00)</option>
                        </select>
                    </div>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">키워드 포함</label>
                    <div class="keyword-filter">
                        <input type="text" id="keywordFilter" placeholder="키워드 입력...">
                        <div class="keyword-suggestions" id="keywordSuggestions"></div>
                    </div>
                </div>
                
                <div class="filter-actions">
                    <button class="btn btn-primary btn-sm" id="applyAdvancedFilters">
                        <i class="fas fa-check"></i> 적용
                    </button>
                    <button class="btn btn-secondary btn-sm" id="resetAdvancedFilters">
                        <i class="fas fa-undo"></i> 초기화
                    </button>
                    <button class="btn btn-outline btn-sm" id="saveFilterPreset">
                        <i class="fas fa-save"></i> 프리셋 저장
                    </button>
                </div>
            </div>
        `;

        // 필터 패널에 추가
        const filterRow = filterPanel.querySelector('.flex');
        if (filterRow) {
            filterRow.appendChild(advancedToggle);
            filterPanel.appendChild(advancedPanel);
        }

        // 이벤트 리스너 설정
        this.setupAdvancedFilterEvents();
        this.populateTagFilter();
        this.setupSizeRangeFilter();
    }

    setupAdvancedFilterEvents() {
        // 고급 필터 토글
        const toggle = document.getElementById('advancedFilterToggle');
        const panel = document.getElementById('advancedFilters');
        
        if (toggle && panel) {
            toggle.addEventListener('click', () => {
                panel.classList.toggle('show');
                toggle.classList.toggle('active');
            });
        }

        // 고급 필터 적용
        const applyBtn = document.getElementById('applyAdvancedFilters');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.applyAdvancedFilters();
            });
        }

        // 고급 필터 초기화
        const resetBtn = document.getElementById('resetAdvancedFilters');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetAdvancedFilters();
            });
        }

        // 프리셋 저장
        const saveBtn = document.getElementById('saveFilterPreset');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.showSavePresetDialog();
            });
        }

        // 키워드 필터
        const keywordInput = document.getElementById('keywordFilter');
        if (keywordInput) {
            keywordInput.addEventListener('input', debounce((e) => {
                this.updateKeywordSuggestions(e.target.value);
            }, 300));
        }

        // 시간 범위 필터
        const timeRangeFilter = document.getElementById('timeRangeFilter');
        if (timeRangeFilter) {
            timeRangeFilter.addEventListener('change', (e) => {
                this.updateFilter('timeRange', e.target.value);
            });
        }
    }

    populateTagFilter() {
        const tagFilter = document.getElementById('tagFilter');
        if (!tagFilter || !this.dashboard.reports) return;

        // 모든 태그 수집
        const tagCounts = new Map();
        this.dashboard.reports.forEach(report => {
            if (report.tags) {
                report.tags.forEach(tag => {
                    tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
                });
            }
        });

        // 태그 빈도순 정렬
        const sortedTags = Array.from(tagCounts.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 20); // 상위 20개만

        // 태그 체크박스 생성
        tagFilter.innerHTML = sortedTags.map(([tag, count]) => `
            <label class="tag-checkbox">
                <input type="checkbox" value="${tag}" data-count="${count}">
                <span class="tag-label">${tag}</span>
                <span class="tag-count">(${count})</span>
            </label>
        `).join('');

        // 태그 선택 이벤트
        tagFilter.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.updateTagFilter();
            }
        });
    }

    setupSizeRangeFilter() {
        const minRange = document.getElementById('sizeRangeMin');
        const maxRange = document.getElementById('sizeRangeMax');
        const minLabel = document.getElementById('sizeMinLabel');
        const maxLabel = document.getElementById('sizeMaxLabel');

        if (!minRange || !maxRange) return;

        // 파일 크기 범위 계산
        const sizes = this.dashboard.reports.map(r => r.size || 0);
        const minSize = Math.min(...sizes);
        const maxSize = Math.max(...sizes);

        minRange.min = minSize;
        minRange.max = maxSize;
        minRange.value = minSize;

        maxRange.min = minSize;
        maxRange.max = maxSize;
        maxRange.value = maxSize;

        // 라벨 업데이트 함수
        const updateLabels = () => {
            minLabel.textContent = this.formatFileSize(parseInt(minRange.value));
            maxLabel.textContent = this.formatFileSize(parseInt(maxRange.value));
        };

        // 초기 라벨 설정
        updateLabels();

        // 범위 변경 이벤트
        minRange.addEventListener('input', updateLabels);
        maxRange.addEventListener('input', updateLabels);

        minRange.addEventListener('change', () => {
            this.updateFilter('sizeMin', parseInt(minRange.value));
        });

        maxRange.addEventListener('change', () => {
            this.updateFilter('sizeMax', parseInt(maxRange.value));
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    updateFilter(key, value) {
        if (value === '' || value === null || value === undefined) {
            this.activeFilters.delete(key);
        } else {
            this.activeFilters.set(key, value);
        }

        this.applyFilters();
        this.saveFilterState();
        this.addToFilterHistory();
    }

    updateTagFilter() {
        const tagCheckboxes = document.querySelectorAll('#tagFilter input[type="checkbox"]:checked');
        const selectedTags = Array.from(tagCheckboxes).map(cb => cb.value);
        
        if (selectedTags.length > 0) {
            this.activeFilters.set('tags', selectedTags);
        } else {
            this.activeFilters.delete('tags');
        }

        this.applyFilters();
    }

    applyFilters() {
        if (!this.dashboard.reports) return;

        let filtered = [...this.dashboard.reports];

        // 각 필터 적용
        for (const [key, value] of this.activeFilters) {
            filtered = this.applyFilter(filtered, key, value);
        }

        // 정렬 적용
        const sortType = this.activeFilters.get('sort') || 'newest';
        filtered = this.sortReports(filtered, sortType);

        // 결과 업데이트
        this.dashboard.filteredReports = filtered;
        this.dashboard.currentPage = 1;
        this.dashboard.renderReports();
        this.dashboard.renderPagination();
        this.dashboard.updateStats();

        // 필터 상태 표시
        this.updateFilterStatus();
    }

    applyFilter(reports, key, value) {
        switch (key) {
            case 'type':
                return value ? reports.filter(r => r.type === value) : reports;

            case 'date':
                return this.applyDateFilter(reports, value);

            case 'tags':
                return reports.filter(r => 
                    r.tags && value.some(tag => r.tags.includes(tag))
                );

            case 'sizeMin':
                return reports.filter(r => (r.size || 0) >= value);

            case 'sizeMax':
                return reports.filter(r => (r.size || 0) <= value);

            case 'timeRange':
                return this.applyTimeRangeFilter(reports, value);

            case 'keyword':
                return this.applyKeywordFilter(reports, value);

            default:
                return reports;
        }
    }

    applyDateFilter(reports, dateFilter) {
        if (!dateFilter) return reports;

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        return reports.filter(report => {
            const reportDate = new Date(report.date);
            const reportDay = new Date(reportDate.getFullYear(), reportDate.getMonth(), reportDate.getDate());

            switch (dateFilter) {
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

                case 'custom':
                    return this.applyCustomDateFilter(reportDay);

                default:
                    return true;
            }
        });
    }

    applyTimeRangeFilter(reports, timeRange) {
        if (!timeRange) return reports;

        return reports.filter(report => {
            const time = report.time;
            if (!time) return true;

            const hour = parseInt(time.split(':')[0]);

            switch (timeRange) {
                case 'morning':
                    return hour >= 6 && hour < 12;
                case 'afternoon':
                    return hour >= 12 && hour < 18;
                case 'evening':
                    return hour >= 18 && hour < 24;
                case 'night':
                    return hour >= 0 && hour < 6;
                default:
                    return true;
            }
        });
    }

    applyKeywordFilter(reports, keyword) {
        if (!keyword) return reports;

        const searchTerms = keyword.toLowerCase().split(' ').filter(term => term.length > 0);

        return reports.filter(report => {
            const searchableText = [
                report.title,
                report.summary?.keyInsights?.join(' '),
                report.tags?.join(' ')
            ].join(' ').toLowerCase();

            return searchTerms.every(term => searchableText.includes(term));
        });
    }

    sortReports(reports, sortType) {
        const sortedReports = [...reports];

        switch (sortType) {
            case 'newest':
                return sortedReports.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

            case 'oldest':
                return sortedReports.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

            case 'name':
                return sortedReports.sort((a, b) => a.title.localeCompare(b.title));

            case 'type':
                return sortedReports.sort((a, b) => a.type.localeCompare(b.type));

            case 'size':
                return sortedReports.sort((a, b) => (b.size || 0) - (a.size || 0));

            case 'relevance':
                // 검색 결과가 있는 경우 관련성순 정렬
                if (window.searchUI && window.searchUI.searchResults.length > 0) {
                    const scoreMap = new Map();
                    window.searchUI.searchResults.forEach(result => {
                        scoreMap.set(result.document.id, result.score);
                    });
                    return sortedReports.sort((a, b) => 
                        (scoreMap.get(b.id) || 0) - (scoreMap.get(a.id) || 0)
                    );
                }
                return sortedReports;

            default:
                return sortedReports;
        }
    }

    updateFilterStatus() {
        this.createFilterStatusDisplay();
        this.updateTypeFilterStats();
    }

    createFilterStatusDisplay() {
        // 기존 상태 표시 제거
        const existingStatus = document.querySelector('.filter-status');
        if (existingStatus) {
            existingStatus.remove();
        }

        if (this.activeFilters.size === 0) return;

        // 활성 필터 표시
        const statusElement = DOM.create('div', {
            className: 'filter-status'
        });

        const filterTags = Array.from(this.activeFilters.entries()).map(([key, value]) => {
            const displayValue = this.getFilterDisplayValue(key, value);
            return `
                <span class="filter-tag" data-filter="${key}">
                    ${displayValue}
                    <button class="filter-remove" onclick="filterSystem.removeFilter('${key}')">
                        <i class="fas fa-times"></i>
                    </button>
                </span>
            `;
        }).join('');

        statusElement.innerHTML = `
            <div class="filter-status-content">
                <span class="filter-status-label">활성 필터:</span>
                ${filterTags}
                <button class="btn btn-sm btn-outline" onclick="filterSystem.clearAllFilters()">
                    <i class="fas fa-times"></i> 모든 필터 해제
                </button>
            </div>
        `;

        // 필터 패널 다음에 삽입
        const filterPanel = document.querySelector('.filter-panel');
        if (filterPanel) {
            filterPanel.parentNode.insertBefore(statusElement, filterPanel.nextSibling);
        }
    }

    getFilterDisplayValue(key, value) {
        switch (key) {
            case 'type':
                return `타입: ${getTypeDisplayName(value)}`;
            case 'date':
                return `날짜: ${this.getDateFilterLabel(value)}`;
            case 'tags':
                return `태그: ${value.join(', ')}`;
            case 'timeRange':
                return `시간: ${this.getTimeRangeLabel(value)}`;
            case 'keyword':
                return `키워드: ${value}`;
            case 'sizeMin':
                return `최소 크기: ${this.formatFileSize(value)}`;
            case 'sizeMax':
                return `최대 크기: ${this.formatFileSize(value)}`;
            default:
                return `${key}: ${value}`;
        }
    }

    getDateFilterLabel(value) {
        const labels = {
            'today': '오늘',
            'yesterday': '어제',
            'week': '최근 7일',
            'month': '최근 30일',
            'custom': '사용자 정의'
        };
        return labels[value] || value;
    }

    getTimeRangeLabel(value) {
        const labels = {
            'morning': '오전',
            'afternoon': '오후',
            'evening': '저녁',
            'night': '새벽'
        };
        return labels[value] || value;
    }

    removeFilter(key) {
        this.activeFilters.delete(key);
        this.applyFilters();
        this.updateFilterControls();
    }

    clearAllFilters() {
        this.activeFilters.clear();
        this.applyFilters();
        this.updateFilterControls();
    }

    updateFilterControls() {
        // 필터 컨트롤 UI 업데이트
        document.getElementById('typeFilter').value = this.activeFilters.get('type') || '';
        document.getElementById('dateFilter').value = this.activeFilters.get('date') || '';
        document.getElementById('sortFilter').value = this.activeFilters.get('sort') || 'newest';

        // 고급 필터 컨트롤 업데이트
        const keywordInput = document.getElementById('keywordFilter');
        if (keywordInput) {
            keywordInput.value = this.activeFilters.get('keyword') || '';
        }

        const timeRangeFilter = document.getElementById('timeRangeFilter');
        if (timeRangeFilter) {
            timeRangeFilter.value = this.activeFilters.get('timeRange') || '';
        }

        // 태그 체크박스 업데이트
        const selectedTags = this.activeFilters.get('tags') || [];
        document.querySelectorAll('#tagFilter input[type="checkbox"]').forEach(cb => {
            cb.checked = selectedTags.includes(cb.value);
        });
    }

    updateTypeFilterStats() {
        // 타입별 리포트 수 표시 (향후 구현)
    }

    // 필터 프리셋 관리
    saveFilterPreset(name) {
        const preset = {
            name: name,
            filters: Object.fromEntries(this.activeFilters),
            createdAt: new Date().toISOString()
        };

        this.presets.set(name, preset);
        this.savePresets();
    }

    loadFilterPreset(name) {
        const preset = this.presets.get(name);
        if (preset) {
            this.activeFilters = new Map(Object.entries(preset.filters));
            this.applyFilters();
            this.updateFilterControls();
        }
    }

    // 필터 상태 저장/복원
    saveFilterState() {
        try {
            const state = Object.fromEntries(this.activeFilters);
            localStorage.setItem('posco-filter-state', JSON.stringify(state));
        } catch (e) {
            console.warn('필터 상태 저장 실패:', e);
        }
    }

    loadFilterState() {
        try {
            const saved = localStorage.getItem('posco-filter-state');
            if (saved) {
                const state = JSON.parse(saved);
                this.activeFilters = new Map(Object.entries(state));
                this.updateFilterControls();
            }
        } catch (e) {
            console.warn('필터 상태 로드 실패:', e);
        }
    }

    // 기타 유틸리티 메서드들...
    setupFilterPersistence() {
        this.loadFilterState();
    }

    loadFilterPresets() {
        try {
            const saved = localStorage.getItem('posco-filter-presets');
            if (saved) {
                const presets = JSON.parse(saved);
                this.presets = new Map(Object.entries(presets));
            }
        } catch (e) {
            console.warn('필터 프리셋 로드 실패:', e);
        }
    }

    savePresets() {
        try {
            const presets = Object.fromEntries(this.presets);
            localStorage.setItem('posco-filter-presets', JSON.stringify(presets));
        } catch (e) {
            console.warn('필터 프리셋 저장 실패:', e);
        }
    }

    loadFilterHistory() {
        try {
            const saved = localStorage.getItem('posco-filter-history');
            if (saved) {
                this.filterHistory = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('필터 히스토리 로드 실패:', e);
        }
    }

    addToFilterHistory() {
        if (this.activeFilters.size === 0) return;

        const historyItem = {
            filters: Object.fromEntries(this.activeFilters),
            timestamp: new Date().toISOString()
        };

        this.filterHistory.unshift(historyItem);
        
        // 히스토리 크기 제한
        if (this.filterHistory.length > 20) {
            this.filterHistory = this.filterHistory.slice(0, 20);
        }

        try {
            localStorage.setItem('posco-filter-history', JSON.stringify(this.filterHistory));
        } catch (e) {
            console.warn('필터 히스토리 저장 실패:', e);
        }
    }

    // 추가 메서드들 (커스텀 날짜 선택, 키워드 제안 등)
    showCustomDatePicker() {
        // 커스텀 날짜 선택 모달 (향후 구현)
        console.log('커스텀 날짜 선택 (향후 구현)');
    }

    updateKeywordSuggestions(keyword) {
        // 키워드 제안 업데이트 (향후 구현)
        console.log('키워드 제안:', keyword);
    }

    showSavePresetDialog() {
        const name = prompt('프리셋 이름을 입력하세요:');
        if (name && name.trim()) {
            this.saveFilterPreset(name.trim());
            alert('프리셋이 저장되었습니다.');
        }
    }

    applyAdvancedFilters() {
        // 고급 필터 적용
        const keywordInput = document.getElementById('keywordFilter');
        if (keywordInput && keywordInput.value) {
            this.updateFilter('keyword', keywordInput.value);
        }

        this.updateTagFilter();
        
        // 패널 닫기
        const panel = document.getElementById('advancedFilters');
        if (panel) {
            panel.classList.remove('show');
        }
    }

    resetAdvancedFilters() {
        // 고급 필터 초기화
        const keywordInput = document.getElementById('keywordFilter');
        if (keywordInput) keywordInput.value = '';

        const timeRangeFilter = document.getElementById('timeRangeFilter');
        if (timeRangeFilter) timeRangeFilter.value = '';

        // 태그 체크박스 해제
        document.querySelectorAll('#tagFilter input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });

        // 크기 범위 초기화
        const minRange = document.getElementById('sizeRangeMin');
        const maxRange = document.getElementById('sizeRangeMax');
        if (minRange) minRange.value = minRange.min;
        if (maxRange) maxRange.value = maxRange.max;

        // 필터 제거
        this.activeFilters.delete('keyword');
        this.activeFilters.delete('timeRange');
        this.activeFilters.delete('tags');
        this.activeFilters.delete('sizeMin');
        this.activeFilters.delete('sizeMax');

        this.applyFilters();
    }
}

// 전역 필터 시스템 인스턴스
let filterSystem = null;

// 필터 시스템 초기화 함수
function initializeFilterSystem(dashboard) {
    filterSystem = new FilterSystem(dashboard);
    console.log('🔧 필터 시스템 초기화 완료');
    return filterSystem;
}

// 필터 시스템 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FilterSystem, initializeFilterSystem };
}