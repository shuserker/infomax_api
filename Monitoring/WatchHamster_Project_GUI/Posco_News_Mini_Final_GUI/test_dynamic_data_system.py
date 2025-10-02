#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동적 데이터 기반 메시지 생성 시스템 테스트
Requirements 2.4 구현 검증

테스트 항목:
- 동적 데이터 수집 및 캐싱
- 데이터 품질 평가
- 동적 메시지 생성
- 신뢰도 지표 표시
"""

import os
import sys
import json
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from dynamic_data_manager import DynamicDataManager
    from message_template_engine import MessageTemplateEngine, MessageType
    from posco_main_notifier import PoscoMainNotifier
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_dynamic_data_collection():
    """동적 데이터 수집 테스트"""
    print("\n" + "="*60)
    print("🧪 동적 데이터 수집 테스트")
    print("="*60)
    
    try:
        # 동적 데이터 관리자 초기화
        data_manager = DynamicDataManager()
        
        # 시장 데이터 수집
        print("📊 시장 데이터 수집 중...")
        market_data = data_manager.collect_market_data()
        
        # 결과 검증
        assert market_data is not None, "시장 데이터가 None입니다"
        assert market_data.overall_quality is not None, "전체 품질 점수가 없습니다"
        assert 0 <= market_data.overall_quality <= 1, "품질 점수가 범위를 벗어났습니다"
        
        print(f"✅ 시장 데이터 수집 성공")
        print(f"   - KOSPI: {market_data.kospi.value if market_data.kospi else 'N/A'}")
        print(f"   - 환율: {market_data.exchange_rate.value if market_data.exchange_rate else 'N/A'}")
        print(f"   - POSCO 주가: {market_data.posco_stock.value if market_data.posco_stock else 'N/A'}")
        print(f"   - 전체 품질: {market_data.overall_quality:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ 동적 데이터 수집 테스트 실패: {e}")
        return False


def test_data_quality_assessment():
    """데이터 품질 평가 테스트"""
    print("\n" + "="*60)
    print("🔍 데이터 품질 평가 테스트")
    print("="*60)
    
    try:
        data_manager = DynamicDataManager()
        
        # 시장 데이터 수집
        market_data = data_manager.collect_market_data()
        
        # 품질 평가 검증
        print("📊 개별 데이터 품질 평가:")
        
        if market_data.kospi:
            print(f"   - KOSPI 품질: {market_data.kospi.quality_score:.1%} (신뢰도: {market_data.kospi.confidence:.1%})")
            assert 0 <= market_data.kospi.quality_score <= 1, "KOSPI 품질 점수 범위 오류"
            assert 0 <= market_data.kospi.confidence <= 1, "KOSPI 신뢰도 범위 오류"
        
        if market_data.exchange_rate:
            print(f"   - 환율 품질: {market_data.exchange_rate.quality_score:.1%} (신뢰도: {market_data.exchange_rate.confidence:.1%})")
            assert 0 <= market_data.exchange_rate.quality_score <= 1, "환율 품질 점수 범위 오류"
        
        if market_data.posco_stock:
            print(f"   - POSCO 품질: {market_data.posco_stock.quality_score:.1%} (신뢰도: {market_data.posco_stock.confidence:.1%})")
            assert 0 <= market_data.posco_stock.quality_score <= 1, "POSCO 품질 점수 범위 오류"
        
        # 품질 통계 테스트
        quality_stats = data_manager.get_quality_statistics()
        print(f"📈 품질 통계: {quality_stats}")
        
        print("✅ 데이터 품질 평가 테스트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 품질 평가 테스트 실패: {e}")
        return False


def test_dynamic_message_generation():
    """동적 메시지 생성 테스트"""
    print("\n" + "="*60)
    print("💬 동적 메시지 생성 테스트")
    print("="*60)
    
    try:
        # 메시지 템플릿 엔진 초기화
        template_engine = MessageTemplateEngine()
        
        # 동적 데이터 업데이트 메시지 생성
        print("📊 동적 데이터 업데이트 메시지 생성...")
        data_update_msg = template_engine.generate_data_update_message(use_dynamic_data=True)
        
        # 메시지 검증
        assert data_update_msg is not None, "데이터 업데이트 메시지가 None입니다"
        assert 'title' in data_update_msg, "메시지에 제목이 없습니다"
        assert 'body' in data_update_msg, "메시지에 본문이 없습니다"
        assert 'priority' in data_update_msg, "메시지에 우선순위가 없습니다"
        
        print("✅ 동적 데이터 업데이트 메시지 생성 성공")
        print(f"   제목: {data_update_msg['title']}")
        print(f"   우선순위: {data_update_msg['priority']}")
        print(f"   본문 길이: {len(data_update_msg['body'])}자")
        
        # 향상된 동적 메시지 생성 테스트
        print("\n🚀 향상된 동적 메시지 생성...")
        enhanced_msg = template_engine.generate_enhanced_dynamic_message(
            MessageType.DATA_UPDATE,
            force_refresh=True
        )
        
        assert enhanced_msg is not None, "향상된 동적 메시지가 None입니다"
        print("✅ 향상된 동적 메시지 생성 성공")
        
        # 메시지 미리보기
        print("\n👀 메시지 미리보기:")
        print("-" * 40)
        print(enhanced_msg['body'][:500] + "..." if len(enhanced_msg['body']) > 500 else enhanced_msg['body'])
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ 동적 메시지 생성 테스트 실패: {e}")
        return False


def test_data_caching():
    """데이터 캐싱 테스트"""
    print("\n" + "="*60)
    print("💾 데이터 캐싱 테스트")
    print("="*60)
    
    try:
        data_manager = DynamicDataManager()
        
        # 첫 번째 데이터 수집 (캐시 생성)
        print("📊 첫 번째 데이터 수집 (캐시 생성)...")
        market_data1 = data_manager.collect_market_data()
        
        # 캐시된 데이터 로드
        print("📂 캐시된 데이터 로드...")
        cached_data = data_manager.load_cached_data()
        
        # 캐시 검증
        assert cached_data is not None, "캐시된 데이터가 None입니다"
        assert cached_data.overall_quality == market_data1.overall_quality, "캐시된 품질 점수가 다릅니다"
        
        print("✅ 데이터 캐싱 테스트 성공")
        print(f"   캐시된 데이터 품질: {cached_data.overall_quality:.1%}")
        print(f"   마지막 업데이트: {cached_data.last_updated}")
        
        # 캐시 파일 존재 확인
        cache_file = os.path.join(data_manager.data_dir, "market_data_cache.json")
        assert os.path.exists(cache_file), "캐시 파일이 생성되지 않았습니다"
        
        print(f"   캐시 파일: {cache_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 캐싱 테스트 실패: {e}")
        return False


def test_quality_indicators():
    """품질 지표 테스트"""
    print("\n" + "="*60)
    print("📈 품질 지표 테스트")
    print("="*60)
    
    try:
        data_manager = DynamicDataManager()
        template_engine = MessageTemplateEngine()
        
        # 시장 데이터 수집
        market_data = data_manager.collect_market_data()
        
        # 동적 메시지 데이터 생성
        message_data = data_manager.generate_dynamic_message_data(market_data)
        
        # 품질 지표 검증
        required_indicators = [
            'data_reliability', 'quality_warning', 'data_freshness', 
            'reliability_indicator', 'market_summary'
        ]
        
        for indicator in required_indicators:
            assert indicator in message_data, f"품질 지표 '{indicator}'가 없습니다"
            print(f"   ✓ {indicator}: {message_data[indicator]}")
        
        # 데이터 품질 리포트 테스트
        print("\n📊 데이터 품질 리포트 생성...")
        quality_report = template_engine.get_data_quality_report()
        
        assert 'current_quality' in quality_report, "현재 품질 정보가 없습니다"
        assert 'recommendations' in quality_report, "권장사항이 없습니다"
        
        print("✅ 품질 지표 테스트 성공")
        print(f"   권장사항 수: {len(quality_report['recommendations'])}개")
        
        return True
        
    except Exception as e:
        print(f"❌ 품질 지표 테스트 실패: {e}")
        return False


def test_integration_with_notifier():
    """메인 알림 시스템 통합 테스트"""
    print("\n" + "="*60)
    print("🔗 메인 알림 시스템 통합 테스트")
    print("="*60)
    
    try:
        # POSCO 메인 알림 시스템 초기화 (웹훅 없이)
        notifier = PoscoMainNotifier()
        
        # 동적 데이터 메시지 생성 테스트 (전송 없이)
        print("💬 동적 데이터 메시지 생성 테스트...")
        
        # 웹훅 URL이 없어도 메시지 생성은 가능해야 함
        original_webhook_url = notifier.webhook_url
        notifier.webhook_url = None  # 웹훅 비활성화
        
        # 동적 메시지 생성만 테스트
        template_message = notifier.message_engine.generate_enhanced_dynamic_message(
            MessageType.DATA_UPDATE
        )
        
        assert template_message is not None, "통합 동적 메시지가 None입니다"
        assert 'title' in template_message, "통합 메시지에 제목이 없습니다"
        assert 'body' in template_message, "통합 메시지에 본문이 없습니다"
        
        print("✅ 메인 알림 시스템 통합 테스트 성공")
        print(f"   메시지 타입: {template_message.get('message_type', 'unknown')}")
        print(f"   우선순위: {template_message.get('priority', 'unknown')}")
        
        # 원래 웹훅 URL 복원
        notifier.webhook_url = original_webhook_url
        
        return True
        
    except Exception as e:
        print(f"❌ 메인 알림 시스템 통합 테스트 실패: {e}")
        return False


def test_data_folder_structure():
    """데이터 폴더 구조 테스트"""
    print("\n" + "="*60)
    print("📁 데이터 폴더 구조 테스트")
    print("="*60)
    
    try:
        data_manager = DynamicDataManager()
        
        # 데이터 디렉토리 존재 확인
        assert os.path.exists(data_manager.data_dir), "데이터 디렉토리가 없습니다"
        print(f"✓ 데이터 디렉토리: {data_manager.data_dir}")
        
        # 데이터 수집 후 파일 생성 확인
        market_data = data_manager.collect_market_data()
        
        # 캐시 파일 확인
        cache_file = data_manager.cache_file
        assert os.path.exists(cache_file), "캐시 파일이 생성되지 않았습니다"
        print(f"✓ 캐시 파일: {cache_file}")
        
        # 품질 로그 파일 확인
        quality_log_file = data_manager.quality_log_file
        assert os.path.exists(quality_log_file), "품질 로그 파일이 생성되지 않았습니다"
        print(f"✓ 품질 로그 파일: {quality_log_file}")
        
        # 파일 내용 검증
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            assert 'market_data' in cache_data, "캐시 파일 구조가 잘못되었습니다"
            assert 'cached_at' in cache_data, "캐시 시간 정보가 없습니다"
        
        with open(quality_log_file, 'r', encoding='utf-8') as f:
            quality_log = json.load(f)
            assert isinstance(quality_log, list), "품질 로그가 리스트가 아닙니다"
            assert len(quality_log) > 0, "품질 로그가 비어있습니다"
        
        print("✅ 데이터 폴더 구조 테스트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 폴더 구조 테스트 실패: {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("🧪 동적 데이터 기반 메시지 생성 시스템 테스트 시작")
    print("Requirements 2.4 구현 검증")
    print("="*80)
    
    tests = [
        ("데이터 폴더 구조", test_data_folder_structure),
        ("동적 데이터 수집", test_dynamic_data_collection),
        ("데이터 품질 평가", test_data_quality_assessment),
        ("데이터 캐싱", test_data_caching),
        ("동적 메시지 생성", test_dynamic_message_generation),
        ("품질 지표", test_quality_indicators),
        ("메인 시스템 통합", test_integration_with_notifier)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "="*80)
    print("📊 테스트 결과 요약")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")
    print(f"성공률: {passed/len(results)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("✅ Requirements 2.4 (동적 데이터 기반 메시지 생성 시스템) 구현 완료")
    else:
        print(f"\n⚠️ {failed}개의 테스트가 실패했습니다.")
        print("❌ 일부 기능에 문제가 있을 수 있습니다.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)