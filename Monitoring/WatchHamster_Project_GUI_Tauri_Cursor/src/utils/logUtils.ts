import { format, parseISO } from 'date-fns';
import { LogEntry, LogLevel, LogFilter } from '../types/logs';

/**
 * 로그 레벨별 색상 매핑
 */
export const LOG_LEVEL_COLORS: Record<LogLevel, string> = {
  DEBUG: '#718096',    // gray.500
  INFO: '#3182CE',     // blue.500
  WARN: '#D69E2E',     // yellow.500
  ERROR: '#E53E3E',    // red.500
  CRITICAL: '#9B2C2C', // red.700
};

/**
 * 로그 레벨별 배경색 매핑
 */
export const LOG_LEVEL_BG_COLORS: Record<LogLevel, string> = {
  DEBUG: '#F7FAFC',    // gray.50
  INFO: '#EBF8FF',     // blue.50
  WARN: '#FFFBEB',     // yellow.50
  ERROR: '#FED7D7',    // red.100
  CRITICAL: '#FEB2B2', // red.200
};

/**
 * 로그 메시지에서 ANSI 색상 코드 제거
 */
export const stripAnsiCodes = (text: string): string => {
  // ANSI 색상 코드 정규식
  const ansiRegex = /\x1b\[[0-9;]*m/g;
  return text.replace(ansiRegex, '');
};

/**
 * 로그 메시지 포맷팅
 */
export const formatLogMessage = (log: LogEntry): string => {
  const timestamp = format(parseISO(log.timestamp), 'yyyy-MM-dd HH:mm:ss.SSS');
  const level = log.level.padEnd(8);
  const source = log.source ? `[${log.source}]` : '';
  
  return `${timestamp} ${level} ${source} ${stripAnsiCodes(log.message)}`;
};

/**
 * 로그 엔트리 필터링
 */
export const filterLogs = (logs: LogEntry[], filter: LogFilter): LogEntry[] => {
  return logs.filter(log => {
    // 레벨 필터
    if (filter.level && filter.level.length > 0 && !filter.level.includes(log.level)) {
      return false;
    }

    // 소스 필터
    if (filter.source && filter.source.length > 0 && log.source && !filter.source.includes(log.source)) {
      return false;
    }

    // 검색 필터
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      const messageMatch = log.message.toLowerCase().includes(searchLower);
      const sourceMatch = log.source?.toLowerCase().includes(searchLower) || false;
      
      if (!messageMatch && !sourceMatch) {
        return false;
      }
    }

    // 시간 범위 필터
    if (filter.startTime && log.timestamp < filter.startTime) {
      return false;
    }
    
    if (filter.endTime && log.timestamp > filter.endTime) {
      return false;
    }

    return true;
  });
};

/**
 * 검색어 하이라이트
 */
