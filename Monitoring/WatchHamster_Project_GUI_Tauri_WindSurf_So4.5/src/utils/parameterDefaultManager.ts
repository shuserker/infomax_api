/**
 * InfoMax API 파라미터 기본값 관리자
 * 수동 편집 및 자동 갱신 기능 제공
 */

export interface ParameterDefault {
  apiPath: string;
  paramName: string;
  value: string;
  lastUpdated: string;
  isAutoManaged: boolean;
  autoUpdateRule?: AutoUpdateRule;
}

export interface AutoUpdateRule {
  enabled: boolean;
  schedule: {
    daysOfWeek: number[]; // 0=일요일, 1=월요일, 2=화요일, etc.
    timeHour: number;     // 0-23
    timeMinute: number;   // 0-59
  };
  updateLogic: 
    // 기본 날짜
    | 'current_date_minus_1'      // 어제 날짜 (당일-1)
    | 'current_date'              // 오늘 날짜
    | 'current_date_minus_2'      // 그제 날짜 (당일-2)
    | 'current_date_minus_3'      // 3일 전
    // 주간 단위
    | 'last_week_start'           // 지난주 월요일
    | 'last_week_end'             // 지난주 금요일
    | 'current_week_start'        // 이번주 월요일
    | 'current_week_end'          // 이번주 금요일
    | 'last_business_day'         // 최근 영업일
    // 월간 단위
    | 'current_month_start'       // 이번달 1일
    | 'current_month_end'         // 이번달 말일
    | 'last_month_start'          // 지난달 1일
    | 'last_month_end'            // 지난달 말일
    | 'next_month_start'          // 다음달 1일
    // 분기 단위
    | 'current_quarter_start'     // 이번 분기 시작일
    | 'current_quarter_end'       // 이번 분기 종료일
    | 'last_quarter_start'        // 지난 분기 시작일
    | 'last_quarter_end'          // 지난 분기 종료일
    // 년간 단위
    | 'current_year_start'        // 올해 1월 1일
    | 'current_year_end'          // 올해 12월 31일
    | 'last_year_start'           // 작년 1월 1일
    | 'last_year_end'             // 작년 12월 31일
    // 상대적 날짜
    | 'days_ago_7'                // 1주일 전
    | 'days_ago_30'               // 1개월 전
    | 'days_ago_90'               // 3개월 전
    | 'days_ago_180'              // 6개월 전
    | 'days_ago_365'              // 1년 전
    // 특수 로직
    | 'trading_market_priority'   // 거래시장 우선순위
    | 'rotate_keywords'           // 키워드 로테이션
    | 'next_future_month'         // 다음 선물 만료월
    | 'auto_smart_date'           // 스마트 자동 날짜
    | 'custom';                   // 사용자 정의
  customLogic?: string;
}

export interface ParameterDefaults {
  [apiPath: string]: {
    [paramName: string]: ParameterDefault;
  };
}

const STORAGE_KEY = 'infomax_parameter_defaults';
const AUTO_UPDATE_CHECK_KEY = 'infomax_auto_update_last_check';

