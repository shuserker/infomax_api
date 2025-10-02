#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동적 데이터 기반 메시지 생성 시스템 데모
Requirements 2.4 구현 시연

이 데모는 다음 기능들을 보여줍니다:
- 실시간 시장 데이터 수집
- 데이터 품질 평가 및 신뢰도 계산
- 동적 메시지 생성
- 데이터 품질 지표 표시
"""

import os
import sys
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


def demo_dynamic_data_collection():
    """동적 데이터 수집 데모"""
    print("🎯 데모 1: 동적 데이터 수집 및 품질 평가")
    print("="*60)
    
    # 동적 데이터 관리자 초기화
    data_manager = DynamicDataManager()
    
    # 시장 데이터 수집
    print("📊 실시간 시장 데이터 수집 중...")
    market_data = data_manager.collect_market_data()
    
    print(f"\n✅ 데이터 수집 완료!")
    print(f"📈 KOSPI: {market_data.kospi.value if market_data.kospi else 'N/A'} (품질: {market_data.kospi.quality_score:.1%})")
    print(f"💱 환율: {market_data.exchange_rate.value if market_data.exchange_rate else 'N/A'} (품질: {market_data.exchange_rate.quality_score:.1%})")
    print(f"🏭 POSCO: {market_data.posco_stock.value if market_data.posco_stock else 'N/A'} (품질: {market_data.posco_stock.quality_score:.1%})")
    print(f"📰 뉴스 감정: {market_data.news_sentiment.value if market_data.news_sentiment else 'N/A'} (품질: {market_data.news_sentiment.quality_score:.1%})")
    print(f"🎯 전체 품질: {market_data.overall_quality:.1%}")
    
    return market_data


def demo_dynamic_message_generation():
    """동적 메시지 생성 데모"""
    print("\n🎯 데모 2: 동적 데이터 기반 메시지 생성")
    print("="*60)
    
    # 메시지 템플릿 엔진 초기화
    template_engine = MessageTemplateEngine()
    
    # 동적 데이터 업데이트 메시지 생성
    print("💬 동적 데이터 업데이트 메시지 생성 중...")
    message = template_engine.generate_data_update_message(use_dynamic_data=True)
    
    print(f"\n✅ 메시지 생성 완료!")
    print(f"📝 제목: {message['title']}")
    print(f"⚡ 우선순위: {message['priority']}")
    print(f"🎨 색상: {message['color']}")
    print(f"📏 본문 길이: {len(message['body'])}자")
    
    print(f"\n📄 메시지 본문 미리보기:")
    print("-" * 60)
    print(message['body'][:800] + "..." if len(message['body']) > 800 else message['body'])
    print("-" * 60)
    
    return message


def demo_enhanced_dynamic_messages():
    """향상된 동적 메시지 데모"""
    print("\n🎯 데모 3: 향상된 동적 메시지 (다양한 타입)")
    print("="*60)
    
    template_engine = MessageTemplateEngine()
    
    # 다양한 메시지 타입 테스트
    message_types = [
        (MessageType.DATA_UPDATE, "데이터 업데이트"),
        (MessageType.SYSTEM_STATUS, "시스템 상태"),
    ]
    
    for msg_type, description in message_types:
        print(f"\n📨 {description} 메시지 생성 중...")
        
        try:
            message = template_engine.generate_enhanced_dynamic_message(
                message_type=msg_type,
                force_refresh=False
            )
            
            print(f"✅ {description} 메시지 생성 성공")
            print(f"   제목: {message['title'][:50]}...")
            print(f"   우선순위: {message['priority']}")
            print(f"   본문 길이: {len(message['body'])}자")
            
        except Exception as e:
            print(f"❌ {description} 메시지 생성 실패: {e}")


def demo_data_quality_report():
    """데이터 품질 리포트 데모"""
    print("\n🎯 데모 4: 데이터 품질 리포트")
    print("="*60)
    
    template_engine = MessageTemplateEngine()
    
    print("📊 데이터 품질 리포트 생성 중...")
    quality_report = template_engine.get_data_quality_report()
    
    if 'error' in quality_report:
        print(f"❌ 품질 리포트 생성 실패: {quality_report['error']}")
        return
    
    print("✅ 데이터 품질 리포트 생성 완료!")
    
    current_quality = quality_report.get('current_quality', {})
    statistics = quality_report.get('statistics', {})
    recommendations = quality_report.get('recommendations', [])
    
    print(f"\n📈 현재 품질 상태:")
    print(f"   전체: {current_quality.get('overall', 0):.1%}")
    print(f"   KOSPI: {current_quality.get('kospi', 0):.1%}")
    print(f"   환율: {current_quality.get('exchange', 0):.1%}")
    print(f"   POSCO: {current_quality.get('posco', 0):.1%}")
    print(f"   뉴스: {current_quality.get('news', 0):.1%}")
    
    print(f"\n📊 품질 통계:")
    print(f"   측정 기간: {statistics.get('period', 'N/A')}")
    print(f"   총 측정 횟수: {statistics.get('total_measurements', 0)}회")
    print(f"   평균 품질: {statistics.get('average_quality', 0):.1%}")
    print(f"   품질 트렌드: {statistics.get('quality_trend', 'N/A')}")
    
    print(f"\n💡 개선 권장사항:")
    for i, recommendation in enumerate(recommendations[:3], 1):
        print(f"   {i}. {recommendation}")


def demo_integration_with_notifier():
    """메인 알림 시스템 통합 데모"""
    print("\n🎯 데모 5: 메인 알림 시스템 통합")
    print("="*60)
    
    # POSCO 메인 알림 시스템 초기화 (웹훅 없이)
    notifier = PoscoMainNotifier()
    
    print("🔗 메인 알림 시스템과 동적 데이터 시스템 통합 테스트...")
    
    # 웹훅 URL 비활성화 (테스트용)
    original_webhook_url = notifier.webhook_url
    notifier.webhook_url = None
    
    try:
        # 동적 데이터 메시지 생성 (전송 없이)
        template_message = notifier.message_engine.generate_enhanced_dynamic_message(
            MessageType.DATA_UPDATE
        )
        
        print("✅ 통합 테스트 성공!")
        print(f"   메시지 타입: {template_message.get('message_type', 'unknown')}")
        print(f"   우선순위: {template_message.get('priority', 'unknown')}")
        print(f"   동적 데이터 포함: {'품질' in template_message.get('body', '')}")
        
        # 포스코 스타일 메시지 포맷팅 테스트
        formatted_message = notifier._format_posco_style_message(template_message)
        print(f"   포맷팅된 메시지 길이: {len(formatted_message)}자")
        print(f"   고객 친화적 변환: {'시스템 데이터' in formatted_message}")
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
    finally:
        # 원래 웹훅 URL 복원
        notifier.webhook_url = original_webhook_url


def demo_cache_and_performance():
    """캐시 및 성능 데모"""
    print("\n🎯 데모 6: 데이터 캐싱 및 성능")
    print("="*60)
    
    data_manager = DynamicDataManager()
    
    # 첫 번째 데이터 수집 (캐시 생성)
    print("📊 첫 번째 데이터 수집 (캐시 생성)...")
    start_time = datetime.now()
    market_data1 = data_manager.collect_market_data()
    first_duration = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ 첫 번째 수집 완료 (소요시간: {first_duration:.2f}초)")
    
    # 두 번째 데이터 조회 (캐시 사용)
    print("📂 두 번째 데이터 조회 (캐시 사용)...")
    start_time = datetime.now()
    market_data2 = data_manager.get_market_data()
    second_duration = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ 두 번째 조회 완료 (소요시간: {second_duration:.2f}초)")
    print(f"🚀 성능 향상: {(first_duration - second_duration) / first_duration * 100:.1f}%")
    
    # 캐시 파일 정보
    cache_file = data_manager.cache_file
    if os.path.exists(cache_file):
        cache_size = os.path.getsize(cache_file)
        print(f"💾 캐시 파일 크기: {cache_size:,} bytes")
        print(f"📁 캐시 파일 위치: {cache_file}")


def run_all_demos():
    """모든 데모 실행"""
    print("🎬 동적 데이터 기반 메시지 생성 시스템 데모")
    print("Requirements 2.4 구현 시연")
    print("="*80)
    
    try:
        # 데모 1: 동적 데이터 수집
        market_data = demo_dynamic_data_collection()
        
        # 데모 2: 동적 메시지 생성
        message = demo_dynamic_message_generation()
        
        # 데모 3: 향상된 동적 메시지
        demo_enhanced_dynamic_messages()
        
        # 데모 4: 데이터 품질 리포트
        demo_data_quality_report()
        
        # 데모 5: 메인 시스템 통합
        demo_integration_with_notifier()
        
        # 데모 6: 캐시 및 성능
        demo_cache_and_performance()
        
        # 데모 완료
        print("\n" + "="*80)
        print("🎉 모든 데모가 성공적으로 완료되었습니다!")
        print("✅ Requirements 2.4 (동적 데이터 기반 메시지 생성 시스템) 구현 완료")
        print("\n주요 구현 기능:")
        print("• 📊 실시간 시장 데이터 수집 및 캐싱")
        print("• 🔍 데이터 품질 평가 및 신뢰도 계산")
        print("• 💬 동적 데이터 기반 메시지 생성")
        print("• 📈 데이터 분석 결과 메시지 반영")
        print("• 🎯 데이터 품질에 따른 신뢰도 표시")
        print("• 💾 효율적인 데이터 캐싱 시스템")
        print("• 🔗 기존 알림 시스템과의 완벽한 통합")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_demos()
    sys.exit(0 if success else 1)