export const highlightSearchTerm = (text: string, searchTerm: string): string => {
  if (!searchTerm) return text;
  
  const regex = new RegExp(`(${searchTerm})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

/**
 * 로그 레벨 우선순위 (높을수록 중요)
 */
export const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
  DEBUG: 1,
  INFO: 2,
  WARN: 3,
  ERROR: 4,
  CRITICAL: 5,
};

/**
 * 로그 엔트리 정렬
 */
export const sortLogsByTimestamp = (logs: LogEntry[], ascending = false): LogEntry[] => {
  return [...logs].sort((a, b) => {
    const timeA = new Date(a.timestamp).getTime();
    const timeB = new Date(b.timestamp).getTime();
    
    return ascending ? timeA - timeB : timeB - timeA;
  });
};

/**
 * 로그 통계 계산
 */
export const calculateLogStats = (logs: LogEntry[]) => {
  const stats = {
    total: logs.length,
    byLevel: {} as Record<LogLevel, number>,
    bySource: {} as Record<string, number>,
    timeRange: {
      start: '',
      end: '',
    },
  };

  logs.forEach(log => {
    // 레벨별 통계
    stats.byLevel[log.level] = (stats.byLevel[log.level] || 0) + 1;
    
    // 소스별 통계
    if (log.source) {
      stats.bySource[log.source] = (stats.bySource[log.source] || 0) + 1;
    }
  });

  // 시간 범위 계산
  if (logs.length > 0) {
    const sortedLogs = sortLogsByTimestamp(logs, true);
    stats.timeRange.start = sortedLogs[0].timestamp;
    stats.timeRange.end = sortedLogs[sortedLogs.length - 1].timestamp;
  }

  return stats;
};

/**
 * 로그 데이터 내보내기 포맷팅
 */
export const formatLogsForExport = (logs: LogEntry[], format: 'txt' | 'json' | 'csv'): string => {
  switch (format) {
    case 'txt':
      return logs.map(formatLogMessage).join('\n');
      
    case 'json':
      return JSON.stringify(logs, null, 2);
      
    case 'csv':
      const headers = 'Timestamp,Level,Source,Message';
      const rows = logs.map(log => {
        const timestamp = format(parseISO(log.timestamp), 'yyyy-MM-dd HH:mm:ss.SSS');
        const message = stripAnsiCodes(log.message).replace(/"/g, '""'); // CSV 이스케이프
        return `"${timestamp}","${log.level}","${log.source || ''}","${message}"`;
      });
      return [headers, ...rows].join('\n');
      
    default:
      throw new Error(`지원하지 않는 내보내기 형식: ${format}`);
  }
};

/**
 * 로그 범위 선택 유틸리티
 */
export const selectLogsByTimeRange = (
  logs: LogEntry[], 
  startTime: string, 
  endTime: string
): LogEntry[] => {
  const start = new Date(startTime).getTime();
  const end = new Date(endTime).getTime();
  
  return logs.filter(log => {
    const logTime = new Date(log.timestamp).getTime();
    return logTime >= start && logTime <= end;
  });
};

/**
 * 로그 범위 선택 (인덱스 기반)
 */
export const selectLogsByRange = (
  logs: LogEntry[], 
  startIndex: number, 
  endIndex: number
): LogEntry[] => {
  const start = Math.max(0, startIndex);
  const end = Math.min(logs.length - 1, endIndex);
  
  return logs.slice(start, end + 1);
};

/**
 * 로그 압축 (중복 제거 및 요약)
 */
export const compressLogs = (logs: LogEntry[], options: {
  removeDuplicates?: boolean;
  summarizeRepeated?: boolean;
  maxRepeatedCount?: number;
} = {}): LogEntry[] => {
  const {
    removeDuplicates = false,
    summarizeRepeated = true,
    maxRepeatedCount = 5,
  } = options;

  if (!removeDuplicates && !summarizeRepeated) {
    return logs;
  }

  const result: LogEntry[] = [];
  const messageMap = new Map<string, { count: number; firstLog: LogEntry; lastTimestamp: string }>();

  for (const log of logs) {
    const messageKey = `${log.level}:${stripAnsiCodes(log.message)}`;
    
    if (messageMap.has(messageKey)) {
      const existing = messageMap.get(messageKey)!;
      existing.count++;
      existing.lastTimestamp = log.timestamp;
      
      if (existing.count <= maxRepeatedCount) {
        result.push(log);
      } else if (existing.count === maxRepeatedCount + 1 && summarizeRepeated) {
        // 요약 메시지 추가
        result.push({
          ...existing.firstLog,
          message: `${existing.firstLog.message} (이 메시지가 ${existing.count}회 반복됨)`,
          timestamp: existing.lastTimestamp,
        });
      }
    } else {
      messageMap.set(messageKey, {
        count: 1,
        firstLog: log,
        lastTimestamp: log.timestamp,
      });
      result.push(log);
    }
  }

  return result;
};

/**
 * 로그 파일 크기 추정
 */
export const estimateLogFileSize = (logs: LogEntry[], format: 'txt' | 'json' | 'csv'): number => {
  if (logs.length === 0) return 0;
  
  // 샘플 로그로 크기 추정
  const sampleSize = Math.min(100, logs.length);
  const sampleLogs = logs.slice(0, sampleSize);
  const sampleData = formatLogsForExport(sampleLogs, format);
  const avgSizePerLog = sampleData.length / sampleSize;
  
  return Math.round(avgSizePerLog * logs.length);
};

/**
 * 로그 내보내기 메타데이터 생성
 */
export const generateExportMetadata = (logs: LogEntry[], filter?: LogFilter) => {
  const stats = calculateLogStats(logs);
  const now = new Date();
  
  return {
    exportedAt: now.toISOString(),
    totalLogs: logs.length,
    timeRange: stats.timeRange,
    levelDistribution: stats.byLevel,
    sourceDistribution: stats.bySource,
    filter: filter || null,
    exportedBy: 'WatchHamster Tauri UI',
    version: '1.0.0',
  };
};

/**
 * 로그 내보내기 (메타데이터 포함)
 */
export const exportLogsWithMetadata = (
  logs: LogEntry[], 
  format: 'txt' | 'json' | 'csv',
  includeMetadata = true,
  filter?: LogFilter
): string => {
  const logData = formatLogsForExport(logs, format);
  
  if (!includeMetadata || format !== 'json') {
    return logData;
  }
  
  // JSON 형식일 때만 메타데이터 포함
  const metadata = generateExportMetadata(logs, filter);
  
  return JSON.stringify({
    metadata,
    logs: JSON.parse(logData),
  }, null, 2);
};

/**
 * 로그 공유용 요약 생성
 */
export const generateLogSummary = (logs: LogEntry[], maxLength = 500): string => {
  if (logs.length === 0) {
    return '공유할 로그가 없습니다.';
  }
  
  const stats = calculateLogStats(logs);
  const errorLogs = logs.filter(log => log.level === 'ERROR' || log.level === 'CRITICAL');
  
  let summary = `로그 요약 (총 ${logs.length}개)\n`;
  summary += `시간 범위: ${new Date(stats.timeRange.start).toLocaleString()} ~ ${new Date(stats.timeRange.end).toLocaleString()}\n`;
  summary += `레벨별 분포: ${Object.entries(stats.byLevel).map(([level, count]) => `${level}(${count})`).join(', ')}\n`;
  
  if (errorLogs.length > 0) {
    summary += `\n주요 오류 (${Math.min(3, errorLogs.length)}개):\n`;
    errorLogs.slice(0, 3).forEach((log, index) => {
      const timestamp = new Date(log.timestamp).toLocaleString();
      const message = stripAnsiCodes(log.message).substring(0, 100);
      summary += `${index + 1}. [${timestamp}] ${log.level}: ${message}${message.length > 100 ? '...' : ''}\n`;
    });
  }
  
  // 길이 제한
  if (summary.length > maxLength) {
    summary = summary.substring(0, maxLength - 3) + '...';
  }
  
  return summary;
};