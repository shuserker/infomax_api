// Advanced Theme System for POSCO Dashboard

class ThemeSystem {
    constructor() {
        this.themes = new Map([
            ['light', {
                name: '라이트 모드',
                icon: 'fas fa-sun',
                description: '밝은 테마',
                colors: {
                    primary: '#003d82',
                    secondary: '#0066cc',
                    background: '#ffffff',
                    surface: '#f8fafc',
                    text: '#1e293b'
                }
            }],
            ['dark', {
                name: '다크 모드',
                icon: 'fas fa-moon',
                description: '어두운 테마',
                colors: {
                    primary: '#0066cc',
                    secondary: '#3b82f6',
                    background: '#0f172a',
                    surface: '#1e293b',
                    text: '#f1f5f9'
                }
            }],
            ['auto', {
                name: '시스템 설정',
                icon: 'fas fa-desktop',
                description: '시스템 설정에 따라 자동 변경',
                colors: null // 시스템 설정에 따라 동적 결정
            }],
            ['high-contrast', {
                name: '고대비 모드',
                icon: 'fas fa-adjust',
                description: '접근성을 위한 고대비 테마',
                colors: {
                    primary: '#000000',
                    secondary: '#333333',
                    background: '#ffffff',
                    surface: '#f0f0f0',
                    text: '#000000'
                }
            }]
        ]);
        
        this.currentTheme = 'light';
        this.systemPreference = 'light';
        this.transitionDuration = 300;
        this.mediaQuery = null;
        
        this.init();
    }

    init() {
        this.detectSystemPreference();
        this.loadSavedTheme();
        this.setupMediaQueryListener();
        this.enhanceThemeToggle();
        this.createThemeSelector();
        this.setupEventListeners();
        this.applyTheme(this.currentTheme);
    }

    detectSystemPreference() {
        if (window.matchMedia) {
            this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            this.systemPreference = this.mediaQuery.matches ? 'dark' : 'light';
        }
    }

    setupMediaQueryListener() {
        if (this.mediaQuery) {
            this.mediaQuery.addEventListener('change', (e) => {
                this.systemPreference = e.matches ? 'dark' : 'light';
                
                // auto 모드인 경우 시스템 설정에 따라 변경
                if (this.currentTheme === 'auto') {
                    this.applyTheme('auto');
                }
                
                this.notifyThemeChange('system-preference-changed');
            });
        }
    }

    loadSavedTheme() {
        const savedTheme = Storage.get('theme', 'light');
        if (this.themes.has(savedTheme)) {
            this.currentTheme = savedTheme;
        }
    }

    enhanceThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;

        // 기존 토글 버튼 개선
        themeToggle.innerHTML = `
            <i class="${this.getCurrentThemeIcon()}"></i>
            <span class="theme-label">${this.getCurrentThemeName()}</span>
        `;
        
        themeToggle.classList.add('enhanced-theme-toggle');
        
