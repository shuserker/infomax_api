/**
 * 로그 관련 타입 정의
 */

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  source?: string;
  metadata?: Record<string, any>;
}

export interface LogFilter {
  level?: LogLevel[];
  source?: string[];
  search?: string;
  startTime?: string;
  endTime?: string;
}

export interface LogViewerProps {
  logs: LogEntry[];
  isLoading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  filter?: LogFilter;
  onFilterChange?: (filter: LogFilter) => void;
  height?: number;
  width?: number;
}

export interface VirtualizedLogProps {
  logs: LogEntry[];
  height: number;
  width: number;
  onItemClick?: (log: LogEntry) => void;
  onItemSelect?: (log: LogEntry, isSelected: boolean) => void;
  selectedLogs?: LogEntry[];
  highlightSearch?: string;
}

export interface LogExportOptions {
  format: 'txt' | 'json' | 'csv';
  dateRange?: {
    start: string;
    end: string;
  };
  levels?: LogLevel[];
  maxEntries?: number;
}