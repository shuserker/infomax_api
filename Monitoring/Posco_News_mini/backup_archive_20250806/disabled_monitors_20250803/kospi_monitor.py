#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kospi_monitor.py - 비활성화됨

이 개별 모니터링 스크립트는 통합 리포트 시스템으로 전환되면서 비활성화되었습니다.

비활성화 일시: 2025-08-03 11:36:00
대체 시스템: 통합 리포트 시스템 (integrated_report_scheduler.py)

사용법:
- 통합 리포트 생성: python3 integrated_report_scheduler.py
- 수동 리포트 생성: python3 reports/integrated_report_generator.py

원본 파일 위치: kospi_monitor.py.disabled
"""

import sys
from datetime import datetime

def main():
    print("🚫 이 스크립트는 비활성화되었습니다.")
    print(f"📅 비활성화 일시: 2025-08-03 11:36:00")
    print()
    print("🔄 POSCO 리포트 시스템이 통합 리포트 시스템으로 전환되었습니다.")
    print()
    print("✅ 대신 사용할 수 있는 명령어:")
    print("   • 통합 리포트 생성: python3 integrated_report_scheduler.py")
    print("   • 수동 리포트 생성: python3 reports/integrated_report_generator.py")
    print("   • 메타데이터 업데이트: python3 metadata_reset_manager.py")
    print()
    print("📋 더 자세한 정보는 README.md 파일을 참조하세요.")
    print()
    print("⚠️ 개별 리포트 시스템은 더 이상 지원되지 않습니다.")
    
    return False

if __name__ == "__main__":
    main()
    sys.exit(1)  # 비정상 종료로 스크립트 실행 방지
