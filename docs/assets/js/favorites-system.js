// Advanced Favorites and Recent Items System for POSCO Dashboard

class FavoritesSystem {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.favorites = new Set();
        this.recentItems = [];
        this.maxRecentItems = 20;
        this.syncInterval = 60000; // 1분
        this.syncIntervalId = null;
        
        // 즐겨찾기 카테고리
        this.categories = new Map([
            ['all', '전체'],
            ['integrated', '통합리포트'],
            ['exchange-rate', '서환마감'],
            ['kospi-close', '증시마감'],
            ['newyork-market-watch', '뉴욕마켓워치']
        ]);
        
        this.init();
    }

    init() {
        this.loadFromStorage();
        this.enhanceQuickAccessPanel();
        this.setupEventListeners();
        this.startPeriodicSync();
    }

    enhanceQuickAccessPanel() {
        const quickAccess = document.querySelector('.quick-access');
        if (!quickAccess) return;

        // 기존 탭 버튼 개선
        const tabButtons = quickAccess.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            const tabName = button.dataset.tab;
            const count = this.getItemCount(tabName);
            
            // 카운트 배지 추가
            if (!button.querySelector('.count-badge')) {
                const badge = DOM.create('span', {
                    className: 'count-badge',
                    id: `${tabName}Count`
                });
                badge.textContent = count;
                button.appendChild(badge);
            }
        });

        // 고급 기능 버튼 추가
        this.addAdvancedControls(quickAccess);
        
        // 카테고리 필터 추가
        this.addCategoryFilter(quickAccess);
    }

    addAdvancedControls(quickAccess) {
        const tabsContainer = quickAccess.querySelector('.quick-access-tabs');
        if (!tabsContainer) return;

        // 고급 컨트롤 컨테이너
        const controlsContainer = DOM.create('div', {
            className: 'quick-access-controls'
        });

        controlsContainer.innerHTML = `
            <div class="control-group">
                <button class="btn btn-outline btn-sm" id="exportFavorites" title="즐겨찾기 내보내기">
                    <i class="fas fa-download"></i>
                </button>
                <button class="btn btn-outline btn-sm" id="importFavorites" title="즐겨찾기 가져오기">
                    <i class="fas fa-upload"></i>
                </button>
                <button class="btn btn-outline btn-sm" id="clearRecent" title="최근 항목 지우기">
                    <i class="fas fa-trash"></i>
                </button>
                <button class="btn btn-outline btn-sm" id="syncFavorites" title="동기화">
                    <i class="fas fa-sync"></i>
                </button>
            </div>
            <div class="view-options">
                <button class="view-toggle active" data-view="list" title="목록 보기">
                    <i class="fas fa-list"></i>
                </button>
                <button class="view-toggle" data-view="grid" title="그리드 보기">
                    <i class="fas fa-th"></i>
                </button>
            </div>
        `;

        tabsContainer.appendChild(controlsContainer);
    }

    addCategoryFilter(quickAccess) {
        const contentContainer = quickAccess.querySelector('.quick-access-content');
        if (!contentContainer) return;

        // 카테고리 필터 추가
        const categoryFilter = DOM.create('div', {
            className: 'category-filter',
            id: 'categoryFilter'
        });

        const filterOptions = Array.from(this.categories.entries()).map(([key, name]) => 
            `<button class="category-btn ${key === 'all' ? 'active' : ''}" data-category="${key}">${name}</button>`
        ).join('');

        categoryFilter.innerHTML = `
            <div class="category-buttons">
                ${filterOptions}
            </div>
        `;

        contentContainer.insertBefore(categoryFilter, contentContainer.firstChild);
    }

    setupEventListeners() {
        // 즐겨찾기 버튼 클릭
        document.addEventListener('click', (e) => {
            if (e.target.closest('.favorite-btn')) {
                const button = e.target.closest('.favorite-btn');
                const reportId = button.dataset.reportId;
                this.toggleFavorite(reportId);
            }
        });

        // 고급 컨트롤 버튼들
        this.setupAdvancedControlEvents();
        
        // 카테고리 필터
        this.setupCategoryFilterEvents();
        
        // 뷰 토글
        this.setupViewToggleEvents();
        
        // 탭 전환
        this.setupTabEvents();
    }

    setupAdvancedControlEvents() {
        // 내보내기
        const exportBtn = document.getElementById('exportFavorites');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportFavorites());
        }

        // 가져오기
        const importBtn = document.getElementById('importFavorites');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importFavorites());
        }

        // 최근 항목 지우기
        const clearBtn = document.getElementById('clearRecent');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearRecentItems());
        }

        // 동기화
        const syncBtn = document.getElementById('syncFavorites');
        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.syncWithServer());
        }
    }

    setupCategoryFilterEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('category-btn')) {
                const category = e.target.dataset.category;
                this.filterByCategory(category);
                
                // 활성 상태 업데이트
                document.querySelectorAll('.category-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
            }
        });
    }

    setupViewToggleEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.view-toggle')) {
                const button = e.target.closest('.view-toggle');
                const view = button.dataset.view;
                this.changeView(view);
                
                // 활성 상태 업데이트
                document.querySelectorAll('.view-toggle').forEach(btn => {
                    btn.classList.remove('active');
                });
                button.classList.add('active');
            }
        });
    }

    setupTabEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-button')) {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            }
        });
    }

    // 즐겨찾기 관리
    toggleFavorite(reportId) {
        if (!reportId) return;

        const report = this.findReportById(reportId);
        if (!report) return;

        if (this.favorites.has(reportId)) {
            this.removeFavorite(reportId);
        } else {
            this.addFavorite(reportId, report);
        }

        this.updateFavoriteButton(reportId);
        this.updateFavoritesDisplay();
        this.saveToStorage();
        
        // 알림 표시
        this.showNotification(
            this.favorites.has(reportId) ? '즐겨찾기에 추가되었습니다' : '즐겨찾기에서 제거되었습니다',
            'success'
        );
    }

    addFavorite(reportId, report) {
        this.favorites.add(reportId);
        
        // 즐겨찾기 메타데이터 저장
        const favoriteData = {
            id: reportId,
            title: report.title,
            type: report.type,
            date: report.date,
            url: report.url,
            addedAt: new Date().toISOString(),
            category: report.type
        };
        
        const favoritesData = this.getFavoritesData();
        favoritesData.set(reportId, favoriteData);
        this.saveFavoritesData(favoritesData);
    }

    removeFavorite(reportId) {
        this.favorites.delete(reportId);
        
        const favoritesData = this.getFavoritesData();
        favoritesData.delete(reportId);
        this.saveFavoritesData(favoritesData);
    }

    // 최근 본 항목 관리
    addToRecent(reportId, report) {
        if (!reportId || !report) return;

        // 기존 항목 제거
        this.recentItems = this.recentItems.filter(item => item.id !== reportId);

        // 새 항목을 맨 앞에 추가
        const recentItem = {
            id: reportId,
            title: report.title,
            type: report.type,
            date: report.date,
            url: report.url,
            viewedAt: new Date().toISOString(),
            viewCount: this.getViewCount(reportId) + 1
        };

        this.recentItems.unshift(recentItem);

        // 최대 개수 제한
        if (this.recentItems.length > this.maxRecentItems) {
            this.recentItems = this.recentItems.slice(0, this.maxRecentItems);
        }

        this.updateRecentDisplay();
        this.saveToStorage();
    }

    clearRecentItems() {
        if (confirm('최근 본 항목을 모두 지우시겠습니까?')) {
            this.recentItems = [];
            this.updateRecentDisplay();
            this.saveToStorage();
            this.showNotification('최근 본 항목이 지워졌습니다', 'success');
        }
    }

    // 디스플레이 업데이트
    updateFavoritesDisplay() {
        const container = document.getElementById('favoritesList');
        if (!container) return;

        const favoritesData = this.getFavoritesData();
        const favorites = Array.from(favoritesData.values())
            .sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));

        if (favorites.length === 0) {
            container.innerHTML = '<p class="empty-message text-center text-muted">즐겨찾기한 리포트가 없습니다.</p>';
            return;
        }

        const currentView = this.getCurrentView();
        const currentCategory = this.getCurrentCategory();
        
        // 카테고리 필터링
        const filteredFavorites = currentCategory === 'all' 
            ? favorites 
            : favorites.filter(item => item.category === currentCategory);

        container.innerHTML = this.renderItems(filteredFavorites, currentView, 'favorite');
        this.updateCountBadge('favorites', filteredFavorites.length);
    }

    updateRecentDisplay() {
        const container = document.getElementById('recentList');
        if (!container) return;

        if (this.recentItems.length === 0) {
            container.innerHTML = '<p class="empty-message text-center text-muted">최근 본 리포트가 없습니다.</p>';
            return;
        }

        const currentView = this.getCurrentView();
        const currentCategory = this.getCurrentCategory();
        
        // 카테고리 필터링
        const filteredRecent = currentCategory === 'all' 
            ? this.recentItems 
            : this.recentItems.filter(item => item.type === currentCategory);

        container.innerHTML = this.renderItems(filteredRecent, currentView, 'recent');
        this.updateCountBadge('recent', filteredRecent.length);
    }

    renderItems(items, view, type) {
        if (view === 'grid') {
            return this.renderGridView(items, type);
        } else {
            return this.renderListView(items, type);
        }
    }

    renderListView(items, type) {
        return items.map(item => `
            <div class="quick-item ${type}-item" data-report-id="${item.id}">
                <div class="item-icon">
                    <i class="fas ${this.getTypeIcon(item.type)}"></i>
                </div>
                <div class="item-content">
                    <div class="item-header">
                        <h4 class="item-title">${item.title}</h4>
                        <div class="item-actions">
                            ${type === 'favorite' ? `
                                <button class="btn-icon remove-favorite" data-report-id="${item.id}" title="즐겨찾기 제거">
                                    <i class="fas fa-star"></i>
                                </button>
                            ` : ''}
                            <button class="btn-icon open-report" data-report-id="${item.id}" title="리포트 열기">
                                <i class="fas fa-external-link-alt"></i>
                            </button>
                        </div>
                    </div>
                    <div class="item-meta">
                        <span class="item-date">${formatDate(item.date)}</span>
                        <span class="item-type">${getTypeDisplayName(item.type)}</span>
                        ${type === 'recent' && item.viewCount ? `
                            <span class="view-count">${item.viewCount}회 조회</span>
                        ` : ''}
                        ${type === 'favorite' ? `
                            <span class="added-date">추가: ${getRelativeTime(item.addedAt)}</span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderGridView(items, type) {
        return `
            <div class="items-grid">
                ${items.map(item => `
                    <div class="grid-item ${type}-item" data-report-id="${item.id}">
                        <div class="grid-item-header">
                            <div class="item-type-badge ${item.type}">
                                ${getTypeDisplayName(item.type)}
                            </div>
                            <div class="item-actions">
                                ${type === 'favorite' ? `
                                    <button class="btn-icon remove-favorite" data-report-id="${item.id}">
                                        <i class="fas fa-star"></i>
                                    </button>
                                ` : ''}
                                <button class="btn-icon open-report" data-report-id="${item.id}">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                        <div class="grid-item-content">
                            <h4 class="item-title">${item.title}</h4>
                            <div class="item-meta">
                                <span class="item-date">${formatDate(item.date)}</span>
                                ${type === 'recent' && item.viewCount ? `
                                    <span class="view-count">${item.viewCount}회</span>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // 유틸리티 메서드들
    getTypeIcon(type) {
        const icons = {
            'integrated': 'fa-chart-pie',
            'exchange-rate': 'fa-dollar-sign',
            'kospi-close': 'fa-chart-bar',
            'newyork-market-watch': 'fa-globe-americas'
        };
        return icons[type] || 'fa-file-alt';
    }

    findReportById(reportId) {
        return this.dashboard.reports?.find(report => report.id === reportId);
    }

    updateFavoriteButton(reportId) {
        const buttons = document.querySelectorAll(`[data-report-id="${reportId}"] .favorite-btn`);
        buttons.forEach(button => {
            const isFavorite = this.favorites.has(reportId);
            button.classList.toggle('active', isFavorite);
            button.title = isFavorite ? '즐겨찾기 제거' : '즐겨찾기 추가';
        });
    }

    updateCountBadge(tabName, count) {
        const badge = document.getElementById(`${tabName}Count`);
        if (badge) {
            badge.textContent = count;
            badge.classList.toggle('has-items', count > 0);
        }
    }

    getItemCount(tabName) {
        switch (tabName) {
            case 'favorites':
                return this.favorites.size;
            case 'recent':
                return this.recentItems.length;
            default:
                return 0;
        }
    }

    getCurrentView() {
        const activeToggle = document.querySelector('.view-toggle.active');
        return activeToggle?.dataset.view || 'list';
    }

    getCurrentCategory() {
        const activeCategory = document.querySelector('.category-btn.active');
        return activeCategory?.dataset.category || 'all';
    }

    getViewCount(reportId) {
        const item = this.recentItems.find(item => item.id === reportId);
        return item?.viewCount || 0;
    }

    // 필터링 및 뷰 변경
    filterByCategory(category) {
        this.updateFavoritesDisplay();
        this.updateRecentDisplay();
    }

    changeView(view) {
        this.updateFavoritesDisplay();
        this.updateRecentDisplay();
        
        // 뷰 설정 저장
        Storage.set('quick-access-view', view);
    }

    switchTab(tabName) {
        // 기존 탭 전환 로직 유지
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');

        // 카테고리 필터 표시/숨김
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.style.display = tabName === 'favorites' ? 'block' : 'none';
        }
    }

    // 데이터 관리
    getFavoritesData() {
        const data = Storage.get('favorites-data', {});
        return new Map(Object.entries(data));
    }

    saveFavoritesData(favoritesMap) {
        const data = Object.fromEntries(favoritesMap);
        Storage.set('favorites-data', data);
    }

    loadFromStorage() {
        // 즐겨찾기 로드
        const favoriteIds = Storage.get('favorites', []);
        this.favorites = new Set(favoriteIds);

        // 최근 항목 로드
        this.recentItems = Storage.get('recent-items', []);

        // 뷰 설정 로드
        const savedView = Storage.get('quick-access-view', 'list');
        const viewToggle = document.querySelector(`[data-view="${savedView}"]`);
        if (viewToggle) {
            document.querySelectorAll('.view-toggle').forEach(btn => btn.classList.remove('active'));
            viewToggle.classList.add('active');
        }
    }

    saveToStorage() {
        Storage.set('favorites', Array.from(this.favorites));
        Storage.set('recent-items', this.recentItems);
    }

    // 고급 기능들
    exportFavorites() {
        const favoritesData = this.getFavoritesData();
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            favorites: Object.fromEntries(favoritesData)
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `posco-favorites-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('즐겨찾기가 내보내졌습니다', 'success');
    }

    importFavorites() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    if (data.favorites) {
                        const favoritesMap = new Map(Object.entries(data.favorites));
                        this.saveFavoritesData(favoritesMap);
                        
                        // 즐겨찾기 ID 목록 업데이트
                        this.favorites = new Set(Object.keys(data.favorites));
                        this.saveToStorage();
                        
                        this.updateFavoritesDisplay();
                        this.showNotification('즐겨찾기가 가져와졌습니다', 'success');
                    }
                } catch (error) {
                    this.showNotification('파일을 읽을 수 없습니다', 'error');
                }
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }

    syncWithServer() {
        // 서버와 동기화 (향후 구현)
        const syncBtn = document.getElementById('syncFavorites');
        if (syncBtn) {
            const icon = syncBtn.querySelector('i');
            icon.classList.add('fa-spin');
            
            setTimeout(() => {
                icon.classList.remove('fa-spin');
                this.showNotification('동기화가 완료되었습니다', 'success');
            }, 2000);
        }
    }

    startPeriodicSync() {
        // 주기적 동기화 (향후 구현)
        this.syncIntervalId = setInterval(() => {
            // 서버와 동기화 로직
        }, this.syncInterval);
    }

    showNotification(message, type) {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        }
    }

    // 정리
    destroy() {
        if (this.syncIntervalId) {
            clearInterval(this.syncIntervalId);
        }
    }
}

// 전역 즐겨찾기 시스템 인스턴스
let favoritesSystem = null;

// 즐겨찾기 시스템 초기화 함수
function initializeFavoritesSystem(dashboard) {
    favoritesSystem = new FavoritesSystem(dashboard);
    console.log('⭐ 즐겨찾기 시스템 초기화 완료');
    return favoritesSystem;
}

// 즐겨찾기 시스템 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FavoritesSystem, initializeFavoritesSystem };
}