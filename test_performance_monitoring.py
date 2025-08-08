#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitoring Integration Test

v2 시스템 성능 모니터링 및 최적화 시스템 통합 테스트
- 성능 모니터링 기능 테스트
- v1/v2 성능 비교 테스트
- 최적화 권장사항 생성 테스트
- 응답 시간 측정 테스트

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import unittest
import sys
import os
import time
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 테스트 환경 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'Monitoring', 'Posco_News_mini_v2'))

try:
    from core.performance_monitor import (
        PerformanceMonitor, PerformanceComparator, 
        SystemPerformanceSnapshot, ProcessPerformanceData,
        PerformanceMetric, MetricType, PerformanceLevel
    )
    from core.performance_optimizer import (
        PerformanceOptimizer, OptimizationRecommendation,
        PerformanceIssue, OptimizationCategory, OptimizationPriority
    )
except ImportError as e:
    print(f"❌ 성능 모니터링 모듈 import 실패: {e}")
    sys.exit(1)

class TestPerformanceMonitoring(unittest.TestCase):
    """성능 모니터링 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.performance_monitor = PerformanceMonitor(self.test_dir, monitoring_interval=1)
        self.performance_optimizer = PerformanceOptimizer(self.test_dir)
        self.performance_comparator = PerformanceComparator(self.test_dir)
    
    def tearDown(self):
        """테스트 정리"""
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.stop_monitoring()
        
        # 임시 디렉토리 정리
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_performance_monitor_initialization(self):
        """성능 모니터 초기화 테스트"""
        print("\n🔧 성능 모니터 초기화 테스트...")
        
        # 초기화 상태 확인
        self.assertIsNotNone(self.performance_monitor)
        self.assertEqual(self.performance_monitor.script_dir, self.test_dir)
        self.assertFalse(self.performance_monitor.is_monitoring)
        self.assertEqual(len(self.performance_monitor.metrics_history), 0)
        
        print("✅ 성능 모니터 초기화 성공")
    
    def test_system_snapshot_collection(self):
        """시스템 스냅샷 수집 테스트"""
        print("\n📊 시스템 스냅샷 수집 테스트...")
        
        # 스냅샷 수집
        snapshot = self.performance_monitor._collect_system_snapshot()
        
        # 스냅샷 데이터 검증
        self.assertIsInstance(snapshot, SystemPerformanceSnapshot)
        self.assertIsInstance(snapshot.timestamp, datetime)
        self.assertGreaterEqual(snapshot.cpu_percent, 0)
        self.assertGreaterEqual(snapshot.memory_percent, 0)
        self.assertGreaterEqual(snapshot.memory_available_mb, 0)
        self.assertGreaterEqual(snapshot.process_count, 0)
        self.assertIsInstance(snapshot.active_processes, list)
        
        print(f"✅ 스냅샷 수집 성공: CPU {snapshot.cpu_percent:.1f}%, 메모리 {snapshot.memory_percent:.1f}%")
    
    def test_performance_monitoring_start_stop(self):
        """성능 모니터링 시작/중지 테스트"""
        print("\n🚀 성능 모니터링 시작/중지 테스트...")
        
        # 모니터링 시작
        self.performance_monitor.start_monitoring()
        self.assertTrue(self.performance_monitor.is_monitoring)
        self.assertIsNotNone(self.performance_monitor.monitoring_thread)
        
        # 잠시 대기하여 데이터 수집
        time.sleep(3)
        
        # 데이터 수집 확인
        self.assertGreater(len(self.performance_monitor.metrics_history), 0)
        self.assertGreater(self.performance_monitor.total_measurements, 0)
        
        # 모니터링 중지
        self.performance_monitor.stop_monitoring()
        self.assertFalse(self.performance_monitor.is_monitoring)
        
        print("✅ 성능 모니터링 시작/중지 성공")
    
    def test_response_time_measurement(self):
        """응답 시간 측정 테스트"""
        print("\n⏱️ 응답 시간 측정 테스트...")
        
        # 응답 시간 측정 (컨텍스트 매니저 사용)
        with self.performance_monitor.measure_operation_time("test_operation"):
            time.sleep(0.1)  # 0.1초 대기
        
        # 응답 시간 기록 확인
        self.assertIn("test_operation", self.performance_monitor.response_times)
        response_times = list(self.performance_monitor.response_times["test_operation"])
        self.assertEqual(len(response_times), 1)
        self.assertGreaterEqual(response_times[0], 0.1)
        self.assertLess(response_times[0], 0.2)  # 0.2초 미만이어야 함
        
        # 직접 응답 시간 기록
        self.performance_monitor.record_response_time("manual_operation", 2.5)
        self.assertIn("manual_operation", self.performance_monitor.response_times)
        manual_times = list(self.performance_monitor.response_times["manual_operation"])
        self.assertEqual(len(manual_times), 1)
        self.assertEqual(manual_times[0], 2.5)
        
        print("✅ 응답 시간 측정 성공")
    
    def test_performance_summary(self):
        """성능 요약 조회 테스트"""
        print("\n📋 성능 요약 조회 테스트...")
        
        # 모니터링 시작하여 데이터 수집
        self.performance_monitor.start_monitoring()
        time.sleep(2)
        
        # 응답 시간 데이터 추가
        self.performance_monitor.record_response_time("test_op", 1.5)
        self.performance_monitor.record_response_time("test_op", 2.0)
        
        # 성능 요약 조회
        summary = self.performance_monitor.get_performance_summary()
        
        # 요약 데이터 검증
        self.assertNotIn('error', summary)
        self.assertIn('timestamp', summary)
        self.assertIn('uptime_seconds', summary)
        self.assertIn('monitoring_status', summary)
        self.assertIn('current', summary)
        self.assertIn('averages', summary)
        self.assertIn('response_times', summary)
        self.assertIn('performance_level', summary)
        
        # 현재 상태 데이터 검증
        current = summary['current']
        self.assertIn('cpu_percent', current)
        self.assertIn('memory_percent', current)
        self.assertIn('process_count', current)
        
        # 응답 시간 통계 검증
        response_times = summary['response_times']
        self.assertIn('test_op', response_times)
        test_op_stats = response_times['test_op']
        self.assertIn('avg', test_op_stats)
        self.assertIn('min', test_op_stats)
        self.assertIn('max', test_op_stats)
        self.assertEqual(test_op_stats['count'], 2)
        
        self.performance_monitor.stop_monitoring()
        
        print("✅ 성능 요약 조회 성공")
    
    def test_performance_comparison(self):
        """성능 비교 테스트"""
        print("\n🔍 성능 비교 테스트...")
        
        # v1 기준선 데이터 생성
        v1_baseline = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'process_count': 10,
            'response_time_avg': 3.0
        }
        
        # v2 성능 데이터 시뮬레이션
        self.performance_monitor.start_monitoring()
        time.sleep(2)
        self.performance_monitor.record_response_time("test_operation", 2.0)
        
        # 성능 비교 수행
        comparison = self.performance_monitor.compare_with_baseline(v1_baseline)
        
        # 비교 결과 검증
        self.assertIsNotNone(comparison)
        self.assertIsInstance(comparison.comparison_time, datetime)
        self.assertIsInstance(comparison.v1_metrics, dict)
        self.assertIsInstance(comparison.v2_metrics, dict)
        self.assertIsInstance(comparison.improvement_percentage, dict)
        self.assertIsInstance(comparison.recommendations, list)
        
        # 개선율 계산 검증
        self.assertIn('cpu_percent', comparison.improvement_percentage)
        self.assertIn('memory_percent', comparison.improvement_percentage)
        
        self.performance_monitor.stop_monitoring()
        
        print("✅ 성능 비교 테스트 성공")
    
    def test_performance_optimizer_initialization(self):
        """성능 최적화기 초기화 테스트"""
        print("\n🔧 성능 최적화기 초기화 테스트...")
        
        # 초기화 상태 확인
        self.assertIsNotNone(self.performance_optimizer)
        self.assertEqual(self.performance_optimizer.script_dir, self.test_dir)
        self.assertEqual(len(self.performance_optimizer.recommendations), 0)
        self.assertEqual(len(self.performance_optimizer.applied_optimizations), 0)
        
        # 임계값 설정 확인
        self.assertIn('cpu_high', self.performance_optimizer.thresholds)
        self.assertIn('memory_critical', self.performance_optimizer.thresholds)
        
        print("✅ 성능 최적화기 초기화 성공")
    
    def test_performance_issue_analysis(self):
        """성능 이슈 분석 테스트"""
        print("\n🔍 성능 이슈 분석 테스트...")
        
        # 고부하 상황 시뮬레이션 데이터
        high_load_data = {
            'current': {
                'cpu_percent': 85.0,  # 임계 수준
                'memory_percent': 80.0,  # 높은 수준
                'disk_usage_percent': 70.0,
                'process_count': 20
            },
            'response_times': {
                'slow_operation': {'avg': 8.0, 'min': 5.0, 'max': 12.0}
            }
        }
        
        # 성능 이슈 분석
        issues = self.performance_optimizer.analyze_system_performance(high_load_data)
        
        # 이슈 검증
        self.assertGreater(len(issues), 0)
        
        # CPU 이슈 확인
        cpu_issues = [issue for issue in issues if issue.issue_type.startswith('cpu')]
        self.assertGreater(len(cpu_issues), 0)
        
        # 메모리 이슈 확인
        memory_issues = [issue for issue in issues if issue.issue_type.startswith('memory')]
        self.assertGreater(len(memory_issues), 0)
        
        # 응답시간 이슈 확인
        response_issues = [issue for issue in issues if issue.issue_type.startswith('response_time')]
        self.assertGreater(len(response_issues), 0)
        
        print(f"✅ 성능 이슈 분석 성공: {len(issues)}개 이슈 발견")
    
    def test_optimization_recommendations(self):
        """최적화 권장사항 생성 테스트"""
        print("\n💡 최적화 권장사항 생성 테스트...")
        
        # 테스트용 성능 이슈 생성
        test_issues = [
            PerformanceIssue(
                issue_type="cpu_critical",
                severity="critical",
                description="CPU 사용률이 임계 수준입니다",
                affected_components=["system"],
                metrics={"cpu_percent": 90.0},
                detected_at=datetime.now(),
                recommendations=["cpu_optimization"]
            ),
            PerformanceIssue(
                issue_type="memory_high",
                severity="warning",
                description="메모리 사용률이 높습니다",
                affected_components=["system"],
                metrics={"memory_percent": 80.0},
                detected_at=datetime.now(),
                recommendations=["memory_cleanup"]
            )
        ]
        
        # 권장사항 생성
        recommendations = self.performance_optimizer.generate_optimization_recommendations(test_issues)
        
        # 권장사항 검증
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIsInstance(rec, OptimizationRecommendation)
            self.assertIsInstance(rec.category, OptimizationCategory)
            self.assertIsInstance(rec.priority, OptimizationPriority)
            self.assertIsInstance(rec.implementation_steps, list)
            self.assertGreater(len(rec.implementation_steps), 0)
        
        print(f"✅ 최적화 권장사항 생성 성공: {len(recommendations)}개 권장사항")
    
    def test_optimization_summary(self):
        """최적화 요약 조회 테스트"""
        print("\n📊 최적화 요약 조회 테스트...")
        
        # 테스트용 권장사항 추가
        test_recommendation = OptimizationRecommendation(
            id="test_rec_001",
            category=OptimizationCategory.CPU,
            priority=OptimizationPriority.HIGH,
            title="테스트 CPU 최적화",
            description="테스트용 CPU 최적화 권장사항",
            impact_description="성능 향상 예상",
            implementation_steps=["1단계", "2단계"],
            estimated_improvement="20% 개선",
            risk_level="낮음",
            created_at=datetime.now()
        )
        
        self.performance_optimizer.recommendations.append(test_recommendation)
        
        # 최적화 요약 조회
        summary = self.performance_optimizer.get_optimization_summary()
        
        # 요약 데이터 검증
        self.assertNotIn('error', summary)
        self.assertIn('timestamp', summary)
        self.assertIn('total_recommendations', summary)
        self.assertIn('applied_optimizations', summary)
        self.assertIn('pending_optimizations', summary)
        self.assertIn('category_breakdown', summary)
        self.assertIn('priority_breakdown', summary)
        self.assertIn('recent_recommendations', summary)
        
        # 데이터 값 검증
        self.assertEqual(summary['total_recommendations'], 1)
        self.assertEqual(summary['applied_optimizations'], 0)
        self.assertEqual(summary['pending_optimizations'], 1)
        
        print("✅ 최적화 요약 조회 성공")
    
    def test_performance_data_export(self):
        """성능 데이터 내보내기 테스트"""
        print("\n💾 성능 데이터 내보내기 테스트...")
        
        # 모니터링 시작하여 데이터 수집
        self.performance_monitor.start_monitoring()
        time.sleep(2)
        self.performance_monitor.record_response_time("export_test", 1.0)
        
        # 데이터 내보내기
        export_file = self.performance_monitor.export_performance_data()
        
        # 파일 생성 확인
        self.assertTrue(os.path.exists(export_file))
        self.assertTrue(export_file.endswith('.json'))
        
        # 내보낸 데이터 검증
        with open(export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn('export_timestamp', export_data)
        self.assertIn('monitoring_period', export_data)
        self.assertIn('summary', export_data)
        self.assertIn('metrics_history', export_data)
        self.assertIn('alert_count', export_data)
        
        self.performance_monitor.stop_monitoring()
        
        print(f"✅ 성능 데이터 내보내기 성공: {export_file}")
    
    def test_v1_baseline_collection(self):
        """v1 기준선 수집 테스트"""
        print("\n📊 v1 기준선 수집 테스트...")
        
        # psutil 모킹으로 v1 프로세스 시뮬레이션
        with patch('psutil.process_iter') as mock_process_iter:
            # 모킹된 프로세스 데이터
            mock_processes = [
                Mock(info={
                    'pid': 1234,
                    'name': 'python3',
                    'cmdline': ['python3', 'monitor_watchhamster.py'],
                    'cpu_percent': 15.0,
                    'memory_percent': 25.0
                }),
                Mock(info={
                    'pid': 1235,
                    'name': 'python3',
                    'cmdline': ['python3', 'posco_main_notifier.py'],
                    'cpu_percent': 10.0,
                    'memory_percent': 20.0
                })
            ]
            
            mock_process_iter.return_value = mock_processes
            
            # CPU와 메모리 사용률 모킹
            with patch('psutil.cpu_percent', return_value=45.0), \
                 patch('psutil.virtual_memory') as mock_memory:
                
                mock_memory.return_value.percent = 55.0
                
                # v1 기준선 수집
                baseline = self.performance_comparator.collect_v1_baseline()
                
                # 기준선 데이터 검증
                self.assertIn('timestamp', baseline)
                self.assertIn('system_type', baseline)
                self.assertEqual(baseline['system_type'], 'v1')
                self.assertIn('cpu_percent', baseline)
                self.assertIn('memory_percent', baseline)
                self.assertIn('process_count', baseline)
                self.assertIn('processes', baseline)
                
                # 프로세스 데이터 검증
                self.assertEqual(baseline['process_count'], 2)
                self.assertEqual(len(baseline['processes']), 2)
        
        print("✅ v1 기준선 수집 성공")
    
    def test_comparison_report_generation(self):
        """비교 보고서 생성 테스트"""
        print("\n📋 비교 보고서 생성 테스트...")
        
        # 테스트 데이터
        v1_data = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'process_count': 10,
            'response_time_avg': 3.0
        }
        
        v2_data = {
            'cpu_percent': 40.0,
            'memory_percent': 50.0,
            'process_count': 8,
            'response_time_avg': 2.0
        }
        
        # 비교 보고서 생성
        report = self.performance_comparator.generate_comparison_report(v1_data, v2_data)
        
        # 보고서 내용 검증
        self.assertIsInstance(report, str)
        self.assertIn("성능 비교 보고서", report)
        self.assertIn("CPU 사용률", report)
        self.assertIn("메모리 사용률", report)
        self.assertIn("권장사항", report)
        self.assertIn("v1", report)
        self.assertIn("v2", report)
        
        # 보고서 저장 테스트
        report_file = self.performance_comparator.save_comparison_report(report)
        self.assertTrue(os.path.exists(report_file))
        
        print("✅ 비교 보고서 생성 성공")
    
    def test_optimization_report_generation(self):
        """최적화 보고서 생성 테스트"""
        print("\n📋 최적화 보고서 생성 테스트...")
        
        # 테스트용 권장사항 추가
        test_recommendations = [
            OptimizationRecommendation(
                id="test_001",
                category=OptimizationCategory.CPU,
                priority=OptimizationPriority.CRITICAL,
                title="긴급 CPU 최적화",
                description="CPU 사용률 긴급 최적화",
                impact_description="시스템 안정성 향상",
                implementation_steps=["1단계", "2단계"],
                estimated_improvement="30% 개선",
                risk_level="낮음",
                created_at=datetime.now()
            ),
            OptimizationRecommendation(
                id="test_002",
                category=OptimizationCategory.MEMORY,
                priority=OptimizationPriority.HIGH,
                title="메모리 정리",
                description="메모리 사용량 최적화",
                impact_description="메모리 효율성 향상",
                implementation_steps=["정리", "최적화"],
                estimated_improvement="20% 개선",
                risk_level="낮음",
                created_at=datetime.now(),
                applied=True,
                applied_at=datetime.now()
            )
        ]
        
        self.performance_optimizer.recommendations.extend(test_recommendations)
        
        # 최적화 보고서 생성
        report = self.performance_optimizer.generate_optimization_report()
        
        # 보고서 내용 검증
        self.assertIsInstance(report, str)
        self.assertIn("최적화 보고서", report)
        self.assertIn("최적화 요약", report)
        self.assertIn("카테고리별 분석", report)
        self.assertIn("우선순위별 분석", report)
        self.assertIn("최근 권장사항", report)
        self.assertIn("다음 단계 권장사항", report)
        
        print("✅ 최적화 보고서 생성 성공")


def run_performance_integration_test():
    """성능 모니터링 통합 테스트 실행"""
    print("🚀 POSCO 워치햄스터 v2 성능 모니터링 통합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceMonitoring)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"총 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  • {test}: {error_msg}")
    
    if result.errors:
        print("\n💥 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  • {test}: {error_msg}")
    
    # 전체 결과
    if result.wasSuccessful():
        print("\n🎉 모든 성능 모니터링 테스트가 성공했습니다!")
        return True
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
        return False


if __name__ == '__main__':
    success = run_performance_integration_test()
    sys.exit(0 if success else 1)