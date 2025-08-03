// Advanced Client-Side Search Engine for POSCO Dashboard

class SearchEngine {
    constructor() {
        this.searchIndex = new Map();
        this.documents = [];
        this.stopWords = new Set([
            '의', '가', '이', '은', '는', '을', '를', '에', '에서', '로', '으로',
            '와', '과', '도', '만', '까지', '부터', '에게', '한테', '께',
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        ]);
        this.searchHistory = [];
        this.maxHistorySize = 50;
    }

    /**
     * 문서들을 인덱싱하여 검색 가능하게 만듦
     * @param {Array} documents - 검색할 문서 배열
     */
    indexDocuments(documents) {
        console.log(`🔍 ${documents.length}개 문서 인덱싱 시작...`);
        
        this.documents = documents;
        this.searchIndex.clear();
        
        documents.forEach((doc, index) => {
            this.indexDocument(doc, index);
        });
        
        console.log(`✅ 인덱싱 완료: ${this.searchIndex.size}개 토큰`);
    }

    /**
     * 개별 문서 인덱싱
     * @param {Object} document - 문서 객체
     * @param {number} index - 문서 인덱스
     */
    indexDocument(document, index) {
        const searchableText = this.extractSearchableText(document);
        const tokens = this.tokenize(searchableText);
        
        tokens.forEach(token => {
            if (!this.searchIndex.has(token)) {
                this.searchIndex.set(token, new Set());
            }
            this.searchIndex.get(token).add(index);
        });
    }

    /**
     * 문서에서 검색 가능한 텍스트 추출
     * @param {Object} document - 문서 객체
     * @returns {string} 검색 가능한 텍스트
     */
    extractSearchableText(document) {
        const searchableFields = [
            document.title || '',
            document.summary?.keyInsights?.join(' ') || '',
            document.tags?.join(' ') || '',
            getTypeDisplayName(document.type) || '',
            document.date || '',
            document.time || ''
        ];
        
        return searchableFields.join(' ').toLowerCase();
    }

    /**
     * 텍스트를 토큰으로 분할
     * @param {string} text - 분할할 텍스트
     * @returns {Array} 토큰 배열
     */
    tokenize(text) {
        // 한글, 영문, 숫자를 포함한 토큰 추출
        const tokens = text
            .toLowerCase()
            .replace(/[^\w\sㄱ-ㅎㅏ-ㅣ가-힣]/g, ' ')
            .split(/\s+/)
            .filter(token => token.length > 1 && !this.stopWords.has(token));
        
        // N-gram 생성 (부분 매칭을 위해)
        const ngrams = [];
        tokens.forEach(token => {
            if (token.length > 2) {
                for (let i = 0; i <= token.length - 2; i++) {
                    ngrams.push(token.substring(i, i + 2));
                }
            }
        });
        
        return [...new Set([...tokens, ...ngrams])];
    }

    /**
     * 검색 실행
     * @param {string} query - 검색 쿼리
     * @param {Object} options - 검색 옵션
     * @returns {Array} 검색 결과
     */
    search(query, options = {}) {
        if (!query || query.trim().length === 0) {
            return this.documents.map((doc, index) => ({
                document: doc,
                score: 1,
                highlights: []
            }));
        }

        const startTime = performance.now();
        
        // 검색 히스토리에 추가
        this.addToHistory(query);
        
        const queryTokens = this.tokenize(query.toLowerCase());
        const results = new Map();
        
        // 각 토큰에 대해 검색
        queryTokens.forEach(token => {
            const matchingDocs = this.findMatchingDocuments(token);
            
            matchingDocs.forEach(docIndex => {
                if (!results.has(docIndex)) {
                    results.set(docIndex, {
                        document: this.documents[docIndex],
                        score: 0,
                        matchedTokens: new Set(),
                        highlights: []
                    });
                }
                
                const result = results.get(docIndex);
                result.matchedTokens.add(token);
                result.score += this.calculateTokenScore(token, query);
            });
        });

        // 결과 정렬 및 하이라이트 생성
        const sortedResults = Array.from(results.values())
            .map(result => {
                result.score = this.calculateFinalScore(result, queryTokens);
                result.highlights = this.generateHighlights(result.document, queryTokens);
                return result;
            })
            .sort((a, b) => b.score - a.score);

        const endTime = performance.now();
        
        console.log(`🔍 검색 완료: "${query}" (${(endTime - startTime).toFixed(2)}ms, ${sortedResults.length}개 결과)`);
        
        return sortedResults;
    }

