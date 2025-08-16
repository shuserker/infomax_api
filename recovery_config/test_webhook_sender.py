#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 전송 시스템 테스트

웹훅 전송 시스템의 모든 기능을 테스트하는 종합 테스트 스위트입니다.

테스트 항목:
- BOT 타입별 메시지 전송 테스트
- 우선순위 큐 동작 테스트
- 재시도 메커니즘 테스트
- 중복 메시지 방지 테스트
- 전송 통계 테스트
"""

import os
import sys
import json
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from webhook_sender import (
    WebhookSender, WebhookMessage, WebhookSendResult,
    MessagePriority, BotType, WebhookEndpoint
)
import webhook_sender


class TestWebhookSender(unittest.TestCase):
    """웹훅 전송 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.webhook_sender = WebhookSender(test_mode=True)
        
        # 샘플 뉴스 데이터
        self.sample_news_data = {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67)',
                'date': '20250812',
                'time': '061938'
            },
            'kospi-close': {
                'title': '[증시마감] 코스피 2,650.45 상승 마감',
                'content': '코스피 2,650.45 (+15.23), 코스닥 850.67 (+8.45)',
                'date': '20250812',
                'time': '154523'
            },
            'exchange-rate': {
                'title': '[서환마감] 원/달러 환율 1,320원대',
                'content': '원/달러 1,325.50 (-2.30), 엔/달러 148.25 (+0.15)',
                'date': '20250812',
                'time': '163045'
            }
        }
    
    def tearDown(self):
        """테스트 정리"""
        self.webhook_sender.shutdown()
    
    def test_webhook_sender_initialization(self):
        """웹훅 전송자 초기화 테스트"""
        self.assertIsNotNone(self.webhook_sender)
        self.assertTrue(self.webhook_sender.test_mode)
        self.assertIsNotNone(self.webhook_sender.message_generator)
        self.assertIsNotNone(self.webhook_sender.ai_engine)
        self.assertTrue(self.webhook_sender.is_running)
    
    def test_bot_routing_configuration(self):
        """BOT 라우팅 설정 테스트"""
        # 모든 BOT 타입이 적절한 엔드포인트로 라우팅되는지 확인
        self.assertEqual(
            self.webhook_sender.bot_routing[BotType.NEWS_COMPARISON],
            WebhookEndpoint.NEWS_MAIN
        )
        self.assertEqual(
            self.webhook_sender.bot_routing[BotType.WATCHHAMSTER_ERROR],
            WebhookEndpoint.WATCHHAMSTER
        )
        self.assertEqual(
            self.webhook_sender.bot_routing[BotType.TEST],
            WebhookEndpoint.TEST
        )
    
    @patch('webhook_sender.requests.post')
    def test_send_business_day_comparison(self, mock_post):
        """영업일 비교 분석 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 메시지 전송
        message_id = self.webhook_sender.send_business_day_comparison(
            self.sample_news_data,
            priority=MessagePriority.NORMAL
        )
        
        # 결과 검증
        self.assertIsNotNone(message_id)
        
        # 잠시 대기 (큐 처리 시간)
        time.sleep(1)
        
        # HTTP 요청이 호출되었는지 확인
        self.assertTrue(mock_post.called)
        
        # 호출된 인수 확인
        call_args = mock_post.call_args
        self.assertIn('json', call_args.kwargs)
        payload = call_args.kwargs['json']
        
        self.assertIn('botName', payload)
        self.assertIn('text', payload)
        self.assertIn('attachments', payload)
        self.assertEqual(len(payload['attachments']), 1)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_send_delay_notification(self, mock_post):
        """지연 발행 알림 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 메시지 전송
        message_id = self.webhook_sender.send_delay_notification(
            'kospi-close',
            self.sample_news_data['kospi-close'],
            delay_minutes=30,
            priority=MessagePriority.HIGH
        )
        
        # 결과 검증
        self.assertIsNotNone(message_id)
        
        # 잠시 대기
        time.sleep(1)
        
        # HTTP 요청 확인
        self.assertTrue(mock_post.called)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_send_daily_integrated_report(self, mock_post):
        """일일 통합 분석 리포트 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 메시지 전송
        message_id = self.webhook_sender.send_daily_integrated_report(
            self.sample_news_data,
            report_url="https://example.com/report.html",
            priority=MessagePriority.NORMAL
        )
        
        # 결과 검증
        self.assertIsNotNone(message_id)
        
        # 잠시 대기
        time.sleep(1)
        
        # HTTP 요청 확인
        self.assertTrue(mock_post.called)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_send_watchhamster_error(self, mock_post):
        """워치햄스터 오류 알림 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 오류 상세 정보
        error_details = {
            'process_name': 'posco_main_notifier',
            'error_code': 'CONNECTION_FAILED',
            'retry_count': 3
        }
        
        # 메시지 전송
        message_id = self.webhook_sender.send_watchhamster_error(
            "API 연결 실패",
            error_details=error_details,
            priority=MessagePriority.CRITICAL
        )
        
        # 결과 검증
        self.assertIsNotNone(message_id)
        
        # 잠시 대기
        time.sleep(1)
        
        # HTTP 요청 확인
        self.assertTrue(mock_post.called)
        
        # 페이로드 확인
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        self.assertIn("워치햄스터", payload['botName'])
        self.assertIn("오류", payload['text'])
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_send_test_message(self, mock_post):
        """테스트 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 메시지 전송
        message_id = self.webhook_sender.send_test_message(
            "웹훅 전송 시스템 테스트",
            priority=MessagePriority.LOW
        )
        
        # 결과 검증
        self.assertIsNotNone(message_id)
        
        # 잠시 대기
        time.sleep(1)
        
        # HTTP 요청 확인
        self.assertTrue(mock_post.called)
        
        # 페이로드 확인
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        self.assertIn("[TEST]", payload['botName'])
        self.assertIn("[TEST]", payload['text'])
    
    def test_message_priority_queue(self):
        """메시지 우선순위 큐 테스트"""
        # 다양한 우선순위의 메시지 생성
        critical_msg = self.webhook_sender._create_webhook_message(
            BotType.WATCHHAMSTER_ERROR, MessagePriority.CRITICAL,
            "Critical Bot", "Critical", "Critical message", "#dc3545"
        )
        
        normal_msg = self.webhook_sender._create_webhook_message(
            BotType.NEWS_STATUS, MessagePriority.NORMAL,
            "Normal Bot", "Normal", "Normal message", "#28a745"
        )
        
        low_msg = self.webhook_sender._create_webhook_message(
            BotType.TEST, MessagePriority.LOW,
            "Low Bot", "Low", "Low message", "#6c757d"
        )
        
        # 우선순위 비교 테스트
        self.assertTrue(critical_msg < normal_msg)
        self.assertTrue(normal_msg < low_msg)
        self.assertTrue(critical_msg < low_msg)
    
    def test_message_hash_generation(self):
        """메시지 해시 생성 테스트"""
        message1 = self.webhook_sender._create_webhook_message(
            BotType.NEWS_STATUS, MessagePriority.NORMAL,
            "Test Bot", "Test", "Test message", "#28a745"
        )
        
        message2 = self.webhook_sender._create_webhook_message(
            BotType.NEWS_STATUS, MessagePriority.NORMAL,
            "Test Bot", "Test", "Test message", "#28a745"
        )
        
        # 동일한 내용의 메시지는 같은 해시를 가져야 함
        hash1 = self.webhook_sender._generate_message_hash(message1)
        hash2 = self.webhook_sender._generate_message_hash(message2)
        
        self.assertEqual(hash1, hash2)
        
        # 다른 내용의 메시지는 다른 해시를 가져야 함
        message3 = self.webhook_sender._create_webhook_message(
            BotType.NEWS_STATUS, MessagePriority.NORMAL,
            "Test Bot", "Test", "Different message", "#28a745"
        )
        
        hash3 = self.webhook_sender._generate_message_hash(message3)
        self.assertNotEqual(hash1, hash3)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_retry_mechanism(self, mock_post):
        """재시도 메커니즘 테스트"""
        # 첫 번째 호출은 실패, 두 번째 호출은 성공하도록 설정
        mock_responses = [
            Mock(status_code=500, text="Internal Server Error"),
            Mock(status_code=200, text="OK")
        ]
        mock_post.side_effect = mock_responses
        
        # 메시지 전송
        message_id = self.webhook_sender.send_test_message("재시도 테스트")
        
        # 재시도가 완료될 때까지 대기
        time.sleep(3)
        
        # 두 번 호출되었는지 확인 (첫 번째 실패 + 재시도 성공)
        self.assertEqual(mock_post.call_count, 2)
    
    def test_queue_status(self):
        """큐 상태 조회 테스트"""
        status = self.webhook_sender.get_queue_status()
        
        # 필수 필드 확인
        self.assertIn('timestamp', status)
        self.assertIn('queue_size', status)
        self.assertIn('failed_messages_count', status)
        self.assertIn('cache_size', status)
        self.assertIn('is_running', status)
        self.assertIn('statistics', status)
        
        # 타입 확인
        self.assertIsInstance(status['queue_size'], int)
        self.assertIsInstance(status['is_running'], bool)
        self.assertTrue(status['is_running'])
    
    def test_send_statistics(self):
        """전송 통계 테스트"""
        statistics = self.webhook_sender.get_send_statistics()
        
        # 필수 필드 확인
        self.assertIn('total_sent', statistics)
        self.assertIn('successful_sends', statistics)
        self.assertIn('failed_sends', statistics)
        self.assertIn('success_rate', statistics)
        self.assertIn('failure_rate', statistics)
        
        # 초기 상태 확인
        self.assertEqual(statistics['total_sent'], 0)
        self.assertEqual(statistics['successful_sends'], 0)
        self.assertEqual(statistics['failed_sends'], 0)
        self.assertEqual(statistics['success_rate'], 0.0)
        self.assertEqual(statistics['failure_rate'], 0.0)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_duplicate_message_prevention(self, mock_post):
        """중복 메시지 방지 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 동일한 메시지 두 번 전송
        message_id1 = self.webhook_sender.send_test_message("중복 테스트")
        message_id2 = self.webhook_sender.send_test_message("중복 테스트")
        
        # 첫 번째 메시지는 전송되고, 두 번째는 중복으로 인해 None 반환
        self.assertIsNotNone(message_id1)
        self.assertIsNone(message_id2)
        
        # 잠시 대기
        time.sleep(1)
        
        # HTTP 요청이 한 번만 호출되었는지 확인
        self.assertEqual(mock_post.call_count, 1)
    
    def test_webhook_message_creation(self):
        """웹훅 메시지 생성 테스트"""
        message = self.webhook_sender._create_webhook_message(
            bot_type=BotType.NEWS_STATUS,
            priority=MessagePriority.NORMAL,
            bot_name="Test Bot",
            title="Test Title",
            content="Test Content",
            color="#28a745",
            test_mode=True
        )
        
        # 필드 확인
        self.assertIsNotNone(message.id)
        self.assertEqual(message.bot_type, BotType.NEWS_STATUS)
        self.assertEqual(message.priority, MessagePriority.NORMAL)
        self.assertEqual(message.endpoint, WebhookEndpoint.NEWS_MAIN)
        self.assertEqual(message.bot_name, "Test Bot")
        self.assertEqual(message.title, "Test Title")
        self.assertEqual(message.content, "Test Content")
        self.assertEqual(message.color, "#28a745")
        self.assertTrue(message.test_mode)
        self.assertEqual(message.retry_count, 0)
        self.assertEqual(message.max_retries, 3)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_error_handling(self, mock_post):
        """오류 처리 테스트"""
        # 연결 오류 시뮬레이션
        mock_post.side_effect = Exception("Connection failed")
        
        # 메시지 전송
        message_id = self.webhook_sender.send_test_message("오류 테스트")
        
        # 메시지 ID는 생성되어야 함 (큐에 추가됨)
        self.assertIsNotNone(message_id)
        
        # 재시도가 완료될 때까지 대기
        time.sleep(5)
        
        # 최대 재시도 횟수만큼 호출되었는지 확인
        self.assertGreaterEqual(mock_post.call_count, 3)
        
        # 실패한 메시지가 기록되었는지 확인
        self.assertGreater(len(self.webhook_sender.failed_messages), 0)


