#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캐시 모니터 테스트 스크립트
내장형 캐시 데이터 모니터링 시스템 검증

테스트 항목:
- 캐시 상태 분석
- 알림 시스템
- GUI 통합
- 자동 갱신
"""

import os
import sys
import json
import time
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from cache_monitor import CacheMonitor, CacheStatus, DataType, CacheAlert


class CacheMonitorTester:
    """캐시 모니터 테스터"""
    
    def __init__(self):
        """테스터 초기화"""
        self.temp_dir = None
        self.monitor = None
        self.test_results = []
    
    def setup_test_environment(self):
        """테스트 환경 설정"""
        print("🔧 테스트 환경 설정 중...")
        
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp(prefix="cache_monitor_test_")
        print(f"  임시 디렉토리: {self.temp_dir}")
        
        # 캐시 모니터 생성
        self.monitor = CacheMonitor(data_dir=self.temp_dir)
        
        print("✅ 테스트 환경 설정 완료")
    
    def cleanup_test_environment(self):
        """테스트 환경 정리"""
        print("🧹 테스트 환경 정리 중...")
        
        if self.monitor:
            self.monitor.stop_monitoring()
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        print("✅ 테스트 환경 정리 완료")
    
    def create_test_cache_file(self, status_type: str = "fresh"):
        """테스트용 캐시 파일 생성"""
        cache_file = os.path.join(self.temp_dir, "market_data_cache.json")
        
        if status_type == "missing":
            # 파일을 생성하지 않음
            return
        
        # 시간 설정
        if status_type == "fresh":
            timestamp = datetime.now()
        elif status_type == "stale":
            timestamp = datetime.now() - timedelta(minutes=10)
        elif status_type == "expired":
            timestamp = datetime.now() - timedelta(hours=2)
        else:
            timestamp = datetime.now()
        
        # 품질 설정
        if status_type == "corrupted":
            quality_score = 0.3
            confidence = 0.4
        else:
            quality_score = 0.85
            confidence = 0.90
        
        # 테스트 데이터 생성
        test_data = {
            "market_data": {
                "kospi": {
                    "value": 2520.5,
                    "timestamp": timestamp.isoformat(),
                    "source": "kospi_api",
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "metadata": {
                        "change": 15.3,
                        "change_percent": 0.61,
                        "volume": 450000000
                    }
                },
                "exchange_rate": {
                    "value": 1347.5,
                    "timestamp": timestamp.isoformat(),
                    "source": "exchange_api",
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "metadata": {
                        "change": -2.5,
                        "change_percent": -0.18,
                        "base_currency": "USD",
                        "target_currency": "KRW"
                    }
                },
                "posco_stock": {
                    "value": 285000,
                    "timestamp": timestamp.isoformat(),
                    "source": "posco_stock_api",
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "metadata": {
                        "change": 3500,
                        "change_percent": 1.24,
                        "volume": 125000,
                        "market_cap": 24500000000000
                    }
                },
                "news_sentiment": {
                    "value": 0.65,
                    "timestamp": timestamp.isoformat(),
                    "source": "news_api",
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "metadata": {
                        "sentiment_label": "positive",
                        "news_count": 15,
                        "key_topics": ["실적", "투자", "성장"]
                    }
                },
                "last_updated": timestamp.isoformat(),
                "overall_quality": quality_score
            },
            "cached_at": timestamp.isoformat(),
            "cache_version": "1.0"
        }
        
        if status_type == "empty":
            # 빈 파일 생성
            with open(cache_file, 'w') as f:
                pass
        elif status_type == "invalid_json":
            # 잘못된 JSON 파일 생성
            with open(cache_file, 'w') as f:
                f.write("{ invalid json content")
        else:
            # 정상 JSON 파일 생성
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    def test_cache_status_detection(self):
        """캐시 상태 감지 테스트"""
        print("\n🧪 캐시 상태 감지 테스트")
        
        test_cases = [
            ("fresh", CacheStatus.FRESH),
            ("stale", CacheStatus.STALE),
            ("expired", CacheStatus.EXPIRED),
            ("missing", CacheStatus.MISSING),
            ("corrupted", CacheStatus.CORRUPTED),
            ("empty", CacheStatus.CORRUPTED),
            ("invalid_json", CacheStatus.CORRUPTED)
        ]
        
        for test_type, expected_status in test_cases:
            print(f"  테스트: {test_type} -> {expected_status.value}")
            
            # 테스트 파일 생성
            self.create_test_cache_file(test_type)
            
            # 상태 확인
            status = self.monitor.check_cache_status()
            
            # 결과 검증
            success = True
            for data_type in DataType:
                actual_status = status[data_type].status
                if actual_status != expected_status:
                    print(f"    ❌ {data_type.value}: 예상 {expected_status.value}, 실제 {actual_status.value}")
                    success = False
                else:
                    print(f"    ✅ {data_type.value}: {actual_status.value}")
            
            self.test_results.append({
                'test': f'status_detection_{test_type}',
                'success': success,
                'expected': expected_status.value,
                'details': f'{test_type} 상태 감지'
            })
            
            # 다음 테스트를 위해 파일 삭제
            cache_file = os.path.join(self.temp_dir, "market_data_cache.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
    
    def test_alert_system(self):
        """알림 시스템 테스트"""
        print("\n🔔 알림 시스템 테스트")
        
        # 알림 수집기 설정
        received_alerts = []
        
        def alert_collector(alert: CacheAlert):
            received_alerts.append(alert)
        
        self.monitor.add_alert_callback(alert_collector)
        
        # 다양한 상태로 테스트
        test_scenarios = [
            ("missing", "data_shortage"),
            ("expired", "data_shortage"),
            ("corrupted", "quality_degradation"),
            ("stale", "stale_data")
        ]
        
        for scenario, expected_alert_type in test_scenarios:
            print(f"  시나리오: {scenario}")
            received_alerts.clear()
            
            # 테스트 파일 생성
            self.create_test_cache_file(scenario)
            
            # 상태 확인 (알림 트리거)
            self.monitor.check_cache_status()
            
            # 알림 확인
            relevant_alerts = [a for a in received_alerts if a.alert_type == expected_alert_type]
            
            if relevant_alerts:
                print(f"    ✅ 예상 알림 수신: {expected_alert_type}")
                for alert in relevant_alerts:
                    print(f"      - {alert.data_type.value}: {alert.message}")
                success = True
            else:
                print(f"    ❌ 예상 알림 미수신: {expected_alert_type}")
                success = False
            
            self.test_results.append({
                'test': f'alert_system_{scenario}',
                'success': success,
                'expected': expected_alert_type,
                'details': f'{scenario} 시나리오 알림'
            })
            
            # 파일 정리
            cache_file = os.path.join(self.temp_dir, "market_data_cache.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
    
    def test_monitoring_loop(self):
        """모니터링 루프 테스트"""
        print("\n🔄 모니터링 루프 테스트")
        
        # 알림 수집기 설정
        received_alerts = []
        
        def alert_collector(alert: CacheAlert):
            received_alerts.append(alert)
        
        self.monitor.add_alert_callback(alert_collector)
        
        # 모니터링 설정 조정 (빠른 테스트를 위해)
        self.monitor.update_config({'check_interval_seconds': 1})
        
        # 초기 상태 (missing)
        print("  초기 상태: 파일 없음")
        
        # 모니터링 시작
        self.monitor.start_monitoring()
        
        # 잠시 대기 (알림 발생 확인)
        time.sleep(2)
        
        # 파일 생성 (상태 변화)
        print("  상태 변화: 신선한 데이터 생성")
        self.create_test_cache_file("fresh")
        
        # 상태 변화 감지 대기
        time.sleep(2)
        
        # 모니터링 중지
        self.monitor.stop_monitoring()
        
        # 결과 확인
        status_change_alerts = [a for a in received_alerts if a.alert_type == "status_change"]
        
        if status_change_alerts:
            print("  ✅ 상태 변화 알림 수신")
            for alert in status_change_alerts:
                print(f"    - {alert.message}")
            success = True
        else:
            print("  ❌ 상태 변화 알림 미수신")
            success = False
        
        self.test_results.append({
            'test': 'monitoring_loop',
            'success': success,
            'expected': 'status_change alerts',
            'details': '모니터링 루프 및 상태 변화 감지'
        })
    
    def test_cache_summary(self):
        """캐시 요약 테스트"""
        print("\n📊 캐시 요약 테스트")
        
        # 신선한 데이터로 테스트
        self.create_test_cache_file("fresh")
        
        # 요약 정보 생성
        summary = self.monitor.get_cache_summary()
        
        # 결과 검증
        expected_fields = ['last_check', 'total_data_types', 'status_counts', 'overall_health', 'warnings', 'recommendations']
        success = True
        
        for field in expected_fields:
            if field not in summary:
                print(f"  ❌ 필수 필드 누락: {field}")
                success = False
            else:
                print(f"  ✅ 필드 존재: {field}")
        
        # 건강도 확인
        if summary.get('overall_health') == 'excellent':
            print("  ✅ 전체 건강도: excellent")
        else:
            print(f"  ⚠️ 전체 건강도: {summary.get('overall_health')}")
        
        # 상태 카운트 확인
        fresh_count = summary.get('status_counts', {}).get('fresh', 0)
        if fresh_count == len(DataType):
            print(f"  ✅ 신선한 데이터 카운트: {fresh_count}/{len(DataType)}")
        else:
            print(f"  ⚠️ 신선한 데이터 카운트: {fresh_count}/{len(DataType)}")
        
        self.test_results.append({
            'test': 'cache_summary',
            'success': success,
            'expected': 'complete summary',
            'details': '캐시 요약 정보 생성'
        })
    
    def test_report_export(self):
        """보고서 내보내기 테스트"""
        print("\n📄 보고서 내보내기 테스트")
        
        # 테스트 데이터 생성
        self.create_test_cache_file("fresh")
        self.monitor.check_cache_status()
        
        # 보고서 생성
        report_path = self.monitor.export_status_report()
        
        # 파일 존재 확인
        if os.path.exists(report_path):
            print(f"  ✅ 보고서 파일 생성: {os.path.basename(report_path)}")
            
            # JSON 유효성 확인
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                required_sections = ['generated_at', 'summary', 'detailed_status', 'recent_alerts', 'monitoring_config']
                missing_sections = [s for s in required_sections if s not in report_data]
                
                if not missing_sections:
                    print("  ✅ 보고서 구조 완전")
                    success = True
                else:
                    print(f"  ❌ 누락된 섹션: {missing_sections}")
                    success = False
                
            except json.JSONDecodeError:
                print("  ❌ 보고서 JSON 형식 오류")
                success = False
        else:
            print("  ❌ 보고서 파일 생성 실패")
            success = False
        
        self.test_results.append({
            'test': 'report_export',
            'success': success,
            'expected': 'valid report file',
            'details': '상태 보고서 내보내기'
        })
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 캐시 모니터 테스트 시작")
        print("=" * 50)
        
        try:
            self.setup_test_environment()
            
            # 개별 테스트 실행
            self.test_cache_status_detection()
            self.test_alert_system()
            self.test_monitoring_loop()
            self.test_cache_summary()
            self.test_report_export()
            
        finally:
            self.cleanup_test_environment()
        
        # 결과 요약
        self.print_test_summary()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📋 테스트 결과 요약")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ 성공한 테스트:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}: {result['details']}")
        
        if failed_tests == 0:
            print("\n🎉 모든 테스트 통과!")
        else:
            print(f"\n⚠️ {failed_tests}개 테스트 실패")


def main():
    """메인 함수"""
    tester = CacheMonitorTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()