        // 툴팁 추가
        themeToggle.title = `현재: ${this.getCurrentThemeName()}`;
    }

    createThemeSelector() {
        // 고급 테마 선택기 생성
        const themeSelector = DOM.create('div', {
            className: 'theme-selector',
            id: 'themeSelector'
        });

        const themesHTML = Array.from(this.themes.entries()).map(([key, theme]) => `
            <div class="theme-option ${key === this.currentTheme ? 'active' : ''}" data-theme="${key}">
                <div class="theme-preview">
                    <div class="preview-header" style="background-color: ${theme.colors?.background || 'var(--bg-primary)'}">
                        <div class="preview-controls">
                            <div class="preview-dot" style="background-color: ${theme.colors?.primary || 'var(--primary-color)'}"></div>
                            <div class="preview-dot" style="background-color: ${theme.colors?.secondary || 'var(--secondary-color)'}"></div>
                            <div class="preview-dot" style="background-color: ${theme.colors?.text || 'var(--text-primary)'}"></div>
                        </div>
                    </div>
                    <div class="preview-content" style="background-color: ${theme.colors?.surface || 'var(--bg-secondary)'}">
                        <div class="preview-text" style="color: ${theme.colors?.text || 'var(--text-primary)'}"></div>
                        <div class="preview-text" style="color: ${theme.colors?.text || 'var(--text-primary)'}"></div>
                    </div>
                </div>
                <div class="theme-info">
                    <div class="theme-icon">
                        <i class="${theme.icon}"></i>
                    </div>
                    <div class="theme-details">
                        <h4 class="theme-name">${theme.name}</h4>
                        <p class="theme-description">${theme.description}</p>
                    </div>
                    <div class="theme-status">
                        ${key === this.currentTheme ? '<i class="fas fa-check"></i>' : ''}
                    </div>
                </div>
            </div>
        `).join('');

        themeSelector.innerHTML = `
            <div class="theme-selector-header">
                <h3>테마 선택</h3>
                <button class="close-selector" id="closeThemeSelector">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="theme-options">
                ${themesHTML}
            </div>
            <div class="theme-selector-footer">
                <div class="theme-settings">
                    <label class="setting-item">
                        <input type="checkbox" id="smoothTransitions" ${Storage.get('smooth-transitions', true) ? 'checked' : ''}>
                        <span>부드러운 전환 효과</span>
                    </label>
                    <label class="setting-item">
                        <input type="checkbox" id="reduceMotion" ${Storage.get('reduce-motion', false) ? 'checked' : ''}>
                        <span>애니메이션 줄이기</span>
                    </label>
                    <label class="setting-item">
                        <input type="checkbox" id="highContrast" ${Storage.get('high-contrast', false) ? 'checked' : ''}>
                        <span>고대비 모드</span>
                    </label>
                </div>
                <div class="theme-actions">
                    <button class="btn btn-outline btn-sm" id="resetTheme">
                        <i class="fas fa-undo"></i>
                        기본값으로 재설정
                    </button>
                    <button class="btn btn-primary btn-sm" id="applyTheme">
                        <i class="fas fa-check"></i>
                        적용
                    </button>
                </div>
            </div>
        `;

        // 헤더에 추가
        const header = document.querySelector('.header');
        if (header) {
            header.appendChild(themeSelector);
        }
    }

    setupEventListeners() {
        // 기본 테마 토글
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleThemeSelector();
            });
        }

        // 테마 선택기 이벤트
        this.setupThemeSelectorEvents();
        
        // 키보드 단축키
        this.setupKeyboardShortcuts();
        
        // 외부 클릭 시 선택기 닫기
        document.addEventListener('click', (e) => {
            const selector = document.getElementById('themeSelector');
            if (selector && !selector.contains(e.target) && !e.target.closest('#themeToggle')) {
                this.hideThemeSelector();
            }
        });
    }

    setupThemeSelectorEvents() {
        // 테마 옵션 클릭
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-option')) {
                const option = e.target.closest('.theme-option');
                const theme = option.dataset.theme;
                this.selectTheme(theme);
            }
        });

        // 선택기 닫기
        const closeBtn = document.getElementById('closeThemeSelector');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hideThemeSelector();
            });
        }

        // 설정 체크박스
        const smoothTransitions = document.getElementById('smoothTransitions');
        if (smoothTransitions) {
            smoothTransitions.addEventListener('change', (e) => {
                Storage.set('smooth-transitions', e.target.checked);
                this.updateTransitionSettings();
            });
        }

        const reduceMotion = document.getElementById('reduceMotion');
        if (reduceMotion) {
            reduceMotion.addEventListener('change', (e) => {
                Storage.set('reduce-motion', e.target.checked);
                this.updateMotionSettings();
            });
        }

        const highContrast = document.getElementById('highContrast');
        if (highContrast) {
            highContrast.addEventListener('change', (e) => {
                Storage.set('high-contrast', e.target.checked);
                this.updateContrastSettings();
            });
        }

        // 재설정 버튼
        const resetBtn = document.getElementById('resetTheme');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetToDefault();
            });
        }

        // 적용 버튼
        const applyBtn = document.getElementById('applyTheme');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.hideThemeSelector();
            });
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + T: 테마 토글
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.cycleTheme();
            }
            
            // Ctrl/Cmd + Shift + D: 다크모드 토글
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleDarkMode();
            }
        });
    }

    // 테마 적용
    applyTheme(themeName) {
        const theme = this.themes.get(themeName);
        if (!theme) return;

        let actualTheme = themeName;
        
        // auto 모드인 경우 시스템 설정에 따라 결정
        if (themeName === 'auto') {
            actualTheme = this.systemPreference;
        }

        // 전환 애니메이션 시작
        this.startThemeTransition();

        // CSS 변수 업데이트
        this.updateCSSVariables(actualTheme);
        
        // HTML 속성 업데이트
        document.documentElement.setAttribute('data-theme', actualTheme);
        
        // 현재 테마 저장
        this.currentTheme = themeName;
        Storage.set('theme', themeName);
        
        // UI 업데이트
        this.updateThemeToggle();
        this.updateThemeSelector();
        
        // 차트 테마 업데이트
        this.updateChartsTheme();
        
        // 전환 애니메이션 종료
        setTimeout(() => {
            this.endThemeTransition();
        }, this.transitionDuration);
        
        // 테마 변경 알림
        this.notifyThemeChange('theme-applied', { theme: themeName, actualTheme });
        
        console.log(`🎨 테마 적용: ${theme.name} (${actualTheme})`);
    }

    updateCSSVariables(themeName) {
        const theme = this.themes.get(themeName);
        if (!theme || !theme.colors) return;

        const root = document.documentElement;
        
        // 기본 색상 변수 업데이트
        Object.entries(theme.colors).forEach(([key, value]) => {
            root.style.setProperty(`--theme-${key}`, value);
        });
    }

    startThemeTransition() {
        if (!Storage.get('smooth-transitions', true)) return;
        
        document.documentElement.classList.add('theme-transitioning');
        
        // 모든 요소에 전환 효과 적용
        const style = document.createElement('style');
        style.id = 'theme-transition-style';
        style.textContent = `
            * {
                transition: background-color ${this.transitionDuration}ms ease,
                           color ${this.transitionDuration}ms ease,
                           border-color ${this.transitionDuration}ms ease,
                           box-shadow ${this.transitionDuration}ms ease !important;
            }
        `;
        document.head.appendChild(style);
    }

    endThemeTransition() {
        document.documentElement.classList.remove('theme-transitioning');
        
        const transitionStyle = document.getElementById('theme-transition-style');
        if (transitionStyle) {
            transitionStyle.remove();
        }
    }

    updateThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;

        const icon = themeToggle.querySelector('i');
        const label = themeToggle.querySelector('.theme-label');
        
        if (icon) {
            icon.className = this.getCurrentThemeIcon();
        }
        
        if (label) {
            label.textContent = this.getCurrentThemeName();
        }
        
        themeToggle.title = `현재: ${this.getCurrentThemeName()}`;
    }

    updateThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (!selector) return;

        // 활성 테마 옵션 업데이트
        selector.querySelectorAll('.theme-option').forEach(option => {
            const isActive = option.dataset.theme === this.currentTheme;
            option.classList.toggle('active', isActive);
            
            const status = option.querySelector('.theme-status');
            if (status) {
                status.innerHTML = isActive ? '<i class="fas fa-check"></i>' : '';
            }
        });
    }

    updateChartsTheme() {
        // Chart.js 테마 업데이트
        if (window.chartSystem) {
            window.chartSystem.updateChartsForTheme();
        }
    }

    // 테마 선택기 제어
    toggleThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (!selector) return;

        const isVisible = selector.classList.contains('show');
        
        if (isVisible) {
            this.hideThemeSelector();
        } else {
            this.showThemeSelector();
        }
    }

    showThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (!selector) return;

        selector.classList.add('show');
        
        // 첫 번째 테마 옵션에 포커스
        const firstOption = selector.querySelector('.theme-option');
        if (firstOption) {
            firstOption.focus();
        }
    }

    hideThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (!selector) return;

        selector.classList.remove('show');
    }

    selectTheme(themeName) {
        if (!this.themes.has(themeName)) return;
        
        this.applyTheme(themeName);
        
        // 선택 피드백
        this.showNotification(`${this.themes.get(themeName).name}로 변경되었습니다`, 'success');
    }

    // 테마 전환 메서드들
    cycleTheme() {
        const themeKeys = Array.from(this.themes.keys());
        const currentIndex = themeKeys.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeKeys.length;
        const nextTheme = themeKeys[nextIndex];
        
        this.applyTheme(nextTheme);
    }

    toggleDarkMode() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    // 설정 업데이트
    updateTransitionSettings() {
        const enabled = Storage.get('smooth-transitions', true);
        document.documentElement.classList.toggle('no-transitions', !enabled);
    }

    updateMotionSettings() {
        const reduced = Storage.get('reduce-motion', false);
        document.documentElement.classList.toggle('reduce-motion', reduced);
    }

    updateContrastSettings() {
        const highContrast = Storage.get('high-contrast', false);
        document.documentElement.classList.toggle('high-contrast', highContrast);
    }

    // 유틸리티 메서드들
    getCurrentThemeIcon() {
        const theme = this.themes.get(this.currentTheme);
        return theme ? theme.icon : 'fas fa-palette';
    }

    getCurrentThemeName() {
        const theme = this.themes.get(this.currentTheme);
        return theme ? theme.name : '알 수 없음';
    }

    getCurrentThemeColors() {
        const theme = this.themes.get(this.currentTheme);
        if (!theme) return null;
        
        if (this.currentTheme === 'auto') {
            const actualTheme = this.themes.get(this.systemPreference);
            return actualTheme ? actualTheme.colors : null;
        }
        
        return theme.colors;
    }

    isCurrentTheme(themeName) {
        return this.currentTheme === themeName;
    }

    isDarkMode() {
        if (this.currentTheme === 'auto') {
            return this.systemPreference === 'dark';
        }
        return this.currentTheme === 'dark';
    }

    // 테마 관리
    addCustomTheme(name, themeData) {
        this.themes.set(name, themeData);
        this.updateThemeSelector();
    }

    removeCustomTheme(name) {
        if (this.themes.has(name) && name !== 'light' && name !== 'dark') {
            this.themes.delete(name);
            
            if (this.currentTheme === name) {
                this.applyTheme('light');
            }
            
            this.updateThemeSelector();
        }
    }

    resetToDefault() {
        if (confirm('테마 설정을 기본값으로 재설정하시겠습니까?')) {
            // 설정 초기화
            Storage.remove('theme');
            Storage.remove('smooth-transitions');
            Storage.remove('reduce-motion');
            Storage.remove('high-contrast');
            
            // 기본 테마 적용
            this.currentTheme = 'light';
            this.applyTheme('light');
            
            // 설정 UI 업데이트
            const smoothTransitions = document.getElementById('smoothTransitions');
            const reduceMotion = document.getElementById('reduceMotion');
            const highContrast = document.getElementById('highContrast');
            
            if (smoothTransitions) smoothTransitions.checked = true;
            if (reduceMotion) reduceMotion.checked = false;
            if (highContrast) highContrast.checked = false;
            
            this.updateTransitionSettings();
            this.updateMotionSettings();
            this.updateContrastSettings();
            
            this.showNotification('테마 설정이 기본값으로 재설정되었습니다', 'success');
        }
    }

    // 이벤트 시스템
    notifyThemeChange(eventType, data = {}) {
        const event = new CustomEvent('themeChange', {
            detail: {
                type: eventType,
                currentTheme: this.currentTheme,
                isDarkMode: this.isDarkMode(),
                ...data
            }
        });
        
        document.dispatchEvent(event);
    }

    onThemeChange(callback) {
        document.addEventListener('themeChange', callback);
    }

    offThemeChange(callback) {
        document.removeEventListener('themeChange', callback);
    }

    showNotification(message, type) {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        }
    }

    // 테마 내보내기/가져오기
    exportThemeSettings() {
        const settings = {
            currentTheme: this.currentTheme,
            smoothTransitions: Storage.get('smooth-transitions', true),
            reduceMotion: Storage.get('reduce-motion', false),
            highContrast: Storage.get('high-contrast', false),
            customThemes: {}
        };

        // 커스텀 테마 포함
        this.themes.forEach((theme, name) => {
            if (!['light', 'dark', 'auto', 'high-contrast'].includes(name)) {
                settings.customThemes[name] = theme;
            }
        });

        return settings;
    }

    importThemeSettings(settings) {
        try {
            // 커스텀 테마 추가
            if (settings.customThemes) {
                Object.entries(settings.customThemes).forEach(([name, theme]) => {
                    this.addCustomTheme(name, theme);
                });
            }

            // 설정 적용
            if (settings.currentTheme) {
                this.applyTheme(settings.currentTheme);
            }

            Storage.set('smooth-transitions', settings.smoothTransitions ?? true);
            Storage.set('reduce-motion', settings.reduceMotion ?? false);
            Storage.set('high-contrast', settings.highContrast ?? false);

            this.updateTransitionSettings();
            this.updateMotionSettings();
            this.updateContrastSettings();

            this.showNotification('테마 설정을 가져왔습니다', 'success');
            return true;
        } catch (error) {
            this.showNotification('테마 설정 가져오기에 실패했습니다', 'error');
            return false;
        }
    }
}

// 전역 테마 시스템 인스턴스
let themeSystem = null;

// 테마 시스템 초기화 함수
function initializeThemeSystem() {
    themeSystem = new ThemeSystem();
    console.log('🎨 테마 시스템 초기화 완료');
    return themeSystem;
}

// 기존 Theme 객체와의 호환성 유지
if (typeof Theme !== 'undefined') {
    // 기존 Theme 객체를 새로운 시스템으로 대체
    Object.assign(Theme, {
        toggle: () => themeSystem?.toggleDarkMode(),
        set: (theme) => themeSystem?.applyTheme(theme),
        get: () => themeSystem?.currentTheme,
        init: () => initializeThemeSystem()
    });
}

// 테마 시스템 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeSystem, initializeThemeSystem };
}