    /**
     * 토큰과 매칭되는 문서 찾기
     * @param {string} token - 검색 토큰
     * @returns {Set} 매칭되는 문서 인덱스 집합
     */
    findMatchingDocuments(token) {
        const exactMatches = this.searchIndex.get(token) || new Set();
        const fuzzyMatches = new Set();
        
        // 퍼지 매칭 (편집 거리 기반)
        if (token.length > 2) {
            for (const [indexToken, docIndices] of this.searchIndex) {
                if (this.calculateEditDistance(token, indexToken) <= 1) {
                    docIndices.forEach(docIndex => fuzzyMatches.add(docIndex));
                }
            }
        }
        
        return new Set([...exactMatches, ...fuzzyMatches]);
    }

    /**
     * 편집 거리 계산 (Levenshtein Distance)
     * @param {string} str1 - 첫 번째 문자열
     * @param {string} str2 - 두 번째 문자열
     * @returns {number} 편집 거리
     */
    calculateEditDistance(str1, str2) {
        const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));
        
        for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
        for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
        
        for (let j = 1; j <= str2.length; j++) {
            for (let i = 1; i <= str1.length; i++) {
                const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
                matrix[j][i] = Math.min(
                    matrix[j][i - 1] + 1,     // deletion
                    matrix[j - 1][i] + 1,     // insertion
                    matrix[j - 1][i - 1] + indicator // substitution
                );
            }
        }
        
        return matrix[str2.length][str1.length];
    }

    /**
     * 토큰 점수 계산
     * @param {string} token - 토큰
     * @param {string} originalQuery - 원본 쿼리
     * @returns {number} 토큰 점수
     */
    calculateTokenScore(token, originalQuery) {
        let score = 1;
        
        // 완전 일치 보너스
        if (originalQuery.toLowerCase().includes(token)) {
            score += 2;
        }
        
        // 토큰 길이에 따른 가중치
        if (token.length > 3) {
            score += 0.5;
        }
        
        // 희귀도 점수 (역문서 빈도)
        const docFrequency = this.searchIndex.get(token)?.size || 1;
        score += Math.log(this.documents.length / docFrequency);
        
        return score;
    }

    /**
     * 최종 점수 계산
     * @param {Object} result - 검색 결과
     * @param {Array} queryTokens - 쿼리 토큰들
     * @returns {number} 최종 점수
     */
    calculateFinalScore(result, queryTokens) {
        let score = result.score;
        
        // 매칭된 토큰 비율 보너스
        const matchRatio = result.matchedTokens.size / queryTokens.length;
        score *= (1 + matchRatio);
        
        // 문서 타입별 가중치
        const typeWeights = {
            'integrated': 1.5,
            'exchange-rate': 1.2,
            'kospi-close': 1.2,
            'newyork-market-watch': 1.1
        };
        
        const typeWeight = typeWeights[result.document.type] || 1.0;
        score *= typeWeight;
        
        // 최신성 보너스
        const docDate = new Date(result.document.date);
        const daysDiff = (new Date() - docDate) / (1000 * 60 * 60 * 24);
        const recencyBonus = Math.max(0, 1 - daysDiff / 30); // 30일 기준
        score *= (1 + recencyBonus * 0.2);
        
        return score;
    }

    /**
     * 검색 결과 하이라이트 생성
     * @param {Object} document - 문서
     * @param {Array} queryTokens - 쿼리 토큰들
     * @returns {Array} 하이라이트 정보
     */
    generateHighlights(document, queryTokens) {
        const highlights = [];
        const searchableText = this.extractSearchableText(document);
        
        queryTokens.forEach(token => {
            const regex = new RegExp(`(${this.escapeRegExp(token)})`, 'gi');
            const matches = [...searchableText.matchAll(regex)];
            
            matches.forEach(match => {
                const start = Math.max(0, match.index - 20);
                const end = Math.min(searchableText.length, match.index + match[0].length + 20);
                const context = searchableText.substring(start, end);
                
                highlights.push({
                    text: context,
                    matchedText: match[0],
                    position: match.index
                });
            });
        });
        
        return highlights.slice(0, 3); // 최대 3개 하이라이트
    }

    /**
     * 정규식 특수문자 이스케이프
     * @param {string} string - 이스케이프할 문자열
     * @returns {string} 이스케이프된 문자열
     */
    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * 검색 히스토리에 추가
     * @param {string} query - 검색 쿼리
     */
    addToHistory(query) {
        const trimmedQuery = query.trim();
        if (trimmedQuery.length === 0) return;
        
        // 중복 제거
        this.searchHistory = this.searchHistory.filter(item => item.query !== trimmedQuery);
        
        // 새 항목 추가
        this.searchHistory.unshift({
            query: trimmedQuery,
            timestamp: new Date().toISOString(),
            count: 1
        });
        
        // 히스토리 크기 제한
        if (this.searchHistory.length > this.maxHistorySize) {
            this.searchHistory = this.searchHistory.slice(0, this.maxHistorySize);
        }
        
        // 로컬 스토리지에 저장
        try {
            localStorage.setItem('posco-search-history', JSON.stringify(this.searchHistory));
        } catch (e) {
            console.warn('검색 히스토리 저장 실패:', e);
        }
    }

    /**
     * 검색 히스토리 로드
     */
    loadHistory() {
        try {
            const saved = localStorage.getItem('posco-search-history');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('검색 히스토리 로드 실패:', e);
            this.searchHistory = [];
        }
    }

    /**
     * 검색 제안 생성
     * @param {string} partialQuery - 부분 쿼리
     * @returns {Array} 검색 제안 목록
     */
    getSuggestions(partialQuery) {
        if (!partialQuery || partialQuery.length < 2) {
            return this.searchHistory.slice(0, 5).map(item => ({
                text: item.query,
                type: 'history',
                count: item.count
            }));
        }
        
        const suggestions = [];
        const query = partialQuery.toLowerCase();
        
        // 히스토리에서 매칭되는 항목
        this.searchHistory.forEach(item => {
            if (item.query.toLowerCase().includes(query)) {
                suggestions.push({
                    text: item.query,
                    type: 'history',
                    count: item.count
                });
            }
        });
        
        // 문서 제목에서 매칭되는 항목
        const titleSuggestions = new Set();
        this.documents.forEach(doc => {
            const title = doc.title.toLowerCase();
            if (title.includes(query)) {
                const words = title.split(' ').filter(word => 
                    word.includes(query) && word.length > 2
                );
                words.forEach(word => titleSuggestions.add(word));
            }
        });
        
        titleSuggestions.forEach(suggestion => {
            suggestions.push({
                text: suggestion,
                type: 'suggestion'
            });
        });
        
        // 태그에서 매칭되는 항목
        const tagSuggestions = new Set();
        this.documents.forEach(doc => {
            if (doc.tags) {
                doc.tags.forEach(tag => {
                    if (tag.toLowerCase().includes(query)) {
                        tagSuggestions.add(tag);
                    }
                });
            }
        });
        
        tagSuggestions.forEach(suggestion => {
            suggestions.push({
                text: suggestion,
                type: 'tag'
            });
        });
        
        // 중복 제거 및 정렬
        const uniqueSuggestions = suggestions
            .filter((item, index, self) => 
                index === self.findIndex(t => t.text === item.text)
            )
            .sort((a, b) => {
                // 히스토리 항목 우선
                if (a.type === 'history' && b.type !== 'history') return -1;
                if (a.type !== 'history' && b.type === 'history') return 1;
                
                // 사용 횟수 기준 정렬
                if (a.count && b.count) return b.count - a.count;
                
                // 알파벳 순 정렬
                return a.text.localeCompare(b.text);
            })
            .slice(0, 8);
        
        return uniqueSuggestions;
    }

    /**
     * 검색 통계 반환
     * @returns {Object} 검색 통계
     */
    getSearchStats() {
        return {
            totalDocuments: this.documents.length,
            indexSize: this.searchIndex.size,
            historySize: this.searchHistory.length,
            topQueries: this.searchHistory
                .sort((a, b) => b.count - a.count)
                .slice(0, 5)
                .map(item => ({ query: item.query, count: item.count }))
        };
    }

    /**
     * 검색 인덱스 최적화
     */
    optimizeIndex() {
        console.log('🔧 검색 인덱스 최적화 시작...');
        
        // 사용 빈도가 낮은 토큰 제거
        const minFrequency = Math.max(1, Math.floor(this.documents.length * 0.01));
        const tokensToRemove = [];
        
        for (const [token, docIndices] of this.searchIndex) {
            if (docIndices.size < minFrequency && token.length < 3) {
                tokensToRemove.push(token);
            }
        }
        
        tokensToRemove.forEach(token => this.searchIndex.delete(token));
        
        console.log(`✅ 최적화 완료: ${tokensToRemove.length}개 토큰 제거`);
    }

    /**
     * 검색 엔진 초기화
     */
    clear() {
        this.searchIndex.clear();
        this.documents = [];
        console.log('🗑️ 검색 인덱스 초기화 완료');
    }
}

// 전역 검색 엔진 인스턴스
const searchEngine = new SearchEngine();

// 초기화 시 히스토리 로드
searchEngine.loadHistory();

// 검색 엔진 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SearchEngine, searchEngine };
}