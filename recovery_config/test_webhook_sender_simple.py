#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 전송 시스템 간단 테스트

웹훅 전송 시스템의 기본 기능을 테스트하는 간단한 테스트입니다.
"""

import os
import sys
import time
import logging

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from webhook_sender import (
    WebhookSender, MessagePriority, BotType, WebhookEndpoint
)


def test_webhook_sender_basic():
    """웹훅 전송자 기본 기능 테스트"""
    print("🧪 웹훅 전송 시스템 기본 테스트 시작")
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 웹훅 전송자 생성
    webhook_sender = WebhookSender(test_mode=True)
    
    try:
        # 1. 초기화 테스트
        print("✅ 웹훅 전송자 초기화 성공")
        assert webhook_sender.test_mode == True
        assert webhook_sender.is_running == True
        
        # 2. BOT 라우팅 설정 테스트
        print("✅ BOT 라우팅 설정 확인")
        assert webhook_sender.bot_routing[BotType.NEWS_COMPARISON] == WebhookEndpoint.NEWS_MAIN
        assert webhook_sender.bot_routing[BotType.WATCHHAMSTER_ERROR] == WebhookEndpoint.WATCHHAMSTER
        
        # 3. 메시지 생성 테스트
        print("✅ 웹훅 메시지 생성 테스트")
        message = webhook_sender._create_webhook_message(
            bot_type=BotType.TEST,
            priority=MessagePriority.LOW,
            bot_name="Test Bot",
            title="Test Title",
            content="Test Content",
            color="#28a745",
            test_mode=True
        )
        
        assert message.bot_type == BotType.TEST
        assert message.priority == MessagePriority.LOW
        assert message.test_mode == True
        
        # 4. 메시지 해시 생성 테스트
        print("✅ 메시지 해시 생성 테스트")
        hash1 = webhook_sender._generate_message_hash(message)
        hash2 = webhook_sender._generate_message_hash(message)
        assert hash1 == hash2
        
        # 5. 큐 상태 조회 테스트
        print("✅ 큐 상태 조회 테스트")
        status = webhook_sender.get_queue_status()
        assert 'queue_size' in status
        assert 'is_running' in status
        assert status['is_running'] == True
        
        # 6. 전송 통계 테스트
        print("✅ 전송 통계 테스트")
        statistics = webhook_sender.get_send_statistics()
        assert 'total_sent' in statistics
        assert 'success_rate' in statistics
        
        # 7. 테스트 메시지 전송 (실제 전송 없이 큐 추가만)
        print("✅ 테스트 메시지 큐 추가 테스트")
        message_id = webhook_sender.send_test_message("기본 기능 테스트")
        assert message_id is not None
        
        # 잠시 대기
        time.sleep(1)
        
        print("🎉 모든 기본 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False
        
    finally:
        # 정리
        webhook_sender.shutdown()
        print("🔧 웹훅 전송자 종료 완료")


def test_message_priority():
    """메시지 우선순위 테스트"""
    print("\n🧪 메시지 우선순위 테스트 시작")
    
    webhook_sender = WebhookSender(test_mode=True)
    
    try:
        # 다양한 우선순위의 메시지 생성
        critical_msg = webhook_sender._create_webhook_message(
            BotType.WATCHHAMSTER_ERROR, MessagePriority.CRITICAL,
            "Critical Bot", "Critical", "Critical message", "#dc3545"
        )
        
        normal_msg = webhook_sender._create_webhook_message(
            BotType.NEWS_STATUS, MessagePriority.NORMAL,
            "Normal Bot", "Normal", "Normal message", "#28a745"
        )
        
        low_msg = webhook_sender._create_webhook_message(
            BotType.TEST, MessagePriority.LOW,
            "Low Bot", "Low", "Low message", "#6c757d"
        )
        
        # 우선순위 비교 테스트
        assert critical_msg < normal_msg
        assert normal_msg < low_msg
        assert critical_msg < low_msg
        
        print("✅ 메시지 우선순위 정렬 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 우선순위 테스트 실패: {e}")
        return False
        
    finally:
        webhook_sender.shutdown()


def test_bot_type_routing():
    """BOT 타입별 라우팅 테스트"""
    print("\n🧪 BOT 타입별 라우팅 테스트 시작")
    
    webhook_sender = WebhookSender(test_mode=True)
    
    try:
        # 뉴스 관련 BOT들은 NEWS_MAIN으로 라우팅
        news_bots = [
            BotType.NEWS_COMPARISON,
            BotType.NEWS_DELAY,
            BotType.NEWS_REPORT,
            BotType.NEWS_STATUS,
            BotType.NEWS_NO_DATA
        ]
        
        for bot_type in news_bots:
            assert webhook_sender.bot_routing[bot_type] == WebhookEndpoint.NEWS_MAIN
        
        # 워치햄스터 관련 BOT들은 WATCHHAMSTER로 라우팅
        watchhamster_bots = [
            BotType.WATCHHAMSTER_ERROR,
            BotType.WATCHHAMSTER_STATUS
        ]
        
        for bot_type in watchhamster_bots:
            assert webhook_sender.bot_routing[bot_type] == WebhookEndpoint.WATCHHAMSTER
        
        # 테스트 BOT은 TEST로 라우팅
        assert webhook_sender.bot_routing[BotType.TEST] == WebhookEndpoint.TEST
        
        print("✅ BOT 타입별 라우팅 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 라우팅 테스트 실패: {e}")
        return False
        
    finally:
        webhook_sender.shutdown()


def test_duplicate_prevention():
    """중복 메시지 방지 테스트"""
    print("\n🧪 중복 메시지 방지 테스트 시작")
    
    webhook_sender = WebhookSender(test_mode=True)
    
    try:
        # 동일한 메시지 두 번 전송 시도
        message_id1 = webhook_sender.send_test_message("중복 테스트 메시지")
        message_id2 = webhook_sender.send_test_message("중복 테스트 메시지")
        
        # 첫 번째는 성공, 두 번째는 중복으로 인해 None
        assert message_id1 is not None
        assert message_id2 is None
        
        print("✅ 중복 메시지 방지 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 중복 방지 테스트 실패: {e}")
        return False
        
    finally:
        webhook_sender.shutdown()


def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 웹훅 전송 시스템 종합 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("기본 기능", test_webhook_sender_basic),
        ("메시지 우선순위", test_message_priority),
        ("BOT 타입 라우팅", test_bot_type_routing),
        ("중복 메시지 방지", test_duplicate_prevention)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과")
            else:
                failed += 1
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            failed += 1
            print(f"🚨 {test_name} 테스트 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 웹훅 전송 시스템 테스트 완료")
    print(f"✅ 통과: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"📊 성공률: {passed/(passed+failed)*100:.1f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)