class ParameterDefaultManager {
  private defaults: ParameterDefaults = {};
  private checkInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.loadDefaults();
    this.startAutoUpdateChecker();
  }

  /**
   * 로컬 스토리지에서 기본값 로드
   */
  private loadDefaults(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        this.defaults = JSON.parse(stored);
        console.log('🔧 파라미터 기본값 로드됨:', Object.keys(this.defaults).length, '개 API');
      } else {
        // 초기 기본값 설정
        this.setInitialDefaults();
      }
    } catch (error) {
      console.error('❌ 파라미터 기본값 로드 실패:', error);
      this.setInitialDefaults();
    }
  }

  /**
   * 초기 기본값 설정 (실용적인 자동갱신 규칙 포함)
   */
  private setInitialDefaults(): void {
    const yesterday = this.getYesterday();
    const today = this.getToday();
    const lastWeekStart = this.getLastWeekStart();
    const lastWeekEnd = this.getLastWeekEnd();
    const lastMonth = this.getLastMonth();

    // 채권 관련 API - 실용적 자동갱신
    this.setParameterDefault('bond/market/mn_hist', 'stdcd', 'KR103502GE97', false);
    this.setParameterDefault('bond/market/mn_hist', 'market', '장외', false);
    this.setParameterDefault('bond/market/mn_hist', 'startDate', lastWeekStart, true, {
      enabled: true,
      schedule: { daysOfWeek: [1], timeHour: 1, timeMinute: 0 }, // 매주 월요일 01:00
      updateLogic: 'last_week_start'
    });
    this.setParameterDefault('bond/market/mn_hist', 'endDate', yesterday, true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 1, timeMinute: 0 },
      updateLogic: 'current_date_minus_1'
    });
    this.setParameterDefault('bond/marketvaluation', 'stdcd', 'KR101501DA32', false);
    this.setParameterDefault('bond/marketvaluation', 'bonddate', yesterday, true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5, 6, 0], timeHour: 0, timeMinute: 30 }, // 매일 00:30
      updateLogic: 'current_date_minus_1'
    });

    // 주식 일별 API - 스마트 날짜 갱신
    this.setParameterDefault('stock/hist', 'code', '005930', false);
    this.setParameterDefault('stock/hist', 'startDate', lastMonth, true, {
      enabled: true,
      schedule: { daysOfWeek: [1], timeHour: 2, timeMinute: 0 }, // 매주 월요일 02:00
      updateLogic: 'last_month_start'
    });
    this.setParameterDefault('stock/hist', 'endDate', yesterday, true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 0, timeMinute: 15 }, // 평일 00:15
      updateLogic: 'current_date_minus_1'
    });

    // 주식 코드 검색 - 분기별 기본값 갱신
    this.setParameterDefault('stock/code', 'type', 'ST', false);
    this.setParameterDefault('stock/code', 'market', '1', true, {
      enabled: true,
      schedule: { daysOfWeek: [1], timeHour: 3, timeMinute: 0 }, // 매주 월요일 03:00  
      updateLogic: 'trading_market_priority'
    });

    // ETF 관련 - NAV 데이터 자동갱신
    this.setParameterDefault('etf/hist', 'code', '069500', false);
    this.setParameterDefault('etf/intra', 'code', '069500', false);

    // 외환 관련 - 매일 환율 갱신
    this.setParameterDefault('fx/exchangerate/hist', 'currency', 'USD', false);
    this.setParameterDefault('fx/exchangerate/hist', 'date', yesterday, true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 9, timeMinute: 30 }, // 평일 09:30 (장 시작 후)
      updateLogic: 'current_date_minus_1'
    });

    // 뉴스 검색 - 매일 키워드 로테이션
    this.setParameterDefault('news/search', 'keyword', '코스피', true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 6, timeMinute: 0 }, // 평일 06:00
      updateLogic: 'rotate_keywords'
    });
    this.setParameterDefault('news/search', 'date', today, true, {
      enabled: true,
      schedule: { daysOfWeek: [1, 2, 3, 4, 5, 6, 0], timeHour: 0, timeMinute: 5 }, // 매일 00:05
      updateLogic: 'current_date'
    });

    // 선물/옵션 - 만료일 기준 자동 갱신
    this.setParameterDefault('future/code', 'month', this.getCurrentFutureMonth(), true, {
      enabled: true,
      schedule: { daysOfWeek: [4], timeHour: 16, timeMinute: 0 }, // 매주 목요일 16:00 (만료일 체크)
      updateLogic: 'next_future_month'
    });

    this.saveDefaults();
    console.log('🎯 실용적인 자동갱신 규칙으로 초기값 설정 완료');
  }

  /**
   * 파라미터 기본값 설정
   */
  setParameterDefault(
    apiPath: string, 
    paramName: string, 
    value: string, 
    isAutoManaged: boolean = false,
    autoUpdateRule?: AutoUpdateRule
  ): void {
    if (!this.defaults[apiPath]) {
      this.defaults[apiPath] = {};
    }

    this.defaults[apiPath][paramName] = {
      apiPath,
      paramName,
      value,
      lastUpdated: new Date().toISOString(),
      isAutoManaged,
      autoUpdateRule
    };

    this.saveDefaults();
  }

  /**
   * 파라미터 기본값 가져오기
   */
  getParameterDefault(apiPath: string, paramName: string): string | undefined {
    return this.defaults[apiPath]?.[paramName]?.value;
  }

  /**
   * API별 모든 기본값 가져오기
   */
  getApiDefaults(apiPath: string): Record<string, string> {
    const apiDefaults = this.defaults[apiPath];
    if (!apiDefaults) return {};

    const result: Record<string, string> = {};
    Object.entries(apiDefaults).forEach(([paramName, paramDefault]) => {
      result[paramName] = paramDefault.value;
    });

    return result;
  }

  /**
   * 모든 기본값 가져오기 (관리 UI용)
   */
  getAllDefaults(): ParameterDefaults {
    return { ...this.defaults };
  }

  /**
   * 기본값을 로컬 스토리지에 저장
   */
  private saveDefaults(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.defaults));
    } catch (error) {
      console.error('❌ 파라미터 기본값 저장 실패:', error);
    }
  }

  /**
   * 자동 갱신 체커 시작
   */
  private startAutoUpdateChecker(): void {
    // 5분마다 자동 갱신 체크
    this.checkInterval = setInterval(() => {
      this.checkAndPerformAutoUpdates();
    }, 5 * 60 * 1000);

    // 즉시 한 번 체크
    setTimeout(() => this.checkAndPerformAutoUpdates(), 1000);
  }

  /**
   * 자동 갱신 체크 및 실행
   */
  private checkAndPerformAutoUpdates(): void {
    const now = new Date();
    const lastCheck = localStorage.getItem(AUTO_UPDATE_CHECK_KEY);
    const lastCheckDate = lastCheck ? new Date(lastCheck) : new Date(0);

    // 마지막 체크가 하루 이상 전이거나, 현재 시간이 스케줄과 일치하는 경우만 실행
    const shouldCheck = (now.getTime() - lastCheckDate.getTime()) > 60 * 60 * 1000; // 1시간 이상 차이

    if (!shouldCheck) return;

    let updatedCount = 0;

    Object.values(this.defaults).forEach(apiDefaults => {
      Object.values(apiDefaults).forEach(paramDefault => {
        if (paramDefault.isAutoManaged && paramDefault.autoUpdateRule?.enabled) {
          if (this.shouldUpdateNow(now, paramDefault.autoUpdateRule)) {
            const newValue = this.calculateNewValue(paramDefault.autoUpdateRule.updateLogic);
            if (newValue !== paramDefault.value) {
              paramDefault.value = newValue;
              paramDefault.lastUpdated = now.toISOString();
              updatedCount++;
              console.log(`🔄 자동 갱신: ${paramDefault.apiPath}.${paramDefault.paramName} = ${newValue}`);
            }
          }
        }
      });
    });

    if (updatedCount > 0) {
      this.saveDefaults();
      console.log(`✅ 자동 갱신 완료: ${updatedCount}개 파라미터 업데이트`);
    }

    localStorage.setItem(AUTO_UPDATE_CHECK_KEY, now.toISOString());
  }

  /**
   * 현재 시점에 업데이트해야 하는지 확인
   */
  private shouldUpdateNow(now: Date, rule: AutoUpdateRule): boolean {
    const currentDay = now.getDay(); // 0=일요일, 1=월요일, etc.
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    // 지정된 요일인지 확인
    if (!rule.schedule.daysOfWeek.includes(currentDay)) {
      return false;
    }

    // 지정된 시간인지 확인 (±5분 허용)
    const targetTime = rule.schedule.timeHour * 60 + rule.schedule.timeMinute;
    const currentTime = currentHour * 60 + currentMinute;
    const timeDiff = Math.abs(currentTime - targetTime);

    return timeDiff <= 5; // 5분 이내
  }

  /**
   * 새로운 값 계산 (대폭 확장된 로직)
   */
  private calculateNewValue(logic: string): string {
    // === 동적 D+n, D-n 처리 ===
    if (logic === 'current_date') {
      return this.getToday();
    }
    
    // current_date_minus_숫자 또는 current_date_plus_숫자 형태 파싱
    const minusMatch = logic.match(/^current_date_minus_(\d+)$/);
    if (minusMatch) {
      const days = parseInt(minusMatch[1]);
      return this.getDaysAgo(days);
    }
    
    const plusMatch = logic.match(/^current_date_plus_(\d+)$/);
    if (plusMatch) {
      const days = parseInt(plusMatch[1]);
      return this.getDaysLater(days);
    }

    switch (logic) {
      
      // === 주간 단위 ===
      case 'last_week_start':
        return this.getLastWeekStart();
      case 'last_week_end':
        return this.getLastWeekEnd();
      case 'current_week_start':
        return this.getCurrentWeekStart();
      case 'current_week_end':
        return this.getCurrentWeekEnd();
      case 'last_business_day':
        return this.getLastBusinessDay();
      
      // === 월간 단위 ===
      case 'current_month_start':
        return this.getCurrentMonthStart();
      case 'current_month_end':
        return this.getCurrentMonthEnd();
      case 'last_month_start':
        return this.getLastMonthStart();
      case 'last_month_end':
        return this.getLastMonthEnd();
      case 'next_month_start':
        return this.getNextMonthStart();
      
      // === 분기 단위 ===
      case 'current_quarter_start':
        return this.getCurrentQuarterStart();
      case 'current_quarter_end':
        return this.getCurrentQuarterEnd();
      case 'last_quarter_start':
        return this.getLastQuarterStart();
      case 'last_quarter_end':
        return this.getLastQuarterEnd();
      
      // === 년간 단위 ===
      case 'current_year_start':
        return this.getCurrentYearStart();
      case 'current_year_end':
        return this.getCurrentYearEnd();
      case 'last_year_start':
        return this.getLastYearStart();
      case 'last_year_end':
        return this.getLastYearEnd();
      
      // === 상대적 날짜 ===
      case 'days_ago_7':
        return this.getDaysAgo(7);
      case 'days_ago_30':
        return this.getDaysAgo(30);
      case 'days_ago_90':
        return this.getDaysAgo(90);
      case 'days_ago_180':
        return this.getDaysAgo(180);
      case 'days_ago_365':
        return this.getDaysAgo(365);
      
      // === 특수 로직 ===
      case 'trading_market_priority':
        return this.getTradingMarketPriority();
      case 'rotate_keywords':
        return this.getRotateKeywords();
      case 'next_future_month':
        return this.getNextFutureMonth();
      case 'auto_smart_date':
        return this.getAutoSmartDate();
      
      default:
        console.warn(`⚠️ 알 수 없는 갱신 로직: ${logic}, 기본값(어제 날짜) 사용`);
        return this.getYesterday();
    }
  }

  /**
   * 어제 날짜를 YYYYMMDD 형식으로 반환
   */
  private getYesterday(): string {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return this.formatDate(yesterday);
  }

  /**
   * 오늘 날짜를 YYYYMMDD 형식으로 반환
   */
  private getToday(): string {
    return this.formatDate(new Date());
  }

  /**
   * 날짜를 YYYYMMDD 형식으로 포맷
   */
  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
  }

  // ========== 확장된 날짜 계산 함수들 ==========
  
  /**
   * N일 전 날짜
   */
  private getDaysAgo(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return this.formatDate(date);
  }

  /**
   * N일 후 날짜
   */
  private getDaysLater(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return this.formatDate(date);
  }

  /**
   * 지난주 월요일
   */
  private getLastWeekStart(): string {
    const date = new Date();
    const dayOfWeek = date.getDay();
    const daysToLastMonday = dayOfWeek === 0 ? 13 : dayOfWeek + 6;
    date.setDate(date.getDate() - daysToLastMonday);
    return this.formatDate(date);
  }

  /**
   * 지난주 금요일
   */
  private getLastWeekEnd(): string {
    const date = new Date();
    const dayOfWeek = date.getDay();
    const daysToLastFriday = dayOfWeek === 0 ? 9 : dayOfWeek + 2;
    date.setDate(date.getDate() - daysToLastFriday);
    return this.formatDate(date);
  }

  /**
   * 이번주 월요일
   */
  private getCurrentWeekStart(): string {
    const date = new Date();
    const dayOfWeek = date.getDay();
    const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    date.setDate(date.getDate() - daysToMonday);
    return this.formatDate(date);
  }

  /**
   * 이번주 금요일
   */
  private getCurrentWeekEnd(): string {
    const date = new Date();
    const dayOfWeek = date.getDay();
    const daysToFriday = dayOfWeek === 0 ? 2 : 5 - dayOfWeek;
    date.setDate(date.getDate() + daysToFriday);
    return this.formatDate(date);
  }

  /**
   * 최근 영업일 (토,일 제외)
   */
  private getLastBusinessDay(): string {
    const date = new Date();
    date.setDate(date.getDate() - 1); // 어제부터 시작
    
    while (date.getDay() === 0 || date.getDay() === 6) {
      date.setDate(date.getDate() - 1);
    }
    return this.formatDate(date);
  }

  /**
   * 이번달 1일
   */
  private getCurrentMonthStart(): string {
    const date = new Date();
    date.setDate(1);
    return this.formatDate(date);
  }

  /**
   * 이번달 말일
   */
  private getCurrentMonthEnd(): string {
    const date = new Date();
    date.setMonth(date.getMonth() + 1, 0); // 다음달 0일 = 이번달 마지막날
    return this.formatDate(date);
  }

  /**
   * 지난달 1일
   */
  private getLastMonthStart(): string {
    const date = new Date();
    date.setMonth(date.getMonth() - 1, 1);
    return this.formatDate(date);
  }

  /**
   * 지난달 말일
   */
  private getLastMonthEnd(): string {
    const date = new Date();
    date.setDate(0); // 이번달 0일 = 지난달 마지막날
    return this.formatDate(date);
  }

  /**
   * 다음달 1일
   */
  private getNextMonthStart(): string {
    const date = new Date();
    date.setMonth(date.getMonth() + 1, 1);
    return this.formatDate(date);
  }

  /**
   * 이번 분기 시작일
   */
  private getCurrentQuarterStart(): string {
    const date = new Date();
    const quarter = Math.floor(date.getMonth() / 3);
    date.setMonth(quarter * 3, 1);
    return this.formatDate(date);
  }

  /**
   * 이번 분기 종료일
   */
  private getCurrentQuarterEnd(): string {
    const date = new Date();
    const quarter = Math.floor(date.getMonth() / 3);
    date.setMonth((quarter + 1) * 3, 0);
    return this.formatDate(date);
  }

  /**
   * 지난 분기 시작일
   */
  private getLastQuarterStart(): string {
    const date = new Date();
    const quarter = Math.floor(date.getMonth() / 3);
    const lastQuarter = quarter === 0 ? 3 : quarter - 1;
    const year = quarter === 0 ? date.getFullYear() - 1 : date.getFullYear();
    date.setFullYear(year);
    date.setMonth(lastQuarter * 3, 1);
    return this.formatDate(date);
  }

  /**
   * 지난 분기 종료일
   */
  private getLastQuarterEnd(): string {
    const date = new Date();
    const quarter = Math.floor(date.getMonth() / 3);
    const lastQuarter = quarter === 0 ? 3 : quarter - 1;
    const year = quarter === 0 ? date.getFullYear() - 1 : date.getFullYear();
    date.setFullYear(year);
    date.setMonth((lastQuarter + 1) * 3, 0);
    return this.formatDate(date);
  }

  /**
   * 올해 1월 1일
   */
  private getCurrentYearStart(): string {
    const date = new Date();
    date.setMonth(0, 1);
    return this.formatDate(date);
  }

  /**
   * 올해 12월 31일
   */
  private getCurrentYearEnd(): string {
    const date = new Date();
    date.setMonth(11, 31);
    return this.formatDate(date);
  }

  /**
   * 작년 1월 1일
   */
  private getLastYearStart(): string {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 1);
    date.setMonth(0, 1);
    return this.formatDate(date);
  }

  /**
   * 작년 12월 31일
   */
  private getLastYearEnd(): string {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 1);
    date.setMonth(11, 31);
    return this.formatDate(date);
  }

  /**
   * 거래시장 우선순위 로직
   */
  private getTradingMarketPriority(): string {
    const now = new Date();
    const hour = now.getHours();
    
    // 장중(09:00-15:30): 코스피 우선
    if (hour >= 9 && hour < 16) {
      return '1'; // 코스피
    }
    // 장후: 코스닥 우선
    return '2'; // 코스닥
  }

  /**
   * 키워드 로테이션 로직
   */
  private getRotateKeywords(): string {
    const keywords = ['코스피', '코스닥', '삼성전자', '반도체', 'SK하이닉스', 'LG에너지', '현대차', 'NAVER', '카카오', '배당'];
    const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
    return keywords[dayOfYear % keywords.length];
  }

  /**
   * 다음 선물 만료월
   */
  private getNextFutureMonth(): string {
    const date = new Date();
    const currentMonth = date.getMonth() + 1;
    
    // 선물은 3,6,9,12월이 메인 만료월
    const expiryMonths = [3, 6, 9, 12];
    const nextExpiry = expiryMonths.find(month => month > currentMonth) || (expiryMonths[0] + 12);
    
    if (nextExpiry > 12) {
      date.setFullYear(date.getFullYear() + 1);
      return (nextExpiry - 12).toString().padStart(2, '0');
    }
    
    return nextExpiry.toString().padStart(2, '0');
  }

  /**
   * 스마트 자동 날짜 (컨텍스트에 따라 적절한 날짜 선택)
   */
  private getAutoSmartDate(): string {
    const now = new Date();
    const hour = now.getHours();
    const dayOfWeek = now.getDay();
    
    // 주말이면 지난주 금요일
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      return this.getLastWeekEnd();
    }
    
    // 장시작 전(09:00 이전)이면 전일
    if (hour < 9) {
      return this.getLastBusinessDay();
    }
    
    // 그외는 당일
    return this.getToday();
  }

  /**
   * 현재 선물 만료월 (YYMM 형식)
   */
  private getCurrentFutureMonth(): string {
    const date = new Date();
    const year = date.getFullYear().toString().slice(2);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    return year + month;
  }

  /**
   * 지난달 시작 (호환성)
   */
  private getLastMonth(): string {
    return this.getLastMonthStart();
  }

  /**
   * 파라미터 기본값 삭제
   */
  removeParameterDefault(apiPath: string, paramName: string): void {
    if (this.defaults[apiPath]?.[paramName]) {
      delete this.defaults[apiPath][paramName];
      
      // API에 파라미터가 없으면 API 자체도 삭제
      if (Object.keys(this.defaults[apiPath]).length === 0) {
        delete this.defaults[apiPath];
      }
      
      this.saveDefaults();
    }
  }

  /**
   * 모든 기본값 초기화
   */
  resetAllDefaults(): void {
    this.defaults = {};
    localStorage.removeItem(STORAGE_KEY);
    this.setInitialDefaults();
  }

  /**
   * 자동 갱신 체커 중지
   */
  destroy(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }
}

// 싱글톤 인스턴스
export const parameterDefaultManager = new ParameterDefaultManager();
