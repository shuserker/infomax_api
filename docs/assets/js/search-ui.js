// Search UI Components for POSCO Dashboard

class SearchUI {
    constructor(searchEngine, dashboard) {
        this.searchEngine = searchEngine;
        this.dashboard = dashboard;
        this.currentQuery = '';
        this.searchResults = [];
        this.isSearching = false;
        this.suggestionTimeout = null;
        
        this.init();
    }

    init() {
        this.setupSearchInput();
        this.setupSearchSuggestions();
        this.setupKeyboardShortcuts();
        this.setupSearchHistory();
    }

    setupSearchInput() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        // 검색 입력 이벤트
        searchInput.addEventListener('input', debounce((e) => {
            this.handleSearchInput(e.target.value);
        }, 300));

        // 포커스 이벤트
        searchInput.addEventListener('focus', () => {
            this.showSuggestions();
        });

        // 키보드 이벤트
        searchInput.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });

        // 검색 아이콘 클릭
        const searchIcon = searchInput.parentElement.querySelector('i');
        if (searchIcon) {
            searchIcon.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
        }
    }

    setupSearchSuggestions() {
        // 검색 제안 컨테이너 생성
        const searchBox = document.querySelector('.search-box');
        if (!searchBox) return;

        const suggestionsContainer = DOM.create('div', {
            className: 'search-suggestions',
            id: 'searchSuggestions'
        });

        searchBox.appendChild(suggestionsContainer);

        // 외부 클릭 시 제안 숨기기
        document.addEventListener('click', (e) => {
            if (!searchBox.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    setupKeyboardShortcuts() {
        // Ctrl/Cmd + K로 검색 포커스
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });
    }

    setupSearchHistory() {
        // 검색 히스토리 UI 생성
        this.createSearchHistoryPanel();
    }

    handleSearchInput(query) {
        this.currentQuery = query;

        if (query.length === 0) {
            this.clearSearch();
            this.showSuggestions();
            return;
        }

        if (query.length >= 2) {
            this.showSuggestions(query);
        }

        // 실시간 검색 (옵션)
        if (query.length >= 3) {
            this.performSearch(query, false); // 히스토리에 추가하지 않음
        }
    }

    handleKeyDown(e) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        const activeSuggestion = document.querySelector('.suggestion-item.active');

        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                if (activeSuggestion) {
                    this.selectSuggestion(activeSuggestion.textContent);
                } else {
                    this.performSearch(this.currentQuery);
                }
                break;

            case 'ArrowDown':
                e.preventDefault();
                this.navigateSuggestions('down');
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.navigateSuggestions('up');
                break;

            case 'Escape':
                this.hideSuggestions();
                document.getElementById('searchInput').blur();
                break;
        }
    }

    navigateSuggestions(direction) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        if (suggestions.length === 0) return;

        const currentActive = document.querySelector('.suggestion-item.active');
        let newIndex = 0;

        if (currentActive) {
            const currentIndex = Array.from(suggestions).indexOf(currentActive);
            currentActive.classList.remove('active');

            if (direction === 'down') {
                newIndex = (currentIndex + 1) % suggestions.length;
            } else {
                newIndex = currentIndex === 0 ? suggestions.length - 1 : currentIndex - 1;
            }
        }

        suggestions[newIndex].classList.add('active');
        suggestions[newIndex].scrollIntoView({ block: 'nearest' });
    }

    showSuggestions(query = '') {
        const suggestionsContainer = document.getElementById('searchSuggestions');
        if (!suggestionsContainer) return;

        const suggestions = this.searchEngine.getSuggestions(query);
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        const suggestionsHTML = suggestions.map(suggestion => {
            const iconClass = this.getSuggestionIcon(suggestion.type);
            const countBadge = suggestion.count ? 
                `<span class="suggestion-count">${suggestion.count}</span>` : '';
            
            return `
                <div class="suggestion-item" data-query="${suggestion.text}">
                    <i class="${iconClass}"></i>
                    <span class="suggestion-text">${this.highlightQuery(suggestion.text, query)}</span>
                    <span class="suggestion-type">${this.getSuggestionTypeLabel(suggestion.type)}</span>
                    ${countBadge}
                </div>
            `;
        }).join('');

        suggestionsContainer.innerHTML = suggestionsHTML;
        suggestionsContainer.classList.add('show');

        // 제안 항목 클릭 이벤트
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item.dataset.query);
            });
        });
    }

    hideSuggestions() {
        const suggestionsContainer = document.getElementById('searchSuggestions');
        if (suggestionsContainer) {
            suggestionsContainer.classList.remove('show');
        }
    }

    getSuggestionIcon(type) {
        const icons = {
            'history': 'fas fa-history',
            'suggestion': 'fas fa-search',
            'tag': 'fas fa-tag'
        };
        return icons[type] || 'fas fa-search';
    }

    getSuggestionTypeLabel(type) {
        const labels = {
            'history': '최근 검색',
            'suggestion': '제안',
            'tag': '태그'
        };
        return labels[type] || '';
    }

    highlightQuery(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${this.escapeRegExp(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    selectSuggestion(query) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = query;
        }
        
        this.hideSuggestions();
        this.performSearch(query);
    }

    performSearch(query, addToHistory = true) {
        if (!query || query.trim().length === 0) {
            this.clearSearch();
            return;
        }

        this.isSearching = true;
        this.showSearchLoading();

        // 검색 실행
        setTimeout(() => {
            try {
                const results = this.searchEngine.search(query.trim());
                this.displaySearchResults(results, query);
                
                if (addToHistory) {
                    this.updateSearchHistory();
                }
                
                // 검색 통계 업데이트
                this.updateSearchStats();
                
            } catch (error) {
                console.error('검색 오류:', error);
                this.showSearchError();
            } finally {
                this.isSearching = false;
                this.hideSearchLoading();
            }
        }, 100);
    }

    displaySearchResults(results, query) {
        this.searchResults = results;
        
        // 대시보드에 결과 전달
        if (this.dashboard) {
            const documents = results.map(result => result.document);
            this.dashboard.filteredReports = documents;
            this.dashboard.currentPage = 1;
            this.dashboard.renderReports();
            this.dashboard.renderPagination();
        }

        // 검색 결과 정보 표시
        this.showSearchResultsInfo(results.length, query);
        
        // 검색 결과 하이라이트
        this.highlightSearchResults(results, query);
    }

    showSearchResultsInfo(count, query) {
        // 기존 정보 제거
        const existingInfo = document.querySelector('.search-results-info');
        if (existingInfo) {
            existingInfo.remove();
        }

        // 새 정보 생성
        const infoElement = DOM.create('div', {
            className: 'search-results-info'
        });

        if (count === 0) {
            infoElement.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>"${query}"에 대한 검색 결과가 없습니다</h3>
                    <p>다른 키워드로 검색해보세요.</p>
                    <button class="btn btn-secondary" onclick="searchUI.clearSearch()">
                        검색 초기화
                    </button>
                </div>
            `;
        } else {
            infoElement.innerHTML = `
                <div class="search-info">
                    <span class="search-query">"${query}"</span>에 대한 
                    <span class="search-count">${count}개</span>의 검색 결과
                    <button class="btn btn-sm btn-outline" onclick="searchUI.clearSearch()">
                        <i class="fas fa-times"></i> 검색 해제
                    </button>
                </div>
            `;
        }

        // 리포트 그리드 앞에 삽입
        const reportGrid = document.getElementById('reportGrid');
        if (reportGrid) {
            reportGrid.parentNode.insertBefore(infoElement, reportGrid);
        }
    }

    highlightSearchResults(results, query) {
        // 검색 결과에 하이라이트 효과 추가
        setTimeout(() => {
            const reportCards = document.querySelectorAll('.report-card');
            const queryTokens = this.searchEngine.tokenize(query.toLowerCase());
            
            reportCards.forEach((card, index) => {
                if (index < results.length) {
                    const result = results[index];
                    
                    // 매칭 점수에 따른 시각적 표시
                    if (result.score > 5) {
                        card.classList.add('high-relevance');
                    } else if (result.score > 2) {
                        card.classList.add('medium-relevance');
                    }
                    
                    // 텍스트 하이라이트
                    this.highlightTextInElement(card, queryTokens);
                }
            });
        }, 100);
    }

    highlightTextInElement(element, tokens) {
        const textNodes = this.getTextNodes(element);
        
        textNodes.forEach(node => {
            let text = node.textContent;
            let hasHighlight = false;
            
            tokens.forEach(token => {
                const regex = new RegExp(`(${this.escapeRegExp(token)})`, 'gi');
                if (regex.test(text)) {
                    text = text.replace(regex, '<mark class="search-highlight">$1</mark>');
                    hasHighlight = true;
                }
            });
            
            if (hasHighlight) {
                const wrapper = document.createElement('span');
                wrapper.innerHTML = text;
                node.parentNode.replaceChild(wrapper, node);
            }
        });
    }

    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                textNodes.push(node);
            }
        }
        
        return textNodes;
    }

    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        this.currentQuery = '';
        this.searchResults = [];
        this.hideSuggestions();
        
        // 검색 결과 정보 제거
        const searchInfo = document.querySelector('.search-results-info');
        if (searchInfo) {
            searchInfo.remove();
        }
        
        // 하이라이트 제거
        this.removeHighlights();
        
        // 대시보드 초기화
        if (this.dashboard) {
            this.dashboard.filters.search = '';
            this.dashboard.applyFilters();
        }
    }

    removeHighlights() {
        // 검색 하이라이트 제거
        document.querySelectorAll('.search-highlight').forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
        
        // 관련성 클래스 제거
        document.querySelectorAll('.report-card').forEach(card => {
            card.classList.remove('high-relevance', 'medium-relevance');
        });
    }

    showSearchLoading() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.classList.add('searching');
        }
    }

    hideSearchLoading() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.classList.remove('searching');
        }
    }

    showSearchError() {
        const errorElement = DOM.create('div', {
            className: 'search-error'
        });
        
        errorElement.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>검색 중 오류가 발생했습니다</h3>
                <p>잠시 후 다시 시도해주세요.</p>
            </div>
        `;
        
        const reportGrid = document.getElementById('reportGrid');
        if (reportGrid) {
            reportGrid.parentNode.insertBefore(errorElement, reportGrid);
        }
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.remove();
            }
        }, 3000);
    }

    focusSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    updateSearchHistory() {
        // 검색 히스토리 패널 업데이트
        const historyPanel = document.getElementById('searchHistoryPanel');
        if (historyPanel) {
            this.renderSearchHistory();
        }
    }

    createSearchHistoryPanel() {
        // 검색 히스토리 패널은 필요시 동적으로 생성
        // 현재는 제안 시스템으로 대체
    }

    renderSearchHistory() {
        const history = this.searchEngine.searchHistory.slice(0, 10);
        // 히스토리 렌더링 로직 (필요시 구현)
    }

    updateSearchStats() {
        const stats = this.searchEngine.getSearchStats();
        console.log('검색 통계:', stats);
        
        // 통계 정보를 UI에 표시 (선택사항)
        if (window.DEBUG) {
            console.table(stats.topQueries);
        }
    }

    // 고급 검색 기능
    showAdvancedSearch() {
        // 고급 검색 모달 표시 (향후 구현)
        console.log('고급 검색 기능 (향후 구현)');
    }

    // 검색 필터 적용
    applySearchFilters(filters) {
        // 추가 필터와 함께 검색 실행
        if (this.currentQuery) {
            this.performSearch(this.currentQuery);
        }
    }
}

// 전역 검색 UI 인스턴스 (dashboard 초기화 후 생성됨)
let searchUI = null;

// 검색 UI 초기화 함수
function initializeSearchUI(dashboard) {
    if (typeof searchEngine !== 'undefined') {
        searchUI = new SearchUI(searchEngine, dashboard);
        console.log('🔍 검색 UI 초기화 완료');
        return searchUI;
    } else {
        console.error('❌ 검색 엔진이 로드되지 않았습니다');
        return null;
    }
}

// 검색 UI 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SearchUI, initializeSearchUI };
}