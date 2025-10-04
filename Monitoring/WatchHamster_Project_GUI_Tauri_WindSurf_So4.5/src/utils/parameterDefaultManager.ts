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
  updateLogic: 'current_date_minus_1' | 'current_date' | 'custom';
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
   * 초기 기본값 설정 (실제 API 문서 기반)
   */
  private setInitialDefaults(): void {
    const now = new Date().toISOString();
    const yesterday = this.getYesterday();

    // 채권 체결정보 API 기본값
    this.setParameterDefault('bond/market/mn_hist', 'stdcd', 'KR103502GE97', false);
    this.setParameterDefault('bond/market/mn_hist', 'market', '장외', false);
    this.setParameterDefault('bond/market/mn_hist', 'startDate', '20250401', false);
    this.setParameterDefault('bond/market/mn_hist', 'endDate', '20250401', false);
    
    // 채권 시가평가 API - 자동 갱신 설정
    this.setParameterDefault('bond/marketvaluation', 'stdcd', 'KR101501DA32', false);
    this.setParameterDefault('bond/marketvaluation', 'bonddate', yesterday, true, {
      enabled: true,
      schedule: {
        daysOfWeek: [1, 2], // 월요일, 화요일
        timeHour: 4,        // 04:00
        timeMinute: 0
      },
      updateLogic: 'current_date_minus_1'
    });

    // 주식 관련 API 기본값
    this.setParameterDefault('stock/hist', 'code', '005930', false);
    this.setParameterDefault('stock/code', 'type', 'EF', false);

    this.saveDefaults();
    console.log('🎯 초기 파라미터 기본값 설정 완료');
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
   * 새로운 값 계산
   */
  private calculateNewValue(logic: string): string {
    switch (logic) {
      case 'current_date_minus_1':
        return this.getYesterday();
      case 'current_date':
        return this.getToday();
      default:
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