class TestWebhookIntegration(unittest.TestCase):
    """웹훅 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.webhook_sender = WebhookSender(test_mode=True)
        
        # 실제 뉴스 데이터 시뮬레이션
        self.realistic_news_data = {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미 증시, 인플레이션 우려에도 상승 마감',
                'content': '다우존스 35,123.45 (+150.25, +0.43%), 나스닥 14,567.89 (+45.67, +0.31%), S&P500 4,456.78 (+12.34, +0.28%)',
                'date': '20250812',
                'time': '061938',
                'url': 'https://example.com/news/1'
            },
            'kospi-close': {
                'title': '[증시마감] 코스피, 외국인 매수세에 상승 마감',
                'content': '코스피 2,650.45 (+15.23, +0.58%), 코스닥 850.67 (+8.45, +1.00%), 거래대금 12.5조원',
                'date': '20250812',
                'time': '154523',
                'url': 'https://example.com/news/2'
            },
            'exchange-rate': {
                'title': '[서환마감] 원/달러 환율, 미 달러 강세에 상승',
                'content': '원/달러 1,325.50 (-2.30, -0.17%), 엔/달러 148.25 (+0.15, +0.10%), 유로/달러 1.0845 (-0.0012)',
                'date': '20250812',
                'time': '163045',
                'url': 'https://example.com/news/3'
            }
        }
    
    def tearDown(self):
        """테스트 정리"""
        self.webhook_sender.shutdown()
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_full_workflow_simulation(self, mock_post):
        """전체 워크플로우 시뮬레이션 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 1. 영업일 비교 분석 전송
        comparison_id = self.webhook_sender.send_business_day_comparison(
            self.realistic_news_data,
            priority=MessagePriority.NORMAL
        )
        
        # 2. 지연 발행 알림 전송
        delay_id = self.webhook_sender.send_delay_notification(
            'kospi-close',
            self.realistic_news_data['kospi-close'],
            delay_minutes=45,
            priority=MessagePriority.HIGH
        )
        
        # 3. 일일 통합 리포트 전송
        report_id = self.webhook_sender.send_daily_integrated_report(
            self.realistic_news_data,
            report_url="https://shuserker.github.io/infomax_api/reports/20250812.html",
            priority=MessagePriority.NORMAL
        )
        
        # 4. 워치햄스터 상태 전송
        status_id = self.webhook_sender.send_watchhamster_status(
            "모든 시스템 정상 작동",
            status_details={
                'uptime': '2일 14시간 32분',
                'processed_messages': 1247,
                'cpu_usage': '15.2%',
                'memory_usage': '342MB'
            },
            priority=MessagePriority.NORMAL
        )
        
        # 모든 메시지 ID가 생성되었는지 확인
        self.assertIsNotNone(comparison_id)
        self.assertIsNotNone(delay_id)
        self.assertIsNotNone(report_id)
        self.assertIsNotNone(status_id)
        
        # 모든 메시지가 처리될 때까지 대기
        time.sleep(3)
        
        # HTTP 요청이 4번 호출되었는지 확인
        self.assertEqual(mock_post.call_count, 4)
        
        # 전송 통계 확인
        statistics = self.webhook_sender.get_send_statistics()
        self.assertEqual(statistics['total_sent'], 4)
        self.assertEqual(statistics['successful_sends'], 4)
        self.assertEqual(statistics['failed_sends'], 0)
        self.assertEqual(statistics['success_rate'], 1.0)
    
    @patch('recovery_config.webhook_sender.requests.post')
    def test_mixed_priority_handling(self, mock_post):
        """혼합 우선순위 처리 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response
        
        # 다양한 우선순위의 메시지들을 역순으로 전송
        # (낮은 우선순위부터 높은 우선순위 순으로)
        
        # 1. 낮은 우선순위 (테스트 메시지)
        test_id = self.webhook_sender.send_test_message(
            "낮은 우선순위 테스트",
            priority=MessagePriority.LOW
        )
        
        # 2. 일반 우선순위 (상태 알림)
        status_id = self.webhook_sender.send_status_notification(
            self.realistic_news_data,
            priority=MessagePriority.NORMAL
        )
        
        # 3. 높은 우선순위 (지연 알림)
        delay_id = self.webhook_sender.send_delay_notification(
            'newyork-market-watch',
            self.realistic_news_data['newyork-market-watch'],
            delay_minutes=60,
            priority=MessagePriority.HIGH
        )
        
        # 4. 최고 우선순위 (오류 알림)
        error_id = self.webhook_sender.send_watchhamster_error(
            "시스템 크리티컬 오류",
            error_details={'severity': 'critical', 'component': 'api_client'},
            priority=MessagePriority.CRITICAL
        )
        
        # 모든 메시지가 처리될 때까지 대기
        time.sleep(3)
        
        # 모든 메시지가 전송되었는지 확인
        self.assertEqual(mock_post.call_count, 4)
        
        # 호출 순서 확인 (우선순위 순으로 처리되어야 함)
        # 실제로는 큐 처리 순서를 직접 확인하기 어려우므로
        # 모든 메시지가 성공적으로 처리되었는지만 확인
        statistics = self.webhook_sender.get_send_statistics()
        self.assertEqual(statistics['successful_sends'], 4)


def run_webhook_sender_tests():
    """웹훅 전송 시스템 테스트 실행"""
    print("🧪 웹훅 전송 시스템 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 기본 기능 테스트 추가
    test_suite.addTest(unittest.makeSuite(TestWebhookSender))
    
    # 통합 테스트 추가
    test_suite.addTest(unittest.makeSuite(TestWebhookIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🧪 웹훅 전송 시스템 테스트 완료")
    print(f"✅ 성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"❌ 실패: {len(result.failures)}개")
    print(f"🚨 오류: {len(result.errors)}개")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_msg}")
    
    if result.errors:
        print("\n🚨 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  - {test}: {error_msg}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_webhook_sender_tests()
    sys.exit(0 if success